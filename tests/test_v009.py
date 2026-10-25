"""Branch circuit truth tables, bus timing and executable program checks."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v009 import InstructionSimulator, Memory, ModelError, Simulator, State, evaluate
from cmc8.versions.v009.sequences import BRANCHES, SEQUENCES, decode
from cmc8.versions.v008.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from cmc8.versions.v008 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v008 import Memory as PreviousMemory, State as PreviousState
from tools.build_instruction_reference import load_data, validate


def machine(opcode, *, pc=0x20, n=0, page=1, target=0x80, link=0, z=0,
            registers=None, test_inputs=(None, None, None, None)):
    state = State(n=n, pg=page, link=link, z=z, inte=0)
    state.registers = list(registers) if registers is not None else [0x90 + i for i in range(8)]
    state.registers[n] = pc
    program = {(page << 8) | pc: opcode,
               (page << 8) | ((pc + 1) & 255): target}
    return InstructionSimulator(state, Memory(program=program), test_inputs=test_inputs)


class BranchCircuitTests(unittest.TestCase):
    def test_physical_h_xor_and_inverted_write_condition(self):
        for selector, name in ((51, 'z'), (52, 'link'), (53, 'test'), (54, 'di')):
            for level in (0, 1):
                for desired in (0, 1):
                    state = State(ir=0xD3 | (desired << 3), timing=2, z=level, link=level)
                    state.registers[3] = 0xA0 | level
                    mops = (selector, 55, 19, 21) if selector == 54 else (selector, 55)
                    cpu = Simulator(state)
                    row = cpu.capture(mops, test_inputs=(None, None, None, level))
                    self.assertEqual(row.signals.condition_source, level)
                    self.assertEqual(row.after.h, level ^ desired)
                    self.assertEqual(row.after.h == 0, level == desired)
                    if selector == 53:
                        self.assertEqual(row.after.t, level)

    def test_ambiguous_missing_or_mistimed_condition_is_rejected(self):
        state = State(ir=0xE0, timing=2, z=0)
        for controls in ((51, 52, 55), (55,), (54, 55)):
            with self.subTest(controls=controls), self.assertRaises(ModelError):
                evaluate(state, controls)
        state.timing = 1
        with self.assertRaisesRegex(ModelError, 'only at T2'):
            evaluate(state, (51, 55))
        for pins in ((0, 1), (0, 0, 0, 2), (False, 0, 0, 0)):
            with self.assertRaisesRegex(ModelError, 'four logical bits'):
                evaluate(State(), (), test_inputs=pins)

    def test_end_observation_does_not_recapture_h(self):
        cpu = Simulator(State(ir=0xE0, timing=2, z=0))
        cpu.capture((51, 55), point='start')
        cpu.state.z = 1
        row = cpu.capture((51, 55), point='end')
        self.assertEqual(row.signals.h_input, 1)
        self.assertEqual(row.after.h, 0)


class BranchInstructionTests(unittest.TestCase):
    def test_decoder_matches_entire_independent_repertory(self):
        catalogue, _ = load_data()
        encodings = validate(catalogue)
        supported = 0
        for opcode in range(256):
            if encodings.get(opcode) in SEQUENCES:
                self.assertEqual(decode(opcode), encodings[opcode])
                supported += 1
            else:
                with self.assertRaises(ValueError):
                    decode(opcode)
        self.assertEqual(supported, 141)
        self.assertEqual(len(SEQUENCES), 29)

    def test_flag_branches_all_pc_selectors_pages_and_polarities(self):
        for base, flag in ((0xE0, 'z'), (0xE4, 'link')):
            for desired in (0, 1):
                for level in (0, 1):
                    for n in range(8):
                        for page in range(4):
                            for target_page in range(4):
                                target = (0, 0x80, 0xFF)[(n + page + target_page) % 3]
                                sim = machine(base | (desired << 3) | target_page,
                                              n=n, page=page, target=target, **{flag: level})
                                expected = list(sim.state.registers)
                                taken = level == desired
                                expected[n] = target if taken else 0x22
                                trace = sim.run_instruction()
                                self.assertEqual(sim.state.registers, expected)
                                self.assertEqual(sim.state.pg, target_page if taken else page)
                                self.assertEqual((sim.state.n, sim.state.link, sim.state.z, sim.state.inte),
                                                 (n, level if flag == 'link' else 0,
                                                  level if flag == 'z' else 0, 0))
                                self.assertEqual(len(trace), 16)
                                self.assertEqual(trace[-2].branch_taken, taken)
                                self.assertEqual(sim.state.h, int(not taken))

    def test_bb_all_byte_values_and_both_polarities(self):
        for desired in (0, 1):
            for value in range(256):
                registers = [0x80] * 8
                registers[3] = value
                sim = machine(0xD3 | (desired << 3), registers=registers)
                trace = sim.run_instruction()
                taken = (value & 1) == desired
                self.assertEqual(sim.state.registers[0], 0x80 if taken else 0x22)
                self.assertEqual(sim.state.registers[3], value)
                self.assertEqual(sim.state.pg, 1)
                self.assertEqual(len(trace), 24)
                self.assertEqual(trace[18].start.signals.condition_source, value & 1)
                self.assertEqual(trace[-2].branch_taken, taken)

    def test_bb_register_alias_uses_pc_after_both_bytes(self):
        for n in range(8):
            for a in range(8):
                for pc in (0x20, 0x21, 0xFE, 0xFF):
                    sim = machine(0xD0 | a, n=n, pc=pc)
                    source = ((pc + 2) & 255) if a == n else sim.state.registers[a]
                    expected = list(sim.state.registers)
                    expected[n] = 0x80 if source & 1 == 0 else (pc + 2) & 255
                    sim.run_instruction()
                    self.assertEqual(sim.state.registers, expected)

    def test_test_branches_select_pin_without_selecting_page_or_pc_bank(self):
        for desired in (0, 1):
            for pin in range(4):
                for level in (0, 1):
                    for page in range(4):
                        pins = [1 - level] * 4
                        pins[pin] = level
                        sim = machine(0xC0 | (desired << 3) | pin, page=page, n=5,
                                      test_inputs=pins)
                        trace = sim.run_instruction()
                        self.assertEqual((sim.state.pg, sim.state.n), (page, 5))
                        self.assertEqual(sim.state.t, level)
                        self.assertEqual(sim.state.registers[5], 0x80 if level == desired else 0x22)
                        self.assertEqual(len(trace), 16)

    def test_two_cycle_fetch_increment_and_conditional_write_landmarks(self):
        for z in (0, 1):
            sim = machine(0xE2, z=z)
            trace = sim.run_instruction()
            self.assertEqual([(r.phase, r.timing) for r in trace[8:]],
                             [(1, 0), (1, 1)] + [(2, t) for t in range(2, 8)])
            self.assertEqual(trace[10].start.after.h, z)
            self.assertEqual(trace[12].start.after.registers[0], 0x22)
            self.assertEqual(trace[13].start.after.br, 0x80)
            self.assertEqual(trace[13].start.after.pg, 1)
            self.assertEqual([r.timing for r in trace[8:] if 24 in r.mops], [2, 3, 4, 5])
            self.assertEqual(22 in trace[14].mops, z == 0)
            self.assertEqual(15 in trace[14].mops, z == 0)
            self.assertEqual(sim.state.ab, 0x21)
            self.assertEqual(asdict(sim.memory), asdict(Memory(program={0x120: 0xE2, 0x121: 0x80})))

    def test_bb_functional_correction_and_no_operand_address_preload(self):
        sim = machine(0xD3)
        trace = sim.run_instruction()
        self.assertIn(4, trace[12].mops)
        self.assertNotIn(6, trace[12].mops)
        self.assertEqual(trace[12].start.after.registers[0], 0x22)
        self.assertEqual(trace[13].start.after.br, 0x80)
        self.assertEqual(trace[14].start.after.ab, 0x21)
        self.assertEqual(trace[18].mops, (19, 21, 54, 55))
        self.assertNotIn(22, trace[22].mops)  # R3=93, BB0 untaken.

    def test_condition_is_sampled_at_t2_and_retained_until_t6(self):
        for opcode, sample_index, name in ((0xE0, 10, 'z'), (0xD3, 18, 'register'), (0xC1, 10, 'pin')):
            sim = machine(opcode, z=1, test_inputs=(None, 1, None, None))
            for _ in range(sample_index):
                sim.step()
            if name == 'z': sim.state.z = 0
            elif name == 'register': sim.state.registers[3] = 0
            else: sim.test_inputs = (None, 0, None, None)
            row = sim.step()
            self.assertEqual(row.start.after.h, 0)
            if name == 'z': sim.state.z = 1
            elif name == 'register': sim.state.registers[3] = 1
            else: sim.test_inputs = (None, 1, None, None)
            while (sim.state.phase, sim.state.timing) != (0, 0): sim.step()
            self.assertEqual(sim.state.registers[0], 0x80)
            self.assertTrue(sim.trace[-2].branch_taken)

    def test_unknown_condition_rolls_back_and_can_be_supplied_before_retry(self):
        for opcode, sample_index, source in ((0xE0, 10, 'z'), (0xD3, 18, 'register'), (0xC0, 10, 'pin')):
            sim = machine(opcode, z=None)
            if source == 'register': sim.state.registers[3] = None
            for _ in range(sample_index): sim.step()
            before, memory = deepcopy(sim.state), asdict(sim.memory)
            with self.assertRaisesRegex(ModelError, 'known condition'):
                sim.step()
            self.assertEqual(sim.state, before)
            self.assertEqual(asdict(sim.memory), memory)
            self.assertEqual(len(sim.trace), sample_index)
            if source == 'z': sim.state.z = 0
            elif source == 'register': sim.state.registers[3] = 0
            else: sim.test_inputs = (0, None, None, None)
            sim.step()
            self.assertEqual(sim.state.h, 0)

    def test_operand_read_is_required_even_when_branch_will_not_be_taken(self):
        sim = machine(0xE0, z=1)
        del sim.memory.program[0x121]
        for _ in range(13): sim.step()
        with self.assertRaisesRegex(ModelError, 'DB is not valid'):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 5))
        self.assertEqual(sim.state.registers[0], 0x22)

    def test_operand_must_be_ready_at_start_of_t5(self):
        for opcode, sample_index in ((0xE0, 13), (0xC0, 13), (0xD3, 13)):
            sim = machine(opcode, test_inputs=(0, None, None, None))
            sim.memory.program_delay = 4
            for _ in range(sample_index):
                sim.step()
            with self.assertRaisesRegex(ModelError, 'start of T5'):
                sim.step()
            sim.memory.program_delay = 3
            sim.step()
            self.assertEqual(sim.state.br, 0x80)

    def test_consecutive_branches_resample_h(self):
        sim = machine(0xE1, z=0)
        sim.memory.program.update({0x180: 0xE9, 0x181: 0xA0, 0x182: 0})
        sim.run_instruction()  # BZ0 taken.
        self.assertEqual(sim.state.h, 0)
        trace = sim.run_instruction()  # BZ1 untaken with unchanged Z.
        self.assertEqual(sim.state.h, 1)
        self.assertFalse(trace[-2].branch_taken)
        sim.run_instruction()
        self.assertEqual(sim.state.registers[0], 0x83)

    def test_pc_wrap_stays_on_source_page_until_a_taken_page_branch(self):
        for opcode in (0xD3, 0xC2, 0xE0):
            for pc in (0xFE, 0xFF):
                for taken in (False, True):
                    sim = machine(opcode, pc=pc, z=int(not taken),
                                  test_inputs=(None, None, int(not taken), None))
                    sim.state.registers[3] = int(not taken)
                    sim.run_instruction()
                    self.assertEqual(sim.state.registers[0], 0x80 if taken else (pc + 2) & 255)
                    self.assertEqual(sim.state.pg, 0 if taken and opcode == 0xE0 else 1)

    def test_deferred_flag_instructions_feed_next_branch(self):
        for flag_opcode, flag_name, new_value, base in ((5, 'link', 1, 0xE4), (4, 'link', 0, 0xE4),
                                                       (7, 'z', 1, 0xE0), (6, 'z', 0, 0xE0)):
            for desired in (0, 1):
                sim = machine(flag_opcode, **{flag_name: 1 - new_value})
                sim.memory.program.update({0x121: base | (desired << 3) | 1, 0x122: 0x80})
                sim.run_instruction()
                self.assertEqual(getattr(sim.state, flag_name), 1 - new_value)
                trace = sim.run_instruction()
                self.assertEqual(getattr(sim.state, flag_name), new_value)
                self.assertEqual(trace[2].flag_effect.name, decode(flag_opcode))
                self.assertEqual(sim.state.registers[0], 0x80 if desired == new_value else 0x23)

    def test_actual_next_fetch_for_taken_and_untaken_page_branch(self):
        for z in (0, 1):
            sim = machine(0xE2, z=z)
            sim.memory.program.update({0x280: 0, 0x122: 0, 0x180: 1, 0x222: 1})
            sim.run_instruction()
            trace = sim.run_instruction()
            self.assertEqual(trace[6].instruction, 'NOP')
            self.assertEqual((sim.state.pg, sim.state.registers[0]), (2, 0x81) if z == 0 else (1, 0x23))

    def test_stale_h_does_not_write_pc_during_nop(self):
        sim = machine(0xD3)
        sim.state.registers[3] = 0
        sim.memory.program[0x180] = 0
        sim.run_instruction()
        self.assertEqual(sim.state.h, 0)
        trace = sim.run_instruction()
        self.assertNotIn(22, trace[6].mops)
        self.assertEqual(sim.state.registers[0], 0x81)

    def test_previous_static_sequences_are_preserved(self):
        for name, sequence in PREVIOUS_SEQUENCES.items():
            self.assertEqual(SEQUENCES[name], sequence, name)
        self.assertEqual(set(SEQUENCES) - set(PREVIOUS_SEQUENCES), BRANCHES)

    def test_previous_instruction_traces_and_memory_are_preserved(self):
        def common_fields(value):
            if isinstance(value, dict):
                return {key: common_fields(item) for key, item in value.items()
                        if key not in {'version', 'h', 't', 'condition_source', 'h_input', 'branch_taken'}}
            if isinstance(value, (list, tuple)):
                return [common_fields(item) for item in value]
            return value

        opcodes = [0, 2, 3, 4, 5, 6, 7, 0x53, 0x73, 0x43, 0x63, 0x13,
                   0x1B, 0x4B, 0x5B, 0x6B, 0x7B, 0xF2, 0xFB, 0x0C, 0x0F]
        for opcode in opcodes:
            with self.subTest(opcode=opcode):
                current = machine(opcode)
                current.state.registers[7] = 0x80
                current.memory.program[0x180] = 0xA6
                current.memory.storage[0x180] = 0xA6
                current.memory.devices[0x80] = 0xA6
                old_state = common_fields(asdict(current.state))
                previous = PreviousSimulator(PreviousState(**old_state),
                                             PreviousMemory(**asdict(current.memory)))
                current_trace = current.run_instruction()
                previous_trace = previous.run_instruction()
                self.assertEqual(common_fields([asdict(row) for row in current_trace]),
                                 common_fields([asdict(row) for row in previous_trace]))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))

    def test_branch_demo_finishes_at_expected_location(self):
        from cmc8.__main__ import branch_demo

        sim = branch_demo()
        self.assertEqual(len(sim.trace), 96)
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 2, 0x81))
        outcomes = [(row.instruction, row.branch_taken) for row in sim.trace
                    if row.branch_taken is not None]
        self.assertEqual(outcomes, [('BL1', True), ('BZ0', False), ('BB0', True), ('BT1', True)])


if __name__ == '__main__':
    unittest.main()
