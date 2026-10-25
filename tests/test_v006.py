"""Tests of the selected flag timing model, not interrupt/branch conformance."""
from dataclasses import asdict
import json
import unittest

from cmc8.versions.v005 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v005 import Memory as PreviousMemory
from cmc8.versions.v005 import State as PreviousState
from cmc8.versions.v006 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v006.sequences import decode


# Independent expectations from fig.4.2 and the agreed timing interpretation.
FLAGS = [(0x02, "DIN", "inte", 0, 39), (0x03, "EIN", "inte", 1, 38),
         (0x04, "REL", "link", 0, 35), (0x05, "SEL", "link", 1, 34),
         (0x06, "REZ", "z", 0, 37), (0x07, "SEZ", "z", 1, 36)]


def experiment(opcodes, *, n=0, page=2, initial=0, pc=0x20):
    state = State(n=n, pg=page, inte=initial, link=initial, z=initial, intr=1, inta=0)
    state.registers = list(range(0x30, 0x38))
    state.registers[n] = pc
    program = {(page << 8) | ((pc + offset) & 255): opcode
               for offset, opcode in enumerate(opcodes)}
    return InstructionSimulator(state, Memory(program=program, storage={0: 0xA6}, devices={0: 0x69}))


class FlagTimingTests(unittest.TestCase):
    def test_exact_opcodes(self):
        for opcode, name, *_ in FLAGS:
            self.assertEqual(decode(opcode), name)
        self.assertEqual(decode(0), "NOP")
        for opcode in (1, 8, 9, 12, 15):
            with self.assertRaises(ValueError):
                decode(opcode)

    def test_all_flags_selectors_pages_and_initial_values(self):
        for opcode, name, field, value, mop in FLAGS:
            for n in range(8):
                for page in range(4):
                    for initial in (0, 1):
                        with self.subTest(name=name, n=n, page=page, initial=initial):
                            sim = experiment([opcode, 0], n=n, page=page, initial=initial)
                            memory_before = asdict(sim.memory)
                            registers = list(sim.state.registers)
                            own_trace = sim.run_instruction()
                            self.assertEqual(len(own_trace), 8)
                            self.assertEqual(own_trace[6].instruction, name)
                            self.assertTrue(all(row.flag_effect is None for row in own_trace))
                            self.assertEqual(getattr(sim.state, field), initial)
                            self.assertEqual(sim.state.ir, opcode)
                            for timing in (0, 1):
                                row = sim.step()
                                self.assertEqual(row.timing, timing)
                                self.assertEqual(getattr(sim.state, field), initial)
                            row = sim.step()
                            self.assertEqual((row.phase, row.timing), (0, 2))
                            self.assertIn(mop, row.mops)
                            self.assertEqual(row.control_ir, opcode)
                            self.assertEqual(row.start.before.ir, opcode)
                            self.assertEqual(getattr(row.start.before, field), initial)
                            self.assertEqual(getattr(row.start.after, field), value)
                            self.assertEqual(row.flag_effect.name, name)
                            for other in ("inte", "link", "z"):
                                self.assertEqual(getattr(sim.state, other), value if other == field else initial)
                            registers[n] += 1
                            self.assertEqual(sim.state.registers, registers)
                            self.assertEqual((sim.state.intr, sim.state.inta), (1, 0))
                            self.assertEqual(asdict(sim.memory), memory_before)

    def test_ein_effect_precedes_replacement_of_ir(self):
        sim = experiment([0x03, 0x53, 0x80])  # EIN; LRS R3,[80]
        sim.memory.storage[0x280] = 0xA6
        sim.run_instruction()
        trace = sim.run_instruction()
        self.assertEqual(trace[2].control_ir, 0x03)
        self.assertEqual(trace[2].start.after.inte, 1)
        self.assertEqual(trace[5].end.after.ir, 0x53)
        self.assertEqual(trace[6].instruction, "LRS")
        self.assertEqual(sim.state.registers[3], 0xA6)
        self.assertEqual([r for r in trace if r.flag_effect is not None], [trace[2]])
        self.assertEqual(trace[2].flag_effect.confidence, "high")
        encoded = json.loads(json.dumps(trace[2].to_dict()))
        self.assertEqual(encoded["version"], "v006")
        self.assertEqual(encoded["flag_effect"]["basis"], "documented timing; derived decoder")

    def test_consecutive_set_clear_effects_use_the_previous_opcode(self):
        for set_opcode, clear_opcode, field in [(3, 2, "inte"), (5, 4, "link"), (7, 6, "z")]:
            sim = experiment([set_opcode, clear_opcode, 0, 0])
            sim.run_instruction()
            self.assertEqual(getattr(sim.state, field), 0)
            second = sim.run_instruction()
            self.assertEqual(second[2].control_ir, set_opcode)
            self.assertEqual(getattr(sim.state, field), 1)
            third = sim.run_instruction()
            self.assertEqual(third[2].control_ir, clear_opcode)
            self.assertEqual(getattr(sim.state, field), 0)
            fourth = sim.run_instruction()
            self.assertTrue(all(row.flag_effect is None for row in fourth))

    def test_all_six_in_a_stream_then_flush_with_nop(self):
        sim = experiment([3, 2, 5, 4, 7, 6, 0])
        for _ in range(7):
            self.assertEqual(len(sim.run_instruction()), 8)
        effects = [r.flag_effect.name for r in sim.trace if r.flag_effect]
        self.assertEqual(effects, ["EIN", "DIN", "SEL", "REL", "SEZ", "REZ"])
        self.assertEqual((sim.state.inte, sim.state.link, sim.state.z), (0, 0, 0))

    def test_delay_survives_pc_wraparound(self):
        sim = experiment([7, 0], n=7, page=3, pc=0xFF)
        sim.run_instruction()
        self.assertEqual((sim.state.registers[7], sim.state.z), (0, 0))
        sim.run_instruction()
        self.assertEqual((sim.state.registers[7], sim.state.z, sim.state.pg), (1, 1, 3))

    def test_uninitialized_ir_does_not_invent_a_flag_effect(self):
        sim = experiment([0])
        trace = sim.run_instruction()
        self.assertIsNone(trace[2].control_ir)
        self.assertIsNone(trace[2].flag_effect)
        self.assertEqual((sim.state.inte, sim.state.link, sim.state.z), (0, 0, 0))

    def test_resuming_from_explicit_retained_ir_needs_no_pending_latch(self):
        sim = experiment([0])
        sim.state.ir = 0x05  # Model a previous SEL still resident in IR.
        trace = sim.run_instruction()
        self.assertEqual(trace[2].flag_effect.name, "SEL")
        self.assertEqual(sim.state.link, 1)

    def test_manual_step_and_instruction_runs_match(self):
        manual = experiment([3, 0])
        automatic = experiment([3, 0])
        for _ in range(16):
            manual.step()
        automatic.run_instruction()
        automatic.run_instruction()
        self.assertEqual(asdict(manual.state), asdict(automatic.state))
        self.assertEqual([r.to_dict() for r in manual.trace], [r.to_dict() for r in automatic.trace])

    def test_missing_next_opcode_does_not_undo_prior_t2_effect(self):
        sim = experiment([3])
        sim.run_instruction()
        for _ in range(5):
            sim.step()
        with self.assertRaisesRegex(ModelError, "DB is not valid"):
            sim.step()
        self.assertEqual(sim.state.inte, 1)
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 5))
        self.assertEqual(len([r for r in sim.trace if r.flag_effect]), 1)

    def test_nop_uses_consistent_prefetch_tail_and_v005_is_preserved(self):
        sim = experiment([0])
        trace = sim.run_instruction()
        self.assertEqual(trace[6].mops, (6,))
        self.assertEqual(sim.state.ab, 0x21)
        old = PreviousSimulator(PreviousState(n=0, pg=0, registers=[0x20] * 8),
                                PreviousMemory(program={0x20: 0}))
        old.run_instruction()
        self.assertEqual(old.state.ab, 0x20)

    def test_prior_load_store_families_match_v005(self):
        for opcode in (0x43, 0x53, 0x63, 0x73, 0x13, 0x1B):
            sim = experiment([opcode, 0x80])
            sim.memory.program[0x280] = 0x69
            sim.memory.storage[0x280] = 0x56
            sim.memory.devices[0x80] = 0x45
            old = PreviousSimulator(PreviousState(**asdict(sim.state)),
                                    PreviousMemory(**asdict(sim.memory)))
            trace = sim.run_instruction()
            old_trace = old.run_instruction()
            self.assertEqual(len(trace), 24)
            self.assertEqual(asdict(sim.state), asdict(old.state))
            self.assertEqual(asdict(sim.memory), asdict(old.memory))
            self.assertEqual([r.mops for r in trace], [r.mops for r in old_trace])


if __name__ == "__main__":
    unittest.main()
