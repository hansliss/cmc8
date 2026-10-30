#!/usr/bin/env python3
"""Build the compact study reference from the immutable v018 model.

Run from any directory. --check verifies committed Markdown without writing it.
The architecture SVG is authored separately, not inferred from these tables.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cmc8.versions.v018.mops import MOPS
from cmc8.versions.v018.sequences import (
    SEQUENCES, FLAG_INSTRUCTIONS, BRANCHES, PAGE_BRANCHES,
    ALU_A_MODES, ZERO_SOURCES, INTERRUPT_ENTRY, RESET_CYCLE,
)

# Keep the printed shorthand consistent with the portable Midahs reference card.
spec = importlib.util.spec_from_file_location('card', ROOT / 'x7_midahs/tools/export_reference.py')
card = importlib.util.module_from_spec(spec)
spec.loader.exec_module(card)

SHORT = {
    1:'DB→IR', 2:'DB→BR', 3:'BR→B', 4:'BR→DI', 5:'~BR→DI', 6:'BR→AB',
    7:'DI→A', 8:'A XOR B', 9:'A AND B', 10:'A+1', 11:'SHR', 12:'MUX→BR',
    13:'A0→MUX7', 14:'DI→AB', 15:'IR[1:0]→PG', 16:'N+1', 17:'N−1',
    18:'select PC', 19:'select Rr', 20:'select X', 21:'R→DI', 22:'DI→R',
    23:'DI→DB', 24:'PME', 25:'SME', 26:'EDE', 27:'WRITE', 28:'INTR→INTA',
    29:'MEMR?', 30:'0→F', 31:'2→F', 32:'Z←zero', 33:'L↔shift',
    34:'1→L', 35:'0→L', 36:'1→Z', 37:'0→Z', 38:'1→INTE', 39:'0→INTE',
    40:'0→DI', 41:'2→DI', 42:'0→PG', 43:'0→MUX7', 44:'0→PC',
    45:'0→N', 46:'0→INTR', 47:'RESET?', 48:'0→SSE', 49:'1→SSE',
    50:'SCWR?', 51:'Z→cond', 52:'L→cond', 53:'TEST→cond',
    54:'DI0→cond', 55:'cond XOR IR3→H', 57:'0→MUX7',
}
EXPLANATIONS = {
    12:'Capture the ALU result after the shift/insert MUX in BR.',
    13:'Wrap ALU result bit 0 into MUX bit 7 (ROR).',
    18:'Select R(N), the current program counter.',
    19:'Select the register addressed by IR[2:0].',
    20:'Select R7, also called X.',
    28:'At F0T0 clock pending INTR into INTA; raw /INT sets INTR separately when enabled.',
    29:'At T4 test memory wait; shared fetch continuation also observes HALT/single-step.',
    32:'Set Z when the ALU result is zero; DCR instead uses the final DI value (H014).',
    33:'Insert old L into MUX bit 7 and capture ALU bit 0 as new L (RRL).',
    44:'Clear the selected current PC register; reset sequence instead uses 40/18/22.',
    47:'Sample active-low RESET at T7; select a separate reset cycle.',
    48:'Clear single-step enable after accepting a step (selected H023 timing).',
    49:'Rearm single-step enable after SS release (selected H023 timing).',
    50:'Sample /SCWR at T4; high repeats the control-word wait cycle.',
    53:'Select TEST[IR[1:0]] and present it through T to the condition circuit.',
    55:'At T2 latch condition XOR IR bit 3. H=0 permits the branch write at T6.',
    57:'Figure 5.11 label for zero insertion; functional alias of 43 in this model.',
}
NAV = '[Study guide](README.md) · [Instructions](instructions.md) · [MOPs](mops.md) · [Timing](timing.md) · [Datapath](processor.svg)\n\n'


def mop(number, fetch=False):
    text = f'{number} {SHORT[number]}'
    return f'*{text}*' if fetch else text


def build():
    entries = json.loads((ROOT/'specification/instructions.json').read_text())['instructions']
    index = {entry['mnemonic']:entry for entry in entries}
    outputs = {}
    lines = ['# CMC8 compact instruction list\n', NAV,
             'All 43 families / 239 valid encodings. Encoding bits are binary; opcode bases are octal. '
             '`r` selects R0–R7, `p` selects page 0–3, `t` selects TEST0–3. '
             '`A` is an 8-bit address byte, `P` a port byte, `I` an immediate byte; X = R7. '
             'PC = R(N). PM and SM use the current PG, except explicit page-changing jumps/branches. '
             'Flags lists only flags changed. Cycles include fetch, exclude waits.\n',
             '| Form | Bits | Octal base | Bytes | Cycles | Flags | Meaning |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for e in entries:
        name=e['mnemonic']
        variable='r' if 'RRR' in e['pattern'] else 'p' if 'PP' in e['pattern'] else 't' if 'TT' in e['pattern'] else ''
        opcode=f'{e["value"]:03o}'+('+'+variable if variable else '')
        lines.append(f'| [{card.form(e)}](timing.md#{name.lower()}) | `{e["pattern"].lower()}` | {opcode} | {e["length_bytes"]} | {e["base_cycles"]} | {", ".join(e["flags"]) or "—"} | {card.DESCRIPTIONS[name]} |')
    lines += ['\nRRL rotates right through L; ROR wraps bit 0 into bit 7; SHR inserts zero. '
              'Conditional branches replace PC only when their condition is satisfied. '
              'BL/BZ taken branches also install page p; BT/BB retain PG. '
              'JSR increments N and installs its target in the new PC register; RSR decrements N. '
              'Neither changes PG. EXR exchanges Rr and X without changing flags.\n',
              'EIN/DIN/SEL/REL/SEZ/REZ apply their flag strobe at T2 of the following fetch. '
              'See [timing conventions](timing.md) before interpreting instruction boundaries. '
              'Detailed evidence and uncertainties: [existing catalogue](../instruction-set.md).\n']
    outputs['instructions.md']='\n'.join(lines)
    lines=['# CMC8 MOP list\n',NAV,
           'Numbers 1–50 come from figure 4.2 (printed p.38), 51–55 from the branch circuit (p.72), '
           'and 57 from the shift circuit (p.79). No MOP56 has been identified; no number is invented for it. '
           'These are functional controls, not a claim that each is one physical wire. '
           'Short names describe the selected v018 interpretation.\n',
           '| MOP | Short name | Explanation |','| --- | --- | --- |']
    for n,description in MOPS.items():
        lines.append(f'| {n} | {SHORT[n]} | {EXPLANATIONS.get(n, description)} |')
    lines += ['\nA and B here mean ALU inputs, not address bytes or register selectors. '
              'MOP11 shifts the ALU output through the MUX; MOP12 captures that MUX output in BR. '
              'MOP3 and MOP7 enable the two ALU operands; MOP8/9/10 choose the operation. '
              'MOP7 alone allows A to pass through. MOP5 complements BR before driving DI.\n',
              '## Named controls without identified MOP numbers\n',
              '| Control | Meaning |','| --- | --- |',
              '| EXR A.capture | Capture DI into the added ALU input-A latch at F2T0 (H019). |',
              '| EXR A.held | Select the held A value instead of live DI at F2T5 (H019). |',
              '| DCR zero=DI | Use final DI for MOP32 at F2T6 (H014; omitted zero circuitry). |',
              '| STRCS | Control-byte strobe at SCS/SCW F1T6; an external receiver may use a latch. |',
              '| clear INTA | Reset-cycle T0 acknowledgement clear. |',
              '| IRQ set gate | INTE and active-low INT set pending INTR asynchronously. |',
              '| HALT observation | Internal HALT latch and SSE handshake govern fetch continuation; H023 reconstructs omitted timing. |',
              '\nThe external control-byte receiver is not the added internal EXR latch. '
              'See [the diagram](processor.svg) and [v018](../model-v018.md).\n']
    outputs['mops.md']='\n'.join(lines)
    lines=['# CMC8 instruction MOP timing\n',NAV,
           '## Reading the tables\n',
           'These are expanded **v018 working-model** tables, including derived schedules; they are not all printed microcode. '
           'Each cell lists controls held during that subdivision; — means no listed control. '
           '**Italic entries** belong to the shared F0 fetch (T0–T5). '
           'F0T6/T7 are instruction-dependent, so they are not italicized. '
           'The inherited duplicate PME in the LRS transcription is shown only once.\n',
           'IR captures the new opcode at the end of F0T5. Earlier F0 controls are shared sequencing; '
           'the old IR still selects a preceding flag instruction at F0T2. '
           'Thus a table groups fetch with its newly decoded instruction for reading, but does not imply all its cells '
           'are decoded from that instruction. Deferred flag strobes are described separately because they belong to the preceding instruction.\n',
           'MOP31 at F1T1 changes phase to F2 without restarting T: the next cell is **F2T2**. '
           'Cells F1T2–T7 and F2T0–T1 are unreachable in these two-cycle schedules and marked ×. '
           'Repeated controls are held levels, not repeated independent transfers. Data state is captured from '
           'start-of-slot signals; IR additionally captures at slot end. Controls in one cell act together, not left-to-right.\n',
           '### Shared overlays and waits\n',
           '- With interrupt integration, add *28 INTR→INTA* at F0T0; a pending request selects the separate interrupt-entry cycle.\n',
           '- With reset integration, add 47 RESET? at every executed T7, including wait and special cycles.\n',
           '- With execution control, every external read that will capture a byte gets 29 MEMR? at T4 '
           '(H022). Additions omitted by the base table are marked `[H022]` below. This also covers SCS/SCW F1 control-byte reads.\n',
           '- Fetch-context T3 may additionally assert 48 0→SSE or 49 1→SSE, according to HALT/SS/SSE (H023). '
           'These are conditional controller overlays, not unconditional entries in every table.\n',
           '- A failed T4 memory/HALT test suppresses that cell’s CPU write, holds the external enable, '
           'and enters an eight-slot F3 continuation. F3 holds the enable and retests at T4; on release the suspended '
           'T4 controls complete before T5. SCW F3 instead holds PME throughout and samples 50 SCWR? each T4.\n',
           '## Instruction tables\n']
    for e in entries:
        name=e['mnemonic']; phases=SEQUENCES[name]
        lines += [f'### {name}\n',
                  f'{card.form(e)} · {e["base_cycles"]} cycles · [source notes and confidence](../instructions/{name}.md)\n',
                  '| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |',
                  '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        skip=31 in phases[1][1] if len(phases)>1 else False
        for f,phase in enumerate(phases):
            cells=[]
            for t,numbers in enumerate(phase):
                if skip and ((f==1 and t>=2) or (f==2 and t<2)):
                    cells.append('×');continue
                parts=[mop(n, f==0 and t<6) for n in dict.fromkeys(numbers)]
                if t==4 and 29 not in numbers and 23 not in numbers and any(n in numbers for n in (24,25,26)):
                    if f==0 or 2 in phase[5] or (name in {'SCS','SCW'} and f==1):
                        parts.append(mop(29,f==0)+' [H022]')
                if name in BRANCHES and (f,t)==(2,6):
                    parts.append('if H=0: '+mop(22))
                    if name in PAGE_BRANCHES:parts.append('if H=0: '+mop(15))
                mode=ALU_A_MODES.get((name,f,t))
                if mode:parts.append('A.'+mode+' [H019]')
                if (name,f,t) in ZERO_SOURCES:parts.append('zero=DI [H014]')
                if name in {'SCS','SCW'} and (f,t)==(1,6):parts.append('STRCS (unnumbered)')
                cells.append('<br>'.join(parts) or '—')
            lines.append('| F'+str(f)+' | '+' | '.join(cells)+' |')
        flag=next((x for x in FLAG_INSTRUCTIONS.values() if x.name==name),None)
        if flag:
            lines.append(f'\n**Deferred effect:** {mop(flag.mop)} at **following F0T2**, alongside that fetch’s italic controls. '
                         f'Confidence: {flag.confidence}; {flag.basis}.')
        lines.append('')
    lines += ['## Separate entry cycles\n','These cycles have no opcode and are not standard fetches. PG is unchanged by interrupt entry. '
              'Reset clears PG/N/current PC and INTA as shown; it does not clear INTR or unlisted flags.\n']
    for name,seq in [('Interrupt entry',INTERRUPT_ENTRY),('Reset',RESET_CYCLE)]:
        lines += [f'### {name}\n','| T | Controls |','| --- | --- |']
        for t,nums in enumerate(seq):
            text='<br>'.join(mop(n) for n in nums)
            if name=='Reset' and t==0:text+='<br>clear INTA (unnumbered)'
            lines.append(f'| T{t} | {text or "—"} |')
    outputs['timing.md']='\n'.join(lines)+'\n'
    outputs['README.md']='''# CMC8 learning reference

Start with the [instruction card](instructions.md), keep the [MOP list](mops.md) beside the
[phase tables](timing.md), and use the [internal-structure SVG](processor.svg) to follow each transfer.

![CMC8 working-model internal structure](processor.svg)

This is a learning view of the **v018 research model**, based on the CMC8 material in the book.
The diagram is a functional redraw, not a die layout or a wiring/netlist claim. Blue paths carry
8-bit data; green paths carry addresses; purple paths carry selection/condition/control signals.
Dashed orange elements mark the added EXR holding latch and the provisional DCR zero-input path.
The numbered functions remain those in the book; named extra controls have no invented MOP number.

The register file has one selected port: PC means R(N), Rr means R(IR[2:0]), X means R7.
These can alias. PG supplies the high two memory-address bits, AB the low eight; ED ports use AB only.
N wraps modulo eight; register values and address offsets wrap modulo 256.

Only the source-linked notes distinguish printed timing, accepted corrections, and extrapolated
schedules in detail. Each instruction table links to its existing evidence record. In particular,
EXR's latch (H019), DCR's zero source (H014), inferred indexed transfers, and shared wait/single-step
controls remain working choices. Successful simulation is evidence of consistency, not silicon proof.
Other architectures illustrated by the book are not incorporated here.

These Markdown files are generated by `python3 tools/build_learning_reference.py`;
`--check` checks reproducibility. The SVG is separately authored for readability.
The original [full catalogue](../instruction-set.md), [book errata](../errata.md), and
[v018 execution-control notes](../model-v018.md) remain the detailed references.
'''
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    directory=ROOT/'docs/learning'
    directory.mkdir(exist_ok=True)
    for name,text in build().items():
        path=directory/name
        if args.check:
            if not path.exists() or path.read_text()!=text:
                raise SystemExit(f'Stale reference: {path}')
        else:path.write_text(text)
    print('Checked' if args.check else 'Wrote', '43 instruction rows, 56 identified MOPs, 43 timing tables and entry cycles')


if __name__=='__main__':
    main()
