"""Export an inspectable AND/OR control decoder from the selected v018 model.

This is the base decoder, including reset/interrupt cycles and named research
controls. Conditional branch writes, waits, SSE and asynchronous latches
still belong to a separate controller. No FPGA technology is assumed.
"""
from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path

from cmc8.versions.v018.sequences import (ALU_A_MODES, CONTROL_STROBES, FLAG_INSTRUCTIONS,
                                         INTERRUPT_ENTRY, LRS, RESET_CYCLE, SEQUENCES,
                                         ZERO_SOURCES, decode)

ROOT = Path(__file__).resolve().parents[1]
INPUT_BITS = 15
FULL_MASK = (1 << INPUT_BITS)-1
OUTPUTS = [f'MOP{i}' for i in range(1,58)] + [
    'STRCS', 'ZERO_DI', 'ALU_A_CAPTURE', 'ALU_A_HELD', 'CLEAR_INTA', 'DEFINED']


def reference_word(key):
    mode, ir, phase, timing = key >> 13, (key >> 5) & 255, (key >> 3) & 3, key & 7
    name = None
    if mode in (1,2):
        if phase != 0:
            return 0
        mops = (INTERRUPT_ENTRY if mode == 1 else RESET_CYCLE)[timing]
    elif mode == 0:
        if phase == 0 and timing < 6:
            mops = LRS[0][timing]
            flag = FLAG_INSTRUCTIONS.get(ir)
            if timing == 2 and flag is not None:
                mops = (*mops,flag.mop)
        else:
            try:
                name = decode(ir)
            except ValueError:
                return 0
            if phase >= len(SEQUENCES[name]):
                return 0
            mops = SEQUENCES[name][phase][timing]
        if phase == 0 and timing == 0:
            mops = (*mops,28)
        if timing == 4:
            external = any(m in mops for m in (24,25,26)) and 23 not in mops
            data_capture = phase == 0 or 2 in SEQUENCES[name][phase][5]
            control_byte = name in {'SCS','SCW'} and phase == 1
            if external and (data_capture or control_byte):
                mops = (*mops,29)  # Selected H022 read-check overlay.
    else:
        return 0
    if timing == 7:
        mops = (*mops,47)
    word = 1 << OUTPUTS.index('DEFINED')
    for mop in mops:
        word |= 1 << (mop-1)
    named = {'CLEAR_INTA':mode == 2 and timing == 0,
             'STRCS':(name,phase,timing) in CONTROL_STROBES,
             'ZERO_DI':ZERO_SOURCES.get((name,phase,timing)) == 'di',
             'ALU_A_CAPTURE':ALU_A_MODES.get((name,phase,timing)) == 'capture',
             'ALU_A_HELD':ALU_A_MODES.get((name,phase,timing)) == 'held'}
    for output, active in named.items():
        if active:
            word |= 1 << OUTPUTS.index(output)
    return word


def implicants(ones):
    """Exact Boolean merging; no undefined input combinations are don't-cares."""
    current = {(FULL_MASK,key) for key in ones}
    primes = set()
    while current:
        combined, following = set(), set()
        for mask,value in current:
            for bit in range(INPUT_BITS):
                flag = 1 << bit
                if mask & flag and not value & flag and (mask,value|flag) in current:
                    combined.update(((mask,value),(mask,value|flag)))
                    following.add((mask^flag,value))
        primes.update(current-combined)
        current = following
    return primes


@lru_cache(maxsize=None)
def expansion(mask,value):
    keys = [value]
    for bit in range(INPUT_BITS):
        flag = 1 << bit
        if not mask & flag:
            keys += [key|flag for key in keys]
    return frozenset(keys)


def cover(ones):
    """Greedy cover of exact implicants; useful compression, not a minimum proof."""
    remaining, candidates, chosen = set(ones), implicants(ones), []
    while remaining:
        best = max(candidates,key=lambda c:(len(expansion(*c)&remaining),
                                           -c[0].bit_count(),-c[0],-c[1]))
        chosen.append(best)
        remaining.difference_update(expansion(*best))
        candidates.remove(best)
    return chosen


