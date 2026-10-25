"""Logical families, Z semantics, book programs and DCR consistency checks."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v012 import InstructionSimulator, Memory, ModelError, State, evaluate
from cmc8.versions.v012.sequences import SEQUENCES, decode
from cmc8.versions.v011 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v011 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v011.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


def machine(opcode, *, immediate=0xFF, n=0, page=1, pc=0x20):
    state = State(n=n, pg=page, link=1, z=1, inte=0, h=0, t=1)
    state.registers = [0x90 + index for index in range(8)]
    state.registers[n] = pc
    memory = Memory(program={(page << 8) | pc: opcode,
                             (page << 8) | ((pc + 1) & 255): immediate})
    return InstructionSimulator(state, memory)


def without_version(value):
    if isinstance(value, dict):
        return {key: without_version(item) for key, item in value.items() if key != 'version'}
    if isinstance(value, (list, tuple)):
        return [without_version(item) for item in value]
    return value


class LogicalInstructionTests(unittest.TestCase):
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
        self.assertEqual((len(SEQUENCES), count), (37, 205))

    def test_xor_alu_and_zero_for_all_operand_pairs(self):
        state = State(ir=0xAB)
        for left in range(256):
            state.registers[3] = left
            for right in range(256):
                state.br = right
                signals = evaluate(state, (19, 21, 3, 7, 8, 32, 12))
                self.assertEqual(signals.writes, {'br': left ^ right, 'z': int(left == right)})
                self.assertEqual((signals.zero_source, signals.zero_value), ('alu', left ^ right))

    def test_immediate_logic_all_bytes_with_zero_identity_and_mixed_operands(self):
        for base in (0x28, 0x30):
            for value in range(256):
                for immediate in (0, 255, value, value ^ 255):
                    result = value ^ immediate if base == 0x28 else value & immediate
                    sim = machine(base | 3, immediate=immediate)
                    sim.state.registers[3] = value
                    sim.state.z = int(result != 0)  # Require an update either way.
                    sim.run_instruction()
                    self.assertEqual(sim.state.registers[3], result)
                    self.assertEqual(sim.state.z, int(result == 0))
                    self.assertEqual(sim.state.registers[0], 0x22)
                    self.assertEqual(sim.state.registers[7], 0x97)

    def test_xor_all_bytes_with_zero_identity_and_mixed_x(self):
        for value in range(256):
            for x in (0, 255, value, value ^ 255):
                sim = machine(0xAB)
                sim.state.registers[3], sim.state.registers[7] = value, x
                sim.state.z = int(value != x)
                sim.run_instruction()
                self.assertEqual(sim.state.registers[7], value ^ x)
                self.assertEqual(sim.state.registers[3], value)
                self.assertEqual(sim.state.z, int(value == x))

    def test_all_register_pc_x_aliases_pages_and_operand_wrap(self):
        for base in (0x28, 0x30, 0xA8):
            for n in range(8):
                for a in range(8):
                    for page in range(4):
                        for pc in (0x20, 0xFF):
                            immediate = (0, 0xAA, 255)[(n + a + page) % 3]
                            sim = machine(base | a, immediate=immediate, n=n, page=page, pc=pc)
                            expected = list(sim.state.registers)
                            expected[n] = (pc + (1 if base == 0xA8 else 2)) & 255
                            right = expected[7] if base == 0xA8 else immediate
                            result = expected[a] & right if base == 0x30 else expected[a] ^ right
                            expected[7 if base == 0xA8 else a] = result
                            preserved = (sim.state.n, sim.state.pg, sim.state.link,
                                         sim.state.inte, sim.state.h, sim.state.t)
                            memory = asdict(sim.memory)
                            trace = sim.run_instruction()
                            self.assertEqual(sim.state.registers, expected)
                            self.assertEqual(sim.state.z, int(result == 0))
                            self.assertEqual((sim.state.n, sim.state.pg, sim.state.link,
                                              sim.state.inte, sim.state.h, sim.state.t), preserved)
                            self.assertEqual(asdict(sim.memory), memory)
                            self.assertEqual(len(trace), 24)

    def test_immediate_fetch_alu_flag_and_writeback_landmarks(self):
        for opcode in (0x2B, 0x33):
            sim = machine(opcode, immediate=0x08)
            sim.state.registers[3] = 0xF7
            trace = sim.run_instruction()
            result = 0xFF if opcode == 0x2B else 0
            self.assertEqual(trace[12].start.after.registers[0], 0x22)
            self.assertEqual(trace[13].start.after.br, 0x08)
            self.assertEqual(trace[14].mops, ())
            self.assertEqual(trace[18].start.after.registers[3], 0xF7)
            self.assertEqual(trace[19].start.signals.zero_value, result)
            self.assertEqual(trace[19].start.after.br, result)
            self.assertEqual(trace[19].start.after.z, int(result == 0))
            self.assertEqual(trace[19].start.after.registers[3], 0xF7)
            self.assertEqual(trace[20].mops, (4, 22, 19))
            self.assertEqual(trace[20].start.after.registers[3], result)
            self.assertEqual(sim.state.ab, 0x21)
            self.assertEqual([row.timing for row in trace[8:16] if 24 in row.mops], [2, 3, 4, 5])
            self.assertTrue(all(not ({24, 25, 26} & set(row.mops)) for row in trace[16:]))

    def test_xor_is_and_with_only_the_alu_operation_replaced(self):
        sim = machine(0xAB)
        del sim.memory.program[0x121]  # XOR is one byte.
        trace = sim.run_instruction()
        for and_phase, xor_phase in zip(SEQUENCES['AND'], SEQUENCES['XOR']):
            for and_slot, xor_slot in zip(and_phase, xor_phase):
                self.assertEqual(tuple(8 if mop == 9 else mop for mop in and_slot), xor_slot)
        self.assertTrue(all(not ({24, 25, 26} & set(row.mops)) for row in trace[8:]))
        self.assertEqual(trace[20].mops, (4, 22, 20))
        self.assertEqual(sim.state.registers[0], 0x21)

    def test_xor_result_and_z_capture_once_despite_br_feedback(self):
        for opcode in (0x2B, 0xAB):
            sim = machine(opcode, immediate=255)
            sim.state.registers[3] = 255
            sim.state.registers[7] = 255
            trace = sim.run_instruction()
            row = trace[19]
            self.assertEqual((row.start.signals.alu, row.start.after.br, row.start.after.z), (0, 0, 1))
            # Replacing the operand in BR changes the combinational XOR,
            # but the end observation must not clock the result/flag again.
            self.assertEqual(row.end.signals.alu, 255)
            self.assertEqual((row.end.after.br, row.end.after.z), (0, 1))

    def test_unknown_operand_or_alu_source_rolls_back(self):
        for opcode, failure_slot, source in ((0x2B, 13, 'immediate'), (0x33, 13, 'immediate'),
                                             (0x2B, 19, 'register'), (0xAB, 19, 'register')):
            sim = machine(opcode)
            if source == 'immediate':
                del sim.memory.program[0x121]
            else:
                sim.state.registers[3] = None
            for _ in range(failure_slot):
                sim.step()
            before = deepcopy(sim.state)
            with self.assertRaises(ModelError):
                sim.step()
            self.assertEqual(sim.state, before)
            self.assertEqual(len(sim.trace), failure_slot)
            if source == 'immediate':
                sim.memory.program[0x121] = 0
            else:
                sim.state.registers[3] = 0
            sim.step()

    def test_delayed_immediate_must_reach_start_of_t5(self):
        for opcode in (0x2B, 0x33):
            sim = machine(opcode)
            sim.memory.program_delay = 4
            for _ in range(13):
                sim.step()
            with self.assertRaisesRegex(ModelError, 'start of T5'):
                sim.step()
            sim.memory.program_delay = 3
            sim.step()
            self.assertEqual(sim.state.br, 255)

    def test_immediate_matching_ein_is_data_not_retained_control_ir(self):
        for opcode in (0x2B, 0x33):
            sim = machine(opcode, immediate=3)
            sim.memory.program[0x122] = 0
            sim.run_instruction()
            trace = sim.run_instruction()
            self.assertIsNone(trace[2].flag_effect)
            self.assertEqual(sim.state.inte, 0)

    def test_result_written_to_active_pc_controls_actual_next_fetch(self):
        for opcode, n, immediate, target in ((0x28, 0, 0xA2, 0x80),
                                             (0x30, 0, 0xF0, 0x20),
                                             (0xAB, 7, 0, 0x80)):
            sim = machine(opcode, n=n, immediate=immediate)
            if n == 7:
                sim.state.registers[3] = 0xA1  # Post-fetch X=21; A1 XOR 21=80.
            sim.run_instruction()
            self.assertEqual(sim.state.registers[n], target)
            sim.memory.program[(1 << 8) | target] = 0
            trace = sim.run_instruction()
            self.assertEqual(trace[6].instruction, 'NOP')
            self.assertEqual(sim.state.registers[n], target + 1)

    def test_both_branch_polarities_consume_final_logical_result(self):
        for opcode in (0x2B, 0x33, 0xAB):
            for value, right in ((255, 255), (0xF7, 8), (8, 8), (0, 255)):
                for desired in (0, 1):
                    sim = machine(opcode, immediate=right)
                    sim.state.registers[3], sim.state.registers[7] = value, right
                    result = value & right if opcode == 0x33 else value ^ right
                    address = 0x21 if opcode == 0xAB else 0x22
                    sim.memory.program.update({0x100 | address: 0xE1 | (desired << 3),
                                               0x100 | (address + 1): 0x80})
                    sim.run_instruction()
                    trace = sim.run_instruction()
                    self.assertEqual(trace[-2].branch_taken, int(result == 0) == desired)

    def test_ani_lamp_polling_example_uses_masked_result_and_can_exit(self):
        # Fig.6.9 mnemonic structure; R3 chosen as the example accumulator.
        sim = machine(0x23, immediate=4)
        sim.memory.program.update({
            0x122: 0x1B, 0x123: 0,  # SRD R3,port0.
            0x124: 0x13, 0x125: 1,  # LRD R3,port1.
            0x126: 0x33, 0x127: 8,  # ANI R3,#010 octal.
            0x128: 0xE1, 0x129: 0x24, 0x12A: 0,
        })
        sim.memory.devices[1] = 0xF8  # Status bit3 high; unrelated bits high too.
        for _ in range(5):
            sim.run_instruction()
        self.assertEqual(sim.memory.devices[0], 4)
        self.assertEqual((sim.state.registers[0], sim.state.registers[3], sim.state.z), (0x24, 8, 0))
        sim.memory.devices[1] = 0xF7  # Bit3 low; source is still nonzero.
        for _ in range(4):
            sim.run_instruction()
        self.assertEqual((sim.state.registers[0], sim.state.registers[3], sim.state.z), (0x2B, 0, 1))

    def test_xri_keyboard_example_handles_press_release_and_return(self):
        # Fig.8.10 mnemonic intent. Apply candidate byte corrections E004/E005
        # explicitly; the source listing itself remains unchanged.
        sim = machine(0x0C, n=0, page=3, pc=0x40, immediate=0)
        sim.memory.program.update({
            0x342: 0,
            0x300: 0x16, 0x301: 5, 0x302: 0x3E, 0x303: 0x2F, 0x304: 255,
            0x305: 0xEB, 0x306: 0, 0x307: 0,
            0x308: 0x17, 0x309: 5, 0x30A: 0x2F, 0x30B: 255,
            0x30C: 0xE3, 0x30D: 8, 0x30E: 0x0F,
        })
        sim.memory.devices[5] = 255
        for _ in range(5):
            sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.registers[1], sim.state.z), (1, 0, 1))
        sim.memory.devices[5] = 0x42
        for _ in range(4):
            sim.run_instruction()
        self.assertEqual((sim.state.registers[1], sim.state.registers[6]), (7, 0x42))
        for _ in range(4):
            sim.run_instruction()
        self.assertEqual((sim.state.registers[1], sim.state.z), (8, 0))
        sim.memory.devices[5] = 255
        for _ in range(5):
            sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.registers[0], sim.state.registers[6]), (0, 0x43, 0x42))
        self.assertEqual(sim.state.z, 1)
        self.assertEqual(len(sim.trace), 344)

    def test_dcr_matches_xri_inr_xri_reconstruction_for_all_bytes(self):
        for value in range(256):
            direct = machine(0xA3)
            direct.state.registers[3] = value
            trace = direct.run_instruction()
            reconstructed = machine(0x2B, immediate=255)
            reconstructed.state.registers[3] = value
            reconstructed.memory.program.update({0x122: 0x83, 0x123: 0x2B, 0x124: 255})
            for _ in range(3):
                reconstructed.run_instruction()
            self.assertEqual((direct.state.registers[3], direct.state.z),
                             (reconstructed.state.registers[3], reconstructed.state.z))
            # The unselected T3 all-ones detector has the same final predicate
            # as selected T6 DI-zero; this does not prove either capture time.
            self.assertEqual(int(trace[19].start.signals.alu == 255), direct.state.z)
            self.assertEqual(trace[22].start.signals.zero_source, 'di')

    def test_every_previous_opcode_retains_trace_and_memory(self):
        catalogue, _ = load_data()
        for opcode, name in validate(catalogue).items():
            if name not in PREVIOUS_SEQUENCES:
                continue
            with self.subTest(opcode=opcode):
                current = machine(opcode, immediate=0x80)
                current.test_inputs = (0, 0, 0, 0)
                current.state.registers[7] = 0x80
                current.memory.program[0x180] = 0xA6
                current.memory.storage[0x180] = 0x69
                current.memory.devices[0x80] = 0x5A
                previous = PreviousSimulator(PreviousState(**asdict(current.state)),
                                             PreviousMemory(**asdict(current.memory)),
                                             test_inputs=current.test_inputs)
                self.assertEqual(without_version([asdict(row) for row in current.run_instruction()]),
                                 without_version([asdict(row) for row in previous.run_instruction()]))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])

    def test_cli_demo_exercises_all_three_logical_families(self):
        from cmc8.__main__ import logical_demo

        sim = logical_demo()
        self.assertEqual(len(sim.trace), 160)
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (1, 0x4A))
        self.assertEqual(sim.state.registers[3:6], [0, 0, 0xAA])
        self.assertEqual((sim.state.registers[7], sim.state.z), (0, 1))
        samples = [(row.instruction, row.start.signals.zero_source, row.start.signals.zero_value)
                   for row in sim.trace if 32 in row.mops]
        self.assertEqual(samples, [('XRI', 'alu', 0), ('ANI', 'alu', 0), ('XOR', 'alu', 0)])


if __name__ == '__main__':
    unittest.main()
