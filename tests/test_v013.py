"""Shift paths, simultaneous Link capture, aliases and serial/branch programs."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v013 import InstructionSimulator, Memory, ModelError, Simulator, State, evaluate
from cmc8.versions.v013.sequences import SEQUENCES, decode
from cmc8.versions.v012 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v012 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v012.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


def machine(opcode, *, n=0, page=1, pc=0x20, link=0, z=1):
    state = State(n=n, pg=page, link=link, z=z, inte=0, h=0, t=1)
    state.registers = [0x90 + index for index in range(8)]
    state.registers[n] = pc
    return InstructionSimulator(state, Memory(program={(page << 8) | pc: opcode}))


def expected_shift(name, value, link):
    if name == 'ROR':
        return (value >> 1) | ((value & 1) << 7), link
    if name == 'SHR':
        return value >> 1, link
    return (value >> 1) | (link << 7), value & 1


def without_new_metadata(value):
    if isinstance(value, dict):
        return {key: without_new_metadata(item) for key, item in value.items()
                if key not in {'version', 'shift_in', 'link_input'}}
    if isinstance(value, (list, tuple)):
        return [without_new_metadata(item) for item in value]
    return value


class ShiftDatapathTests(unittest.TestCase):
    def test_alu_pass_through_does_not_add_stale_br(self):
        state = State(ir=0x9B, br=0xEF, link=0)
        state.registers[3] = 0x81
        signals = evaluate(state, (19, 21, 7, 11, 12, 33))
        self.assertEqual((signals.alu, signals.mux, signals.link_input), (0x81, 0x40, 1))
        self.assertEqual(signals.writes, {'link': 1, 'br': 0x40})

    def test_all_high_bit_sources_and_every_byte_link_combination(self):
        for high_source, name in ((13, 'ROR'), (43, 'SHR'), (57, 'SHR'), (33, 'RRL')):
            for value in range(256):
                for link in (0, 1):
                    state = State(ir=0x9B, link=link)
                    state.registers[3] = value
                    signals = evaluate(state, (19, 21, 7, 11, 12, high_source))
                    result, expected_link = expected_shift(name, value, link)
                    self.assertEqual(signals.mux, result)
                    self.assertEqual(signals.shift_in, result >> 7)
                    if name == 'RRL':
                        self.assertEqual(signals.writes['link'], expected_link)
                    else:
                        self.assertNotIn('link', signals.writes)

    def test_old_link_is_used_before_new_link_and_end_sample_does_not_capture_again(self):
        state = State(ir=0x9B, link=0)
        state.registers[3] = 1
        cpu = Simulator(state)
        controls = (19, 21, 7, 11, 12, 33)
        start = cpu.capture(controls, point='start')
        self.assertEqual((start.after.br, start.after.link), (0, 1))
        self.assertEqual((start.signals.shift_in, start.signals.link_input), (0, 1))
        end = cpu.capture(controls, point='end')
        self.assertEqual(end.signals.mux, 0x80)  # Combinational path now sees new Link.
        self.assertEqual((end.after.br, end.after.link), (0, 1))

    def test_link_unknown_is_not_needed_for_ror_or_shr(self):
        state = State(ir=0x9B, link=None)
        state.registers[3] = 0x81
        for source, result in ((13, 0xC0), (43, 0x40), (57, 0x40)):
            self.assertEqual(evaluate(state, (19, 21, 7, 11, 12, source)).mux, result)
        self.assertIsNone(evaluate(state, (19, 21, 7, 11, 12, 33)).mux)
        self.assertIsNone(evaluate(state, (19, 21, 7, 11, 12)).mux)

    def test_source_conflicts_and_link_update_conflicts_are_rejected(self):
        state = State(ir=0x9B, link=0)
        state.registers[3] = 1
        for extra in ((13, 33), (13, 43), (33, 57), (43, 57), (33, 34), (33, 35)):
            with self.subTest(extra=extra), self.assertRaises(ModelError):
                evaluate(state, (19, 21, 7, 11, 12, *extra))


class ShiftInstructionTests(unittest.TestCase):
    def test_decoder_matches_entire_repertory(self):
        catalogue, _ = load_data()
        encodings = validate(catalogue)
        count = 0
        for opcode in range(256):
            if encodings.get(opcode) in SEQUENCES:
                self.assertEqual(decode(opcode), encodings[opcode])
                count += 1
            else:
                with self.assertRaises(ValueError):
                    decode(opcode)
        self.assertEqual((len(SEQUENCES), count), (40, 229))

    def test_every_byte_both_link_values_and_both_zero_flags(self):
        for base, name in ((0x88, 'ROR'), (0x90, 'SHR'), (0x98, 'RRL')):
            for value in range(256):
                for link in (0, 1):
                    for z in (0, 1):
                        sim = machine(base | 3, link=link, z=z)
                        sim.state.registers[3] = value
                        result, expected_link = expected_shift(name, value, link)
                        trace = sim.run_instruction()
                        self.assertEqual((sim.state.registers[3], sim.state.link, sim.state.z),
                                         (result, expected_link, z))
                        self.assertEqual(sim.state.registers[0], 0x21)
                        self.assertEqual(len(trace), 16)

    def test_all_register_pc_x_aliases_and_pages(self):
        for base, name in ((0x88, 'ROR'), (0x90, 'SHR'), (0x98, 'RRL')):
            for n in range(8):
                for a in range(8):
                    for page in range(4):
                        for pc in (0x20, 0xFF):
                            link = (n + a + page) & 1
                            sim = machine(base | a, n=n, page=page, pc=pc, link=link)
                            expected = list(sim.state.registers)
                            expected[n] = (pc + 1) & 255
                            expected[a], expected_link = expected_shift(name, expected[a], link)
                            memory = asdict(sim.memory)
                            trace = sim.run_instruction()
                            self.assertEqual(sim.state.registers, expected)
                            self.assertEqual((sim.state.n, sim.state.pg, sim.state.z, sim.state.inte,
                                              sim.state.h, sim.state.t), (n, page, 1, 0, 0, 1))
                            self.assertEqual(sim.state.link, expected_link)
                            self.assertEqual(asdict(sim.memory), memory)
                            self.assertEqual([(row.phase, row.timing) for row in trace[8:]],
                                             [(1, 0), (1, 1)] + [(2, timing) for timing in range(2, 8)])

    def test_rrl_corrected_phase_skip_shift_and_writeback_landmarks(self):
        sim = machine(0x9B, link=1)
        sim.state.registers[3] = 2
        trace = sim.run_instruction()
        self.assertEqual(trace[9].mops, (19, 21, 23, 31))
        self.assertEqual(trace[9].start.after.phase, 2)
        self.assertEqual(trace[10].mops, (19, 21, 7, 11, 12, 33))
        self.assertEqual((trace[10].start.after.br, trace[10].start.after.link), (0x81, 0))
        self.assertEqual(trace[10].start.after.registers[3], 2)
        self.assertEqual(trace[13].mops, (4,))
        self.assertEqual(trace[13].start.signals.di, 0x81)
        self.assertEqual(trace[14].mops, (19, 22, 4))
        self.assertEqual(trace[14].start.after.registers[3], 0x81)
        self.assertTrue(all(not ({24, 25, 26, 27} & set(row.mops)) for row in trace[8:]))
        self.assertTrue(all(32 not in row.mops for row in trace))

    def test_no_operand_or_external_execute_read(self):
        for opcode in (0x8B, 0x93, 0x9B):
            sim = machine(opcode)
            sim.memory.program_delay = 4  # Opcode reaches transparent IR by end T5.
            sim.run_instruction()
            self.assertEqual(sim.state.registers[0], 0x21)

    def test_unknown_source_or_link_rolls_back_shift_capture(self):
        for opcode, source in ((0x8B, 'register'), (0x93, 'register'),
                               (0x9B, 'register'), (0x9B, 'link')):
            sim = machine(opcode)
            if source == 'register':
                sim.state.registers[3] = None
            else:
                sim.state.link = None
            for _ in range(10):
                sim.step()
            before = deepcopy(sim.state)
            with self.assertRaisesRegex(ModelError, 'ALU/MUX result'):
                sim.step()
            self.assertEqual(sim.state, before)
            self.assertEqual(len(sim.trace), 10)
            if source == 'register':
                sim.state.registers[3] = 0
            else:
                sim.state.link = 0
            sim.step()

    def test_unknown_link_is_preserved_by_ror_and_shr(self):
        for opcode in (0x8B, 0x93):
            sim = machine(opcode, link=None)
            sim.run_instruction()
            self.assertIsNone(sim.state.link)

    def test_actual_next_fetch_after_shifting_active_pc(self):
        for opcode, link, target in ((0x88, 0, 0x90), (0x90, 1, 0x10), (0x98, 1, 0x90)):
            sim = machine(opcode, link=link)
            sim.run_instruction()
            self.assertEqual(sim.state.registers[0], target)
            sim.memory.program[0x100 | target] = 0
            sim.run_instruction()
            self.assertEqual(sim.state.registers[0], target + 1)

    def test_rrl_link_is_consumed_by_both_branch_polarities(self):
        for value in (0, 1, 2, 255):
            for desired in (0, 1):
                sim = machine(0x9B, link=1 - (value & 1))
                sim.state.registers[3] = value
                sim.memory.program.update({0x121: 0xE5 | (desired << 3), 0x122: 0x80})
                sim.run_instruction()
                trace = sim.run_instruction()
                taken = value & 1 == desired
                self.assertEqual(trace[-2].branch_taken, taken)
                self.assertEqual(sim.state.registers[0], 0x80 if taken else 0x23)

    def test_sel_rel_deferred_effect_is_shifted_in_then_replaced_by_output_bit(self):
        for flag, old_link, incoming in ((5, 0, 1), (4, 1, 0)):
            sim = machine(flag, link=old_link)
            sim.state.registers[3] = 1 - incoming
            sim.memory.program[0x121] = 0x9B
            sim.run_instruction()
            self.assertEqual(sim.state.link, old_link)
            trace = sim.run_instruction()
            self.assertEqual(trace[2].start.after.link, incoming)
            self.assertEqual(trace[10].start.signals.shift_in, incoming)
            self.assertEqual(sim.state.link, 1 - incoming)
            self.assertEqual(sim.state.registers[3], incoming << 7)

    def test_eight_rotations_emit_all_source_bits_and_nine_restore_nine_bit_state(self):
        for value in range(256):
            for link in (0, 1):
                sim = machine(0x9B, link=link)
                sim.state.registers[3] = value
                sim.memory.program.update({0x120 + i: 0x9B for i in range(9)})
                emitted = []
                for _ in range(8):
                    sim.run_instruction()
                    emitted.append(sim.state.link)
                self.assertEqual(emitted, [(value >> bit) & 1 for bit in range(8)])
                sim.run_instruction()
                self.assertEqual((sim.state.registers[3], sim.state.link), (value, link))

    def test_shr_then_bit_branch_matches_key_classification_structure(self):
        # p.154's two SHR/BB0 stages classify command-code bits 1 and 2.
        for command in (0o361, 0o363, 0o365, 0o367):
            sim = machine(0x96)
            sim.state.registers[6] = command
            sim.memory.program.update({
                0x121: 0xD6, 0x122: 0x80,
                0x123: 0x96, 0x124: 0xD6, 0x125: 0x90,
            })
            sim.run_instruction()
            sim.run_instruction()
            if command & 2 == 0:
                self.assertEqual(sim.state.registers[0], 0x80)
            else:
                sim.run_instruction()
                sim.run_instruction()
                self.assertEqual(sim.state.registers[0], 0x90 if command & 4 == 0 else 0x26)

    def test_test_input_sel_rel_and_rrl_receive_a_serial_byte(self):
        # p.107 describes setting Link from a test input before each RRL.
        # Unroll eight short BT/SEL/REL paths, with input bits supplied LSB first.
        for value in (0, 255, 0xA6, 0x55):
            sim = machine(0xC8, link=None)
            sim.state.registers[3] = 0xCC
            for bit in range(8):
                base = 0x20 + 7 * bit
                sim.memory.program.update({
                    0x100 | base: 0xC8, 0x100 | (base + 1): base + 5,  # BT1 T0.
                    0x100 | (base + 2): 4,                             # REL.
                    0x100 | (base + 3): 0xF1, 0x100 | (base + 4): base + 6,
                    0x100 | (base + 5): 5,                             # SEL.
                    0x100 | (base + 6): 0x9B,                          # RRL R3.
                })
            for bit in range(8):
                sim.test_inputs = ((value >> bit) & 1, None, None, None)
                end = 0x20 + 7 * (bit + 1)
                count = 0
                while sim.state.registers[0] != end:
                    sim.run_instruction()
                    count += 1
                    self.assertLessEqual(count, 4)
            self.assertEqual(sim.state.registers[3], value)
            self.assertEqual(sim.state.z, 1)

    def test_eight_ror_restore_byte_and_eight_shr_clear_it(self):
        for value in (0, 1, 0x80, 0xA6, 255):
            for opcode in (0x8B, 0x93):
                sim = machine(opcode, link=1)
                sim.state.registers[3] = value
                sim.memory.program.update({0x120 + index: opcode for index in range(8)})
                for _ in range(8):
                    sim.run_instruction()
                self.assertEqual(sim.state.registers[3], value if opcode == 0x8B else 0)
                self.assertEqual(sim.state.link, 1)

    def test_every_previous_opcode_retains_trace_and_memory(self):
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
                self.assertEqual(without_new_metadata([asdict(row) for row in current.run_instruction()]),
                                 without_new_metadata([asdict(row) for row in previous.run_instruction()]))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])

    def test_demo_exercises_all_three_shifts_and_link_branch(self):
        from cmc8.__main__ import shift_demo

        sim = shift_demo()
        self.assertEqual(len(sim.trace), 128)
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (1, 0x41))
        self.assertEqual(sim.state.registers[3:5], [0xB0, 0])
        self.assertEqual((sim.state.link, sim.state.z), (1, 0))
        shifts = [(row.instruction, row.start.signals.shift_in, row.start.signals.link_input)
                  for row in sim.trace if 11 in row.mops]
        self.assertEqual(shifts, [('ROR', 1, None), ('SHR', 0, None),
                                  ('RRL', 1, 0), ('RRL', 0, 1)])


if __name__ == '__main__':
    unittest.main()
