#!/usr/bin/env python3
"""Compare the C instruction core with v018, including register/PC aliases.

Optional research check; normal app builds use only this directory and the SDK.
"""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from cmc8.versions.v018 import InstructionSimulator, Memory, State
from cmc8.versions.v018.sequences import decode


def main():
    executable=sys.argv[1] if len(sys.argv)>1 else ROOT/'x7_midahs/build-host/midahs-host'
    payload=bytearray()
    expected=[]
    for opcode in range(256):
        try:
            name=decode(opcode)
        except ValueError:
            continue
        if name in {'EIN','DIN','SEL','REL','SEZ','REZ','SCW','SCS'}:
            continue
        for n,pc,flag in ((0,32,0),(7,255,1)):
            registers=[0x80+i*9 for i in range(8)];registers[n]=pc
            program=[(i*17+11)&255 for i in range(1024)]
            storage=[(i*13+7)&255 for i in range(1024)]
            ports=[i*3+5 for i in range(7)]
            program[256+pc]=opcode;program[256+((pc+1)&255)]=4
            state=State(n=n,pg=1,link=flag,z=flag,inte=0,h=0,t=0)
            state.registers=registers.copy()
            memory=Memory(program=dict(enumerate(program)),storage=dict(enumerate(storage)),devices=dict(enumerate(ports)))
            cpu=InstructionSimulator(state,memory,test_inputs=(0,1,0,1))
            trace=cpu.run_instruction()
            expected.append((opcode,n,[*cpu.state.registers,cpu.state.pg,cpu.state.n,cpu.state.z,cpu.state.link,len(trace)//8,0]))
            payload.extend(bytes([*program,*storage,*ports,*registers,n,1,flag,flag,10,0]))
    output=subprocess.run([str(executable),'--oracle'],input=payload,check=True,capture_output=True).stdout.decode().splitlines()
    if len(output)!=len(expected):raise SystemExit('Incomplete native result')
    for (opcode,n,values),line in zip(expected,output,strict=True):
        actual=list(map(int,line.split()))
        if actual!=values:raise SystemExit(f'Opcode {opcode:02X}, N={n}: {actual} != {values}')
    print(f'{len(expected)} instruction results/cycle counts match v018, including PC aliases and wrapping')


if __name__=='__main__':main()
