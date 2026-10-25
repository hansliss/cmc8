"""Source-derived jump landmarks and integration tests for call/return flow."""
from dataclasses import asdict
import unittest

from cmc8.versions.v007 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v007 import Memory as PreviousMemory
from cmc8.versions.v007 import State as PreviousState
from cmc8.versions.v008 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v008.sequences import decode


SKIPPED_EXECUTE_SLOTS = [(1, 0), (1, 1)] + [(2, t) for t in range(2, 8)]


def machine(program, *, n=0, page=0, pc=0x20, registers=None):
    state = State(n=n, pg=page, link=1, z=0, inte=0)
    state.registers = list(registers) if registers is not None else [0x90 + i for i in range(8)]
    state.registers[n] = pc
    memory = Memory(program=dict(program), storage={0x80: 0xA6}, devices={5: 0x69})
    return InstructionSimulator(state, memory)


def code_at(page, address, *values):
    return {(page << 8) | ((address + offset) & 255): value for offset, value in enumerate(values)}


class JumpTests(unittest.TestCase):
    def test_encodings_from_figure_5_1(self):
        for page in range(4):
            self.assertEqual(decode(0xF0 | page), 'JMP')
        for register in range(8):
            self.assertEqual(decode(0xF8 | register), 'JCR')
        self.assertEqual(decode(0o014), 'JSR')
        self.assertEqual(decode(0o017), 'RSR')
        self.assertEqual(decode(0o360), 'JMP')

    def test_jmp_all_pc_selectors_source_pages_target_pages_and_boundary_addresses(self):
        for n in range(8):
            for page in range(4):
                for target_page in range(4):
                    for target in (0, 0x80, 0xFF):
                        with self.subTest(n=n, page=page, target_page=target_page, target=target):
                            sim = machine(code_at(page, 0x20, 0xF0 | target_page, target), n=n, page=page)
                            registers = list(sim.state.registers)
                            registers[n] = target
                            memory = asdict(sim.memory)
                            trace = sim.run_instruction()
                            self.assertEqual(len(trace), 16)
                            self.assertEqual(sim.state.registers, registers)
                            self.assertEqual((sim.state.n, sim.state.pg), (n, target_page))
                            self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))
                            self.assertEqual((sim.state.link, sim.state.z, sim.state.inte), (1, 0, 0))
                            self.assertEqual(asdict(sim.memory), memory)
                            self.assertEqual([(r.phase, r.timing) for r in trace[8:]], SKIPPED_EXECUTE_SLOTS)

    def test_jmp_phase_and_transfer_landmarks_from_figure_5_3(self):
        sim = machine(code_at(2, 0x20, 0xF1, 0x80), page=2)
        trace = sim.run_instruction()
        self.assertEqual(trace[6].start.after.ab, 0x21)
        self.assertEqual((trace[9].phase, trace[9].timing, trace[9].mops), (1, 1, (31,)))
        self.assertEqual(trace[9].start.after.phase, 2)
        self.assertEqual((trace[10].phase, trace[10].timing), (2, 2))
        self.assertEqual(trace[13].start.after.br, 0x80)
        self.assertEqual(trace[13].start.after.pg, 2)  # Target read uses old page.
        self.assertEqual(trace[14].start.after.pg, 1)
        self.assertEqual(trace[14].start.after.registers[0], 0x80)
        self.assertEqual([r.timing for r in trace[8:] if 'PME' in r.start.signals.outputs], [2, 3, 4, 5])

    def test_jmp_fetches_the_destination_opcode_from_the_new_page(self):
        program = code_at(2, 0x20, 0xF1, 0x80)
        program[0x180] = 0  # NOP on destination page.
        program[0x280] = 1  # Invalid opcode if old PG is mistakenly used.
        sim = machine(program, page=2)
        sim.run_instruction()
        self.assertEqual(sim.state.ab, 0x21)  # Fig.6.7: still the operand address.
        trace = sim.run_instruction()
        self.assertEqual(trace[0].start.after.ab, 0x21)
        self.assertEqual(trace[1].start.after.ab, 0x80)
        self.assertEqual(len(trace), 8)
        self.assertEqual(trace[6].instruction, 'NOP')
        self.assertEqual(sim.state.registers[0], 0x81)

    def test_jmp_operand_fetch_wraps_within_the_original_page(self):
        sim = machine(code_at(3, 0xFF, 0xF0, 0x80), page=3, pc=0xFF)
        sim.run_instruction()
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (0, 0x80))

    def test_jump_address_must_arrive_at_start_of_t5(self):
        sim = machine(code_at(0, 0x20, 0xF0, 0x80))
        sim.memory.program_delay = 4
        for _ in range(13):
            sim.step()
        with self.assertRaisesRegex(ModelError, 'start of T5'):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 5))
        sim.memory.program_delay = 3
        sim.step()
        self.assertEqual(sim.state.br, 0x80)

    def test_jcr_all_register_aliases_pages_and_pc_wrap(self):
        for n in range(8):
            for a in range(8):
                for page in range(4):
                    for pc in (0x20, 0xFF):
                        with self.subTest(n=n, a=a, page=page, pc=pc):
                            registers = [0x30 + i for i in range(8)]
                            sim = machine(code_at(page, pc, 0xF8 | a), n=n, page=page, pc=pc, registers=registers)
                            expected = list(sim.state.registers)
                            expected[n] = (pc + 1) & 255
                            target = expected[a]
                            expected[n] = target
                            trace = sim.run_instruction()
                            self.assertEqual(len(trace), 16)
                            self.assertEqual(sim.state.registers, expected)
                            self.assertEqual((sim.state.pg, sim.state.n), (page, n))
                            self.assertTrue(all(not ({24,25,26} & set(r.mops)) for r in trace[8:]))
                            self.assertEqual(trace[13].start.after.br, target)

    def test_jcr_target_can_be_zero(self):
        sim = machine(code_at(0, 0x20, 0xFB))
        sim.state.registers[3] = 0
        sim.run_instruction()
        self.assertEqual(sim.state.registers[0], 0)

    def test_unknown_jcr_source_is_reported_without_committing_capture(self):
        sim = machine(code_at(0, 0x20, 0xFB))
        sim.state.registers[3] = None
        for _ in range(13):
            sim.step()
        with self.assertRaisesRegex(ModelError, 'DB is not valid'):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 5))
        self.assertEqual(sim.state.registers[0], 0x21)
        self.assertEqual(len(sim.trace), 13)
        sim.state.registers[3] = 0x80
        sim.step()
        self.assertEqual(sim.state.br, 0x80)


