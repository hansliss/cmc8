"""Compare browser instruction results with the signaling model, including aliases."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from cmc8.versions.v018 import InstructionSimulator, Memory, State
from cmc8.versions.v018.sequences import decode

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'), 'Node.js is needed for browser CPU checks')
class BrowserCPUTests(unittest.TestCase):
    def test_results_and_cycles_against_signaling_model(self):
        cases = []
        for opcode in range(256):
            try:
                name = decode(opcode)
            except ValueError:
                continue
            # Flag effects are deferred in the signal model; device handshakes
            # are board-dependent. Both have separate scope/behavior tests.
            if name in {'EIN', 'DIN', 'SEL', 'REL', 'SEZ', 'REZ', 'SCW', 'SCS'}:
                continue
            for n, pc, flag in [(0,32,0), (7,255,1)]:
                registers = [0x80+i*9 for i in range(8)]
                registers[n] = pc
                program = [(i*17+11)&255 for i in range(1024)]
                storage = [(i*13+7)&255 for i in range(1024)]
                devices = [(i*3+5)&255 for i in range(256)]
                program[256+pc] = opcode
                program[256+((pc+1)&255)] = 0x42
                state = State(n=n, pg=1, link=flag, z=flag, inte=0, h=0, t=0)
                state.registers = registers.copy()
                memory = Memory(program=dict(enumerate(program)),
                                storage=dict(enumerate(storage)),
                                devices=dict(enumerate(devices)))
                sim = InstructionSimulator(state, memory, test_inputs=(0,1,0,1))
                trace = sim.run_instruction()
                cases.append(dict(opcode=opcode, n=n, pc=pc, flag=flag,
                                  registers=registers, program=program,
                                  storage=storage, devices=devices,
                                  expected=dict(registers=sim.state.registers,
                                                pg=sim.state.pg, n=sim.state.n,
                                                z=bool(sim.state.z), link=bool(sim.state.link),
                                                cycles=len(trace)//8,
                                                program=list(memory.program.values()),
                                                storage=list(memory.storage.values()),
                                                devices=list(memory.devices.values()))))
        script = """
import {CPU} from './demos/shared/cpu.mjs';
import fs from 'node:fs';
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
class TestCPU extends CPU {
  readPort(port){return this.devices[port];}
  writePort(port,value){this.devices[port]=value;}
  readMemory(space,address){return this[space==='program'?'memory':'storage'][this.pg*256+address];}
  writeMemory(space,address,value){this[space==='program'?'memory':'storage'][this.pg*256+address]=value;}
}
const results=cases.map(test=>{
  const cpu=new TestCPU(Uint8Array.from(test.program));
  cpu.storage=Uint8Array.from(test.storage);cpu.devices=Uint8Array.from(test.devices);
  cpu.r.set(test.registers);cpu.pg=1;cpu.n=test.n;cpu.z=Boolean(test.flag);cpu.link=Boolean(test.flag);
  cpu.tests=[false,true,false,true];const initial=cpu.cycles;cpu.step();
  return {registers:[...cpu.r],pg:cpu.pg,n:cpu.n,z:cpu.z,link:cpu.link,cycles:cpu.cycles-initial,
          program:[...cpu.memory],storage:[...cpu.storage],devices:[...cpu.devices]};
});
process.stdout.write(JSON.stringify(results));
"""
        result = subprocess.run(['node', '--input-type=module', '-e', script], cwd=ROOT,
                                input=json.dumps(cases), capture_output=True, text=True, check=True)
        for case, actual in zip(cases, json.loads(result.stdout), strict=True):
            with self.subTest(opcode=hex(case['opcode']), n=case['n'], pc=case['pc']):
                self.assertEqual(actual, case['expected'])
