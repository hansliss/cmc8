"""One-cycle NOP, mixed instruction lengths and prior instruction regression."""
from dataclasses import asdict
import json
import unittest

from cmc8.versions.v004 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v004 import Memory as PreviousMemory
from cmc8.versions.v004 import State as PreviousState
from cmc8.versions.v005 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v005.sequences import decode


class NopTests(unittest.TestCase):
    def test_only_zero_is_nop(self):
        self.assertEqual(decode(0), "NOP")
        for opcode in (1, 2, 3, 4, 5, 6, 7):
            with self.assertRaises(ValueError):
                decode(opcode)

    def test_one_cycle_for_every_pc_selector_page_and_wrap(self):
        for n in range(8):
            for page in range(4):
                for pc in (0, 0x7F, 0xFF):
                    with self.subTest(n=n, page=page, pc=pc):
                        state = State(n=n, pg=page, link=1, z=1, inte=1, intr=1,
                                      inta=1, sse=1)
                        state.registers = list(range(0x30, 0x38))
                        state.registers[n] = pc
                        expected = list(state.registers)
                        expected[n] = (pc + 1) & 255
                        memory = Memory(program={(page << 8) | pc: 0},
                                        storage={0: 0xA6}, devices={0: 0x69})
                        before = asdict(memory)
                        sim = InstructionSimulator(state, memory)
                        trace = sim.run_instruction()
                        self.assertEqual(len(trace), 8)
                        self.assertEqual([(r.phase, r.timing) for r in trace],
                                         [(0, t) for t in range(8)])
                        self.assertEqual(sim.state.registers, expected)
                        self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))
                        self.assertEqual((sim.state.ir, sim.state.pg), (0, page))
                        for flag in ("link", "z", "inte", "intr", "inta", "sse"):
                            self.assertEqual(getattr(sim.state, flag), 1)
                        self.assertEqual(asdict(memory), before)

    def test_fetch_landmarks_and_no_execution_access(self):
        state = State(n=0, pg=2)
        state.registers[0] = 0x20
        sim = InstructionSimulator(state, Memory(program={0x220: 0}))
        trace = sim.run_instruction()
        self.assertEqual(trace[1].start.after.ab, 0x20)
        self.assertEqual(trace[3].start.after.br, 0x21)
        self.assertEqual(trace[4].start.after.registers[0], 0x21)
        self.assertEqual(trace[5].end.after.ir, 0)
        self.assertEqual([r.timing for r in trace if "PME" in r.start.signals.outputs],
                         [2, 3, 4, 5])
        self.assertTrue(all(not ({"SME", "EDE", "WRITE", "DBDIR"}
                                 & set(r.start.signals.outputs)) for r in trace))
        self.assertTrue(all(r.memory_write is None for r in trace))
        # Explicit minimal-tail assumption: AB is not preloaded at T6.
        self.assertEqual(trace[6].mops, ())
        self.assertEqual(trace[7].mops, (30,))
        self.assertEqual(sim.state.ab, 0x20)
        self.assertEqual(sim.state.br, 0x21)

    def test_consecutive_nops_fetch_successive_addresses(self):
        state = State(n=3, pg=1)
        state.registers[3] = 0xFE
        sim = InstructionSimulator(state, Memory(program={0x1FE: 0, 0x1FF: 0, 0x100: 0}))
        for expected_pc in (0xFF, 0, 1):
            trace = sim.run_instruction()
            self.assertEqual(len(trace), 8)
            self.assertEqual(sim.state.registers[3], expected_pc)
        self.assertEqual(len(sim.trace), 24)

    def test_nop_and_load_store_lengths_can_be_mixed(self):
        state = State(n=0, pg=0)
        state.registers[0] = 0x20
        program = dict(enumerate([0, 0x53, 0x80, 0, 0x73, 0x81, 0], start=0x20))
        sim = InstructionSimulator(state, Memory(program=program, storage={0x80: 0xA6}))
        for length, name in [(8, "NOP"), (24, "LRS"), (8, "NOP"),
                             (24, "SRS"), (8, "NOP")]:
            trace = sim.run_instruction()
            self.assertEqual(len(trace), length)
            self.assertEqual(trace[6].instruction, name)
        self.assertEqual(sim.state.registers[0], 0x27)
        self.assertEqual(sim.memory.storage[0x81], 0xA6)
        self.assertEqual(len(sim.trace), 72)
        self.assertEqual(json.loads(json.dumps(sim.trace[-1].to_dict()))["version"], "v005")

    def test_late_opcode_uses_ir_end_of_t5_capture(self):
        state = State(n=0, pg=0)
        state.registers[0] = 0
        sim = InstructionSimulator(state, Memory(program={0: 0}, program_delay=4))
        trace = sim.run_instruction()
        self.assertIsNone(trace[5].start.after.ir)
        self.assertEqual(trace[5].end.after.ir, 0)
        self.assertEqual(len(trace), 8)

    def test_missing_opcode_does_not_become_nop(self):
        state = State(n=0, pg=0)
        state.registers[0] = 0
        sim = InstructionSimulator(state, Memory())
        for _ in range(5):
            sim.step()
        with self.assertRaisesRegex(ModelError, "DB is not valid"):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 5))
        self.assertEqual(len(sim.trace), 5)

    def test_existing_families_still_match_v004(self):
        for opcode in (0x43, 0x53, 0x63, 0x73, 0x13, 0x1B):
            for page in range(4):
                state = State(n=0, pg=page)
                state.registers = [0xA6] * 8
                state.registers[0] = 0x20
                base = page << 8
                memory = Memory(program={base | 0x20: opcode, base | 0x21: 0x80,
                                         base | 0x80: 0x69},
                                storage={base | 0x80: 0x56}, devices={0x80: 0x45})
                previous = PreviousSimulator(PreviousState(**asdict(state)),
                                             PreviousMemory(**asdict(memory)))
                sim = InstructionSimulator(state, memory)
                trace = sim.run_instruction()
                expected = previous.run_instruction()
                self.assertEqual(len(trace), 24)
                self.assertEqual(asdict(sim.state), asdict(previous.state))
                self.assertEqual(asdict(sim.memory), asdict(previous.memory))
                for actual, old in zip(trace, expected):
                    self.assertEqual(actual.mops, old.mops)
                    self.assertEqual(asdict(actual.start.after), asdict(old.start.after))
                    self.assertEqual(asdict(actual.end.after), asdict(old.end.after))


if __name__ == "__main__":
    unittest.main()