def build_terms(truth):
    shared = defaultdict(int)
    for bit in range(len(OUTPUTS)):
        ones = {key for key,word in enumerate(truth) if word & (1 << bit)}
        for mask,value in cover(ones):
            shared[mask,value] |= 1 << bit
    return [{'mask':mask,'value':value,'outputs':outputs}
            for (mask,value),outputs in sorted(shared.items())]


def evaluate_terms(key,terms):
    word = 0
    for term in terms:
        if key & term['mask'] == term['value']:
            word |= term['outputs']
    return word


def write_hdl(terms):
    declarations = '''// Generated base decoder study, not a complete CMC8 controller.
// key = {mode[1:0], IR[7:0], phase[1:0], timing[2:0]}.
// mode: 0 normal, 1 interrupt entry, 2 reset, 3 reserved.
// outputs bits0..56=MOP1..57, 57=STRCS, 58=ZERO_DI,
// 59=ALU_A_CAPTURE, 60=ALU_A_HELD, 61=CLEAR_INTA, 62=DEFINED.
module cmc8_control_pla(input wire [14:0] key, output reg [62:0] control);
  always @* begin
    control = 63'd0;
'''
    lines = [declarations]
    for t in terms:
        lines.append(f"    if ((key & 15'h{t['mask']:04x}) == 15'h{t['value']:04x}) "
                     f"control = control | 63'h{t['outputs']:016x};")
    lines += ['  end','endmodule','']
    (ROOT/'rtl/study/cmc8_control_pla.v').write_text('\n'.join(lines))
    vhdl = ['-- Generated base decoder study; bit allocation matches the Verilog header.',
            'library ieee;','use ieee.std_logic_1164.all;',
            'entity cmc8_control_pla is',
            '  port (key : in std_logic_vector(14 downto 0);',
            '        control : out std_logic_vector(62 downto 0));','end entity;',
            'architecture rtl of cmc8_control_pla is','begin','  process(all)',
            '    variable result : std_logic_vector(62 downto 0);','  begin',
            "    result := (others => '0');"]
    for t in terms:
        vhdl += [f'    if (key and "{t["mask"]:015b}") = "{t["value"]:015b}" then',
                 f'      result := result or "{t["outputs"]:063b}";','    end if;']
    vhdl += ['    control <= result;','  end process;','end architecture;','']
    (ROOT/'rtl/study/cmc8_control_pla.vhd').write_text('\n'.join(vhdl))


def main():
    truth = [reference_word(key) for key in range(1 << INPUT_BITS)]
    terms = build_terms(truth)
    for key,expected in enumerate(truth):
        actual = evaluate_terms(key,terms)
        if actual != expected:
            raise AssertionError(f'PLA mismatch at key {key:04X}: {actual:X} != {expected:X}')
    report = {'model':'v018','scope':'Base combinational decoder only; dynamic controller excluded',
              'input_order':['mode:2','IR:8','phase:2','timing:3'],
              'output_bits':OUTPUTS,'input_combinations':len(truth),
              'defined_combinations':sum(bool(w >> 62) for w in truth),
              'product_terms':len(terms),'literal_connections':sum(t['mask'].bit_count() for t in terms),
              'or_connections':sum(t['outputs'].bit_count() for t in terms),
              'dense_table_bits':len(truth)*len(OUTPUTS),
              'compression':'Exact per-output implicants, greedy covers, identical products shared; not globally minimal.',
              'hdl_status':'Generated; no HDL compiler/synthesis tool present in the workspace environment.',
              'terms':terms}
    (ROOT/'specification/control-pla.json').write_text(json.dumps(report,indent=2)+'\n')
    write_hdl(terms)
    print(f"Base decoder: {len(terms)} shared product terms; all {len(truth)} binary inputs agree.")
    print(f"Defined combinations: {report['defined_combinations']}; "
          f"AND literals: {report['literal_connections']}; OR connections: {report['or_connections']}.")


if __name__ == '__main__':
    main()
