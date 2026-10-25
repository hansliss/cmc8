"""Independent expectations from figures 4.9–4.13 and the p.53 prose."""
import json
import unittest

from cmc8.versions.v001 import Simulator as BaselineSimulator
from cmc8.versions.v001 import State as BaselineState
from cmc8.versions.v002 import InstructionSimulator, Memory, ModelError, Simulator, State
from cmc8.versions.v002.sequences import PRINTED_LRS


def experiment(opcode=0x53, operand=0x80, value=0xA6, **options):
    state = State(n=0, pg=0, link=1, z=0)
    state.registers[0] = 0x20
    state.registers[3] = value
    memory = Memory(program={0x20: opcode, 0x21: operand}, storage={operand: value})
    return InstructionSimulator(state, memory, **options)


class InstructionTests(unittest.TestCase):
    def test_lrs_internal_landmarks(self):
        sim = experiment()
        trace = sim.run_instruction()
        # Expected effects independently read from fig.4.11, not generated MOPs.
        self.assertEqual(len(trace), 24)
        self.assertEqual(trace[1].start.after.ab, 0x20)
        self.assertEqual(trace[3].start.after.br, 0x21)
        self.assertEqual(trace[4].start.after.registers[0], 0x21)
        self.assertEqual(trace[5].end.after.ir, 0x53)
        self.assertEqual(trace[6].start.after.ab, 0x21)
        self.assertEqual(trace[11].start.after.br, 0x22)
        self.assertEqual(trace[12].start.after.registers[0], 0x22)
        self.assertEqual(trace[13].start.after.br, 0x80)
        self.assertEqual(trace[14].start.after.ab, 0x80)
        self.assertEqual(trace[21].start.after.br, 0xA6)
        self.assertEqual(trace[22].start.after.registers[3], 0xA6)
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))
        self.assertEqual((sim.state.ir, sim.state.link, sim.state.z), (0x53, 1, 0))

    def test_lrs_memory_enable_windows(self):
        trace = experiment().run_instruction()
        pme = [(row.phase, row.timing) for row in trace if "PME" in row.start.signals.outputs]
        sme = [(row.phase, row.timing) for row in trace if "SME" in row.start.signals.outputs]
        self.assertEqual(pme, [(p, t) for p in (0, 1) for t in (2, 3, 4, 5)])
        self.assertEqual(sme, [(2, t) for t in (2, 3, 4, 5)])
        self.assertTrue(all("DBDIR" not in row.start.signals.outputs for row in trace))

    def test_srs_waveform_windows_and_write_completion(self):
        sim = experiment(opcode=0x73)
        sim.memory.storage[0x80] = 0
        trace = sim.run_instruction()
        self.assertEqual(sim.memory.storage[0x80], 0xA6)
        self.assertEqual(sim.state.registers[3], 0xA6)
        self.assertEqual(sim.state.registers[0], 0x22)
        # fig.4.13: SME starts earlier than for LRS; WRITE finishes first.
        for signal, expected in [
            ("SME", [(2, t) for t in range(6)]),
            ("WRITE", [(2, t) for t in range(1, 5)]),
            ("DBDIR", [(1, 7)] + [(2, t) for t in range(6)]),
        ]:
            observed = [(row.phase, row.timing) for row in trace
                        if signal in row.start.signals.outputs]
            self.assertEqual(observed, expected)
        self.assertEqual(trace[14].start.after.ab, 0x80)
        self.assertEqual(trace[14].start.signals.di, 0xA6)
        self.assertTrue(all(row.start.signals.db == 0xA6 for row in trace[15:22]))
        self.assertEqual([(r.phase, r.timing, r.memory_write) for r in trace if r.memory_write],
                         [(2, 5, (0x80, 0xA6))])

    def test_ir_latch_accepts_data_that_arrives_during_t5(self):
        sim = experiment()
        sim.memory.program_delay = 4
        for _ in range(6):
            row = sim.step()
        self.assertIsNone(row.start.after.ir)
        self.assertEqual(row.end.after.ir, 0x53)
        # Same delay is too late for F1's leading-edge BR capture.
        for _ in range(7):
            sim.step()
        with self.assertRaisesRegex(ModelError, "start of T5"):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (1, 5))

    def test_br_does_not_capture_data_arriving_at_end_of_t5(self):
        sim = experiment()
        sim.memory.storage_delay = 4
        for _ in range(21):
            sim.step()
        with self.assertRaisesRegex(ModelError, "start of T5"):
            sim.step()
        self.assertEqual(sim.state.br, 0x80)
        self.assertEqual(len(sim.trace), 21)
        sim.memory.storage_delay = 3
        sim.step()
        self.assertEqual(sim.state.br, 0xA6)

    def test_literal_printed_table_is_a_reproducible_alternative(self):
        sim = experiment(interpretation="printed")
        for _ in range(14):
            sim.step()
        self.assertEqual(sim.state.ir, 0x80)  # Printed MOP1 overwrites the opcode.
        self.assertEqual(sim.state.br, 0x22)  # Operand address did not enter BR.
        self.assertEqual(PRINTED_LRS[1][1], (18, 21))
        self.assertEqual(PRINTED_LRS[1][5], (1, 24))
        self.assertEqual(PRINTED_LRS[0][2], (18, 21, 24, 24))

    def test_load_and_store_all_register_selectors_including_pc(self):
        for n in range(8):
            for target in range(8):
                for value in (0, 1, 0x7F, 0x80, 0xFF):
                    for name, base in [("LRS", 0x50), ("SRS", 0x70)]:
                        with self.subTest(n=n, target=target, value=value, instruction=name):
                            state = State(n=n, pg=0)
                            state.registers = [value] * 8
                            state.registers[n] = 0xFE
                            memory = Memory(program={0xFE: base | target, 0xFF: 0x80},
                                            storage={0x80: value})
                            sim = InstructionSimulator(state, memory)
                            sim.run_instruction()
                            if name == "LRS":
                                self.assertEqual(sim.state.registers[target], value)
                                if target != n:
                                    self.assertEqual(sim.state.registers[n], 0)
                            else:
                                expected = 0 if target == n else value
                                self.assertEqual(memory.storage[0x80], expected)
                                self.assertEqual(sim.state.registers[n], 0)

    def test_page_adapter_and_pc_wrap(self):
        state = State(n=2, pg=3)
        state.registers[2] = 0xFF
        memory = Memory(program={0x3FF: 0x53, 0x300: 0xF0}, storage={0xF0: 0x19})
        sim = InstructionSimulator(state, memory)
        sim.run_instruction()
        self.assertEqual(sim.state.registers[2], 1)
        self.assertEqual(sim.state.registers[3], 0x19)
        self.assertEqual(sim.state.pg, 3)

    def test_two_instructions_execute_from_memory(self):
        sim = experiment()
        sim.memory.program.update({0x22: 0x73, 0x23: 0x81})
        sim.run_instruction()
        self.assertNotIn(0x81, sim.memory.storage)
        sim.run_instruction()
        self.assertEqual(sim.memory.storage[0x81], 0xA6)
        self.assertEqual(sim.state.registers[0], 0x24)
        self.assertEqual(len(sim.trace), 48)
        self.assertEqual(sim.trace[30].instruction, "SRS")
        encoded = json.loads(json.dumps(sim.trace[-1].to_dict()))
        self.assertEqual(encoded["version"], "v002")
        self.assertEqual(encoded["interpretation"], "text")

    def test_unsupported_instruction_is_reported(self):
        sim = experiment(opcode=0)
        for _ in range(6):
            sim.step()
        with self.assertRaisesRegex(ModelError, "Unsupported opcode"):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 6))
        self.assertEqual(len(sim.trace), 6)

    def test_write_is_not_committed_before_falling_edge(self):
        sim = experiment(opcode=0x73)
        sim.memory.storage[0x80] = 0
        for _ in range(21):
            sim.step()
        self.assertEqual(sim.memory.storage[0x80], 0)
        sim.step()
        self.assertEqual(sim.memory.storage[0x80], 0xA6)

    def test_corrupted_store_data_is_rejected_without_partial_write(self):
        sim = experiment(opcode=0x73)
        for _ in range(18):
            sim.step()
        sim.state.registers[3] = 0x12
        before = dict(sim.memory.storage)
        with self.assertRaisesRegex(ModelError, "changed while WRITE"):
            sim.step()
        self.assertEqual(sim.memory.storage, before)
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 2))

    def test_ready_and_initialization_requirements_are_explicit(self):
        with self.assertRaisesRegex(ModelError, "always-ready"):
            experiment(ready=False)
        with self.assertRaisesRegex(ModelError, "memory_ready=True"):
            Simulator().capture([29])
        with self.assertRaisesRegex(ModelError, "Program read needs known"):
            sim = InstructionSimulator(State(), Memory())
            for _ in range(3):
                sim.step()

    def test_baseline_remains_unchanged(self):
        with self.assertRaisesRegex(Exception, "MOP29"):
            BaselineSimulator(BaselineState()).capture([29])


if __name__ == "__main__":
    unittest.main()
