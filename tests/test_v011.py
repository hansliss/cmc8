"""Logical/arithmetic results, zero detection, timing, aliases and program use."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v011 import InstructionSimulator, Memory, ModelError, Simulator, State, evaluate
from cmc8.versions.v011.sequences import SEQUENCES, decode
from cmc8.versions.v010 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v010 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v010.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


def machine(opcode, *, n=0, page=1, pc=0x20):
    state = State(n=n, pg=page, link=1, z=1, inte=0, h=0, t=1)
    state.registers = [0x90 + index for index in range(8)]
    state.registers[n] = pc
    return InstructionSimulator(state, Memory(program={(page << 8) | pc: opcode}))


def without_new_metadata(value):
    if isinstance(value, dict):
        return {key: without_new_metadata(item) for key, item in value.items()
                if key not in {'version', 'zero_source', 'zero_value'}}
    if isinstance(value, (list, tuple)):
        return [without_new_metadata(item) for item in value]
    return value


class ZeroDetectorTests(unittest.TestCase):
    def test_and_alu_and_zero_flag_for_every_operand_pair(self):
        state = State(ir=0xB3)
        controls = (19, 21, 3, 7, 9, 12, 32)
        for left in range(256):
            state.registers[3] = left
            for right in range(256):
                state.br = right
                signals = evaluate(state, controls)
                expected = left & right
                self.assertEqual(signals.alu, expected)
                self.assertEqual(signals.writes, {'br': expected, 'z': int(expected == 0)})
                self.assertEqual((signals.zero_source, signals.zero_value), ('alu', expected))

    def test_zero_source_is_alu_before_mux(self):
        state = State(ir=0x83)
        state.registers[3] = 0
        signals = evaluate(state, (19, 21, 7, 10, 11, 43, 12, 32))
        self.assertEqual((signals.alu, signals.mux, signals.writes['z']), (1, 0, 0))

    def test_dcr_di_detector_differs_from_intermediate_alu_zero(self):
        for source, intermediate, result, z in ((0, 0, 255, 0), (1, 255, 0, 1), (255, 1, 254, 0)):
            cpu = Simulator(State(br=source))
            cpu.capture((5, 7, 10, 12))
            self.assertEqual(cpu.state.br, intermediate)
            row = cpu.capture((5, 32), zero_source='di')
            self.assertEqual(row.signals.di, result)
            self.assertEqual((row.signals.zero_source, row.signals.zero_value), ('di', result))
            self.assertEqual(row.after.z, z)

    def test_zero_capture_is_simultaneous_and_end_observation_does_not_repeat_it(self):
        state = State(ir=0x83, z=1)
        state.registers[3] = 255
        cpu = Simulator(state)
        row = cpu.capture((19, 21, 10, 7, 12, 32), point='start')
        self.assertEqual((row.after.br, row.after.z), (0, 1))
        cpu.state.registers[3] = 0
        row = cpu.capture((19, 21, 10, 7, 12, 32), point='end')
        self.assertEqual(row.signals.zero_value, 1)
        self.assertEqual((row.after.br, row.after.z), (0, 1))

    def test_unknown_manual_data_propagates_and_conflicting_controls_fail(self):
        self.assertIsNone(evaluate(State(), (32,)).writes['z'])
        for controls, source in (((32, 36), 'alu'), ((32, 37), 'alu'), ((), 'di'), ((32,), 'register')):
            with self.subTest(controls=controls, source=source), self.assertRaises(ModelError):
                evaluate(State(), controls, zero_source=source)


class ArithmeticInstructionTests(unittest.TestCase):
    def test_decoder_matches_entire_repertory(self):
        catalogue, _ = load_data()
        count = 0
        for opcode, name in validate(catalogue).items():
            if name in SEQUENCES:
                self.assertEqual(decode(opcode), name)
                count += 1
            else:
                with self.assertRaises(ValueError):
                    decode(opcode)
        self.assertEqual((len(SEQUENCES), count), (34, 181))

    def test_inr_dcr_every_value_and_both_initial_zero_flags(self):
        for opcode, delta in ((0x83, 1), (0xA3, -1)):
            for value in range(256):
                for initial_z in (0, 1):
                    sim = machine(opcode)
                    sim.state.registers[3] = value
                    sim.state.z = initial_z
                    expected = (value + delta) & 255
                    trace = sim.run_instruction()
                    self.assertEqual(sim.state.registers[3], expected)
                    self.assertEqual(sim.state.z, int(expected == 0))
                    self.assertEqual(sim.state.registers[0], 0x21)
                    self.assertEqual(len(trace), 24)

    def test_and_every_byte_with_distinct_masks_and_both_flag_outcomes(self):
        for value in range(256):
            for mask in (0, 255, 0x55, 0xAA):
                sim = machine(0xB3)
                sim.state.registers[3] = value
                sim.state.registers[7] = mask
                sim.state.z = int(value & mask != 0)  # Force a flag change.
                sim.run_instruction()
                self.assertEqual(sim.state.registers[7], value & mask)
                self.assertEqual(sim.state.registers[3], value)
                self.assertEqual(sim.state.z, int(value & mask == 0))
                self.assertEqual(sim.state.registers[0], 0x21)

    def test_all_register_pc_x_aliases_pages_and_fetch_wrap(self):
        for base, operation in ((0x80, 'INR'), (0xA0, 'DCR'), (0xB0, 'AND')):
            for n in range(8):
                for a in range(8):
                    for page in range(4):
                        for pc in (0x20, 0xFF):
                            sim = machine(base | a, n=n, page=page, pc=pc)
                            expected = list(sim.state.registers)
                            expected[n] = (pc + 1) & 255
                            if operation == 'AND':
                                result = expected[a] & expected[7]
                                expected[7] = result
                            else:
                                result = (expected[a] + (1 if operation == 'INR' else -1)) & 255
                                expected[a] = result
                            preserved = (sim.state.n, sim.state.pg, sim.state.link,
                                         sim.state.inte, sim.state.h, sim.state.t)
                            memory = asdict(sim.memory)
                            trace = sim.run_instruction()
                            self.assertEqual(sim.state.registers, expected)
                            self.assertEqual(sim.state.z, int(result == 0))
                            self.assertEqual((sim.state.n, sim.state.pg, sim.state.link,
                                              sim.state.inte, sim.state.h, sim.state.t), preserved)
                            self.assertEqual(asdict(sim.memory), memory)
                            self.assertEqual([(row.phase, row.timing) for row in trace],
                                             [(phase, timing) for phase in range(3) for timing in range(8)])
                            self.assertTrue(all(not ({24, 25, 26, 27} & set(row.mops)) for row in trace[8:]))

    def test_and_source_capture_alu_and_x_write_landmarks(self):
        sim = machine(0xB3)
        sim.state.registers[3], sim.state.registers[7] = 0xF0, 0x0F
        trace = sim.run_instruction()
        self.assertEqual(trace[8].mops, (20, 21))
        self.assertEqual(trace[9].mops, (20, 21, 23))
        self.assertEqual(trace[13].start.after.br, 0x0F)
        self.assertEqual(trace[18].start.after.z, 1)  # Still the initial flag.
        self.assertEqual((trace[19].start.after.br, trace[19].start.after.z), (0, 1))
        self.assertEqual(trace[19].start.signals.zero_source, 'alu')
        self.assertEqual(trace[19].start.after.registers[7], 0x0F)
        self.assertEqual(trace[20].start.after.registers[7], 0)

    def test_inr_uses_held_di_without_f1_buffer_capture(self):
        sim = machine(0x83)
        sim.state.registers[3] = 255
        sim.state.z = 0
        trace = sim.run_instruction()
        self.assertNotIn(2, trace[13].mops)
        self.assertEqual(trace[13].start.after.br, 0x21)
        self.assertEqual(trace[18].start.after.z, 0)
        self.assertEqual((trace[19].start.after.br, trace[19].start.after.z), (0, 1))
        self.assertEqual(trace[19].start.after.registers[3], 255)
        self.assertEqual(trace[22].start.after.registers[3], 0)

    def test_dcr_feedback_captures_once_then_zero_tests_final_di(self):
        sim = machine(0xA3)
        sim.state.registers[3] = 1
        sim.state.z = 0
        trace = sim.run_instruction()
        self.assertEqual(trace[13].start.after.br, 1)
        self.assertEqual(trace[16].start.signals.di, 254)
        self.assertEqual(trace[19].start.signals.alu, 255)
        self.assertEqual(trace[19].start.after.br, 255)
        # BR changed, so the combinational feedback changes at the end,
        # but that endpoint must not clock another increment into BR.
        self.assertEqual(trace[19].end.signals.alu, 1)
        self.assertEqual(trace[19].end.after.br, 255)
        self.assertEqual(trace[21].end.after.z, 0)
        self.assertEqual(trace[22].start.signals.zero_source, 'di')
        self.assertEqual((trace[22].start.after.registers[3], trace[22].start.after.z), (0, 1))

    def test_unknown_operands_fail_before_an_arithmetic_write(self):
        cases = ((0xB3, 7, 13), (0xB3, 3, 19), (0x83, 3, 19), (0xA3, 3, 13))
        for opcode, register, failure_slot in cases:
            sim = machine(opcode)
            sim.state.registers[register] = None
            for _ in range(failure_slot):
                sim.step()
            before = deepcopy(sim.state)
            with self.assertRaises(ModelError):
                sim.step()
            self.assertEqual(sim.state, before)
            self.assertEqual(len(sim.trace), failure_slot)
            sim.state.registers[register] = 0
            sim.step()

    def test_actual_next_fetch_when_result_overwrites_active_pc(self):
        for opcode, n, pc, source, target in ((0x80, 0, 0x20, None, 0x22),
                                            (0xA0, 0, 0x20, None, 0x20),
                                            (0xB3, 7, 0x21, 0xF0, 0x20)):
            sim = machine(opcode, n=n, pc=pc)
            if source is not None:
                sim.state.registers[3] = source
            sim.run_instruction()
            self.assertEqual(sim.state.registers[n], target)
            sim.memory.program[(1 << 8) | target] = 0
            trace = sim.run_instruction()
            self.assertEqual(trace[6].instruction, 'NOP')
            self.assertEqual(sim.state.registers[n], (target + 1) & 255)

    def test_arithmetic_zero_flag_drives_both_branch_polarities(self):
        for opcode in (0x83, 0xA3, 0xB3):
            for value in (0, 1, 255):
                for desired in (0, 1):
                    sim = machine(opcode)
                    sim.state.registers[3] = value
                    sim.state.registers[7] = 0x0F
                    result = ((value + 1) & 255 if opcode == 0x83 else
                              (value - 1) & 255 if opcode == 0xA3 else value & 0x0F)
                    sim.memory.program.update({0x121: 0xE1 | (desired << 3), 0x122: 0x80})
                    sim.run_instruction()
                    branch = sim.run_instruction()
                    taken = int(result == 0) == desired
                    self.assertEqual(branch[-2].branch_taken, taken)
                    self.assertEqual(sim.state.registers[0], 0x80 if taken else 0x23)

    def test_small_delay_loop_matches_book_structure(self):
        # Figure 8.5 structure, shortened initial values for a tractable test.
        sim = machine(0x23)  # LRI R3,#FE.
        sim.memory.program.update({
            0x121: 0xFE, 0x122: 0x24, 0x123: 2,  # LRI R4,#2.
            0x124: 0x83, 0x125: 0xE1, 0x126: 0x24,  # INR R3; BZ0 loop.
            0x127: 0xA4, 0x128: 0xE1, 0x129: 0x24,  # DCR R4; BZ0 loop.
            0x12A: 0,
        })
        instruction_count = 0
        while sim.state.registers[0] != 0x2A:
            sim.run_instruction()
            instruction_count += 1
            self.assertLess(instruction_count, 600)
        self.assertEqual(sim.state.registers[3:5], [0, 0])
        self.assertEqual(sim.state.z, 1)
        self.assertEqual(instruction_count, 522)
        self.assertEqual(len(sim.trace), 10432)

    def test_book_style_delay_subroutine_returns_to_caller(self):
        sim = machine(0x0C)  # JSR 80.
        sim.memory.program.update({
            0x121: 0x80, 0x122: 0,
            0x180: 0x23, 0x181: 0xFE,  # LRI R3,#FE.
            0x182: 0x24, 0x183: 1,     # LRI R4,#1.
            0x184: 0x83, 0x185: 0xE1, 0x186: 0x84,
            0x187: 0xA4, 0x188: 0xE1, 0x189: 0x84,
            0x18A: 0x0F,                # RSR.
        })
        for _ in range(11):
            sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 1, 0x23))
        self.assertEqual(sim.state.registers[3:5], [0, 0])
        self.assertEqual(len(sim.trace), 200)

    def test_demo_combines_alu_zero_flags_and_branches(self):
        from cmc8.__main__ import arithmetic_demo

        sim = arithmetic_demo()
        self.assertEqual(len(sim.trace), 160)
        self.assertEqual(sim.state.registers[3:5], [0xF0, 0xFF])
        self.assertEqual((sim.state.registers[7], sim.state.z), (0, 0))
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 1, 0x61))
        samples = [(row.instruction, row.start.signals.zero_source, row.start.signals.zero_value)
                   for row in sim.trace if 32 in row.mops]
        self.assertEqual(samples, [('AND', 'alu', 0), ('INR', 'alu', 0), ('DCR', 'di', 255)])

    def test_every_previous_opcode_preserves_trace_and_memory(self):
        catalogue, _ = load_data()
        for opcode, name in validate(catalogue).items():
            if name not in PREVIOUS_SEQUENCES:
                continue
            with self.subTest(opcode=opcode):
                current = machine(opcode)
                current.test_inputs = (0, 0, 0, 0)
                current.state.registers[7] = 0x80
                current.memory.program.update({0x121: 0x80, 0x180: 0xA6})
                current.memory.storage[0x180] = 0x69
                current.memory.devices[0x80] = 0x5A
                previous = PreviousSimulator(PreviousState(**asdict(current.state)),
                                             PreviousMemory(**asdict(current.memory)),
                                             test_inputs=current.test_inputs)
                actual = [asdict(row) for row in current.run_instruction()]
                expected = [asdict(row) for row in previous.run_instruction()]
                self.assertEqual(without_new_metadata(actual), without_new_metadata(expected))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])


if __name__ == '__main__':
    unittest.main()
