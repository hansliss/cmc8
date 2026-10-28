#!/usr/bin/env python3
"""Generate the on-device card from the authored instruction catalogue.

Normal builds consume the committed header; this optional tool needs the research
catalogue. --coverage HOST also checks every opcode against the production C core.
"""
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
DESCRIPTIONS={
    'LRM':'PM A TO Rr','LRS':'SM A TO Rr','LRX':'PM X TO Rr','LSX':'SM X TO Rr',
    'LRD':'PORT P TO Rr','SRM':'Rr TO PM A','SRS':'Rr TO SM A','SRX':'Rr TO PM X',
    'SSX':'Rr TO SM X','SRD':'Rr TO PORT P','BB0':'IF Rr BIT0 CLEAR','BB1':'IF Rr BIT0 SET',
    'BL0':'IF L CLEAR','BL1':'IF L SET','BZ0':'IF Z CLEAR','BZ1':'IF Z SET',
    'BT0':'IF TEST t LOW','BT1':'IF TEST t HIGH','JMP':'JUMP PAGE p',
    'JCR':'JUMP TO Rr','LRI':'I TO Rr','XRI':'Rr XOR I TO Rr','ANI':'Rr AND I TO Rr',
    'CPY':'Rr TO X','INR':'INCREMENT Rr','ROR':'ROTATE RIGHT',
    'SHR':'SHIFT RIGHT ZERO','RRL':'RIGHT THROUGH L','DCR':'DECREMENT Rr',
    'XOR':'Rr XOR X TO X','AND':'Rr AND X TO X','EXR':'EXCHANGE Rr X',
    'SCW':'CONTROL THEN WAIT','SCS':'SEND CONTROL','JSR':'CALL NEXT PC REG',
    'RSR':'RETURN PREV PC','NOP':'FETCH ONLY','EIN':'ENABLE IRQ','DIN':'DISABLE IRQ',
    'SEL':'SET L','REL':'CLEAR L','SEZ':'SET Z','REZ':'CLEAR Z'
}


def form(entry):
    name=entry['mnemonic']
    if name in {'LRI','XRI','ANI'}:return name+' Rr,#I'
    if name in {'LRM','LRS','SRM','SRS','BB0','BB1'}:return name+' Rr,A'
    if name in {'LRD','SRD'}:return name+' Rr,P'
    if 'RRR' in entry['pattern']:return name+' Rr'
    if 'PP' in entry['pattern']:return name+' p,A'
    if 'TT' in entry['pattern']:return name+' t,A'
    if name=='JSR':return name+' A'
    if name in {'SCS','SCW'}:return name+' #I'
    return name


def main():
    catalogue=json.loads((ROOT/'specification/instructions.json').read_text())['instructions']
    lines=['/* Generated from specification/instructions.json; regenerate with tools/export_reference.py. */',
           '#ifndef X7_MIDAHS_REFERENCE_H','#define X7_MIDAHS_REFERENCE_H',
           '#define REFERENCE_ROWS 43','#define REFERENCE_PAGE_ROWS 22','#define REFERENCE_PAGES 2',
           'struct reference_row { const char *form, *bits, *octal, *flags, *meaning; unsigned bytes, cycles; };',
           'static const struct reference_row reference_rows[REFERENCE_ROWS] = {']
    for entry in sorted(catalogue,key=lambda e:e['mnemonic']):
        variable='r' if 'RRR' in entry['pattern'] else 'p' if 'PP' in entry['pattern'] else 't' if 'TT' in entry['pattern'] else ''
        octal=f'{entry["value"]:03o}'+('+'+variable if variable else '')
        values=[form(entry),entry['pattern'].lower(),octal,''.join(entry['flags']) or '-',DESCRIPTIONS[entry['mnemonic']]]
        lines.append('    {'+', '.join(json.dumps(value) for value in values)+f', {entry["length_bytes"]}, {entry["base_cycles"]}'+'},')
    lines+=['};','#endif','']
    output=ROOT/'x7_midahs/generated/reference.h';text='\n'.join(lines)
    if '--check' in sys.argv:
        if output.read_text()!=text:raise SystemExit('Stale generated/reference.h')
        print('All 43 reference rows match the instruction catalogue')
    else:output.write_text(text)
    if '--coverage' in sys.argv:
        executable=sys.argv[sys.argv.index('--coverage')+1]
        rows=subprocess.check_output([executable,'--opcodes'],text=True).splitlines()
        if len(rows)!=256:raise SystemExit('Incomplete opcode coverage result')
        valid=0
        for opcode,line in enumerate(rows):
            encoded,cycles,fault=map(int,line.split())
            entries=[e for e in catalogue if opcode&e['mask']==e['value']]
            if encoded!=opcode:raise SystemExit('Mismatched opcode order')
            if entries:
                if len(entries)!=1 or fault or cycles!=entries[0]['base_cycles']:
                    raise SystemExit(f'Opcode {opcode:02X}: {line}, expected {entries}')
                valid+=1
            elif not fault:raise SystemExit(f'Unassigned opcode {opcode:02X} was accepted')
        if valid!=239:raise SystemExit(f'Expected 239 valid encodings, got {valid}')
        print('All 239 valid opcodes execute with catalogue cycle counts; all 17 unassigned bytes fault')


if __name__=='__main__':main()