class SubroutineTests(unittest.TestCase):
    def test_jsr_and_rsr_all_pc_selectors_pages_and_wraps(self):
        for n in range(8):
            for page in range(4):
                for pc in (0x20, 0xFE, 0xFF):
                    with self.subTest(n=n, page=page, pc=pc):
                        target = 0x80
                        program = code_at(page, pc, 0x0C, target)
                        program[(page << 8) | target] = 0x0F
                        sim = machine(program, n=n, page=page, pc=pc)
                        before = list(sim.state.registers)
                        callee = (n + 1) & 7
                        call = sim.run_instruction()
                        self.assertEqual(len(call), 24)
                        self.assertEqual(sim.state.n, callee)
                        self.assertEqual(sim.state.registers[n], (pc + 2) & 255)
                        self.assertEqual(sim.state.registers[callee], target)
                        for index in range(8):
                            if index not in (n, callee):
                                self.assertEqual(sim.state.registers[index], before[index])
                        returned = sim.run_instruction()
                        self.assertEqual(len(returned), 16)
                        self.assertEqual(sim.state.n, n)
                        self.assertEqual(sim.state.registers[n], (pc + 2) & 255)
                        self.assertEqual(sim.state.registers[callee], target + 1)
                        self.assertEqual(sim.state.pg, page)

    def test_jsr_landmarks_from_figure_5_4(self):
        sim = machine(code_at(0, 0x20, 0x0C, 0x80))
        trace = sim.run_instruction()
        self.assertEqual(trace[12].start.after.registers[0], 0x22)
        self.assertEqual(trace[13].start.after.br, 0x80)
        self.assertEqual(trace[14].start.after.ab, 0x21)  # No invented target AB preload.
        self.assertEqual(trace[17].end.after.n, 0)
        self.assertEqual(trace[18].start.after.n, 1)
        self.assertEqual(trace[22].start.after.registers[1], 0x80)
        self.assertEqual(trace[22].start.after.registers[0], 0x22)

    def test_rsr_restores_old_pc_without_fetching_an_operand(self):
        sim = machine(code_at(1, 0x80, 0x0F), n=1, page=1, pc=0x80)
        sim.state.registers[0] = 0x22
        trace = sim.run_instruction()
        self.assertEqual([(r.phase,r.timing) for r in trace[8:]], SKIPPED_EXECUTE_SLOTS)
        self.assertEqual(trace[10].start.before.n, 1)
        self.assertEqual(trace[10].start.after.n, 0)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertEqual(sim.state.registers[1], 0x81)
        self.assertTrue(all(not ({24,25,26} & set(r.mops)) for r in trace[8:]))

    def test_nested_calls_return_to_each_saved_address(self):
        program = {0x20: 0x0C, 0x21: 0x40, 0x22: 0,
                   0x40: 0x0C, 0x41: 0x60, 0x42: 0x0F, 0x60: 0x0F}
        sim = machine(program)
        for expected_name, n, pc, length in [('JSR',1,0x40,24), ('JSR',2,0x60,24),
                                              ('RSR',1,0x42,16), ('RSR',0,0x22,16), ('NOP',0,0x23,8)]:
            trace = sim.run_instruction()
            self.assertEqual(trace[6].instruction, expected_name)
            self.assertEqual((sim.state.n, sim.state.registers[n]), (n, pc))
            self.assertEqual(len(trace), length)

    def test_cross_page_call_does_not_invent_a_page_stack(self):
        program = {0x20: 0x0C, 0x21: 0x40, 0x40: 0xF1, 0x41: 0x60, 0x160: 0x0F}
        sim = machine(program)
        sim.run_instruction()  # JSR on page 0, old PC = 22.
        sim.run_instruction()  # Callee JMP to page 1.
        sim.run_instruction()  # RSR changes N, not PG.
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 1, 0x22))

    def test_ein_then_rsr_matches_delayed_enable_without_implementing_interrupts(self):
        sim = machine({0x40: 3, 0x41: 0x0F}, n=1, pc=0x40)
        sim.state.registers[0] = 0x22
        sim.run_instruction()
        self.assertEqual(sim.state.inte, 0)
        trace = sim.run_instruction()
        self.assertEqual(trace[2].flag_effect.name, 'EIN')
        self.assertEqual(trace[2].start.after.inte, 1)
        self.assertEqual((sim.state.n, sim.state.registers[0], sim.state.inte), (0, 0x22, 1))

    def test_rsr_alone_does_not_enable_interrupts(self):
        sim = machine({0x40: 0x0F}, n=1, pc=0x40)
        sim.run_instruction()
        self.assertEqual(sim.state.inte, 0)
        self.assertTrue(all(row.flag_effect is None for row in sim.trace))

    def test_manual_stepping_matches_instruction_runs(self):
        code = {0x20: 0x0C, 0x21: 0x40, 0x40: 0x0F}
        manual, automatic = machine(code), machine(code)
        for _ in range(40):
            manual.step()
        automatic.run_instruction()
        automatic.run_instruction()
        self.assertEqual(asdict(manual.state), asdict(automatic.state))
        self.assertEqual([r.to_dict() for r in manual.trace], [r.to_dict() for r in automatic.trace])

    def test_previous_instructions_remain_identical_to_v007(self):
        for opcode in (0,2,3,4,5,6,7,0x43,0x53,0x63,0x73,0x13,0x1B,0x4B,0x5B,0x6B,0x7B):
            program = {0x20: opcode, 0x21: 0x80, 0x80: 0x69}
            sim = machine(program)
            sim.state.registers[7] = 0x80
            sim.memory.devices[0x80] = 0x45
            old = PreviousSimulator(PreviousState(**asdict(sim.state)), PreviousMemory(**asdict(sim.memory)))
            trace, old_trace = sim.run_instruction(), old.run_instruction()
            self.assertEqual(asdict(sim.state), asdict(old.state))
            self.assertEqual(asdict(sim.memory), asdict(old.memory))
            self.assertEqual([r.mops for r in trace], [r.mops for r in old_trace])


if __name__ == '__main__':
    unittest.main()
