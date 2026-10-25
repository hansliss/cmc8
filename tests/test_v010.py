"""Immediate loads and register copies: values, aliases, timing and regressions."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v010 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v010.sequences import SEQUENCES, decode
from cmc8.versions.v009 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v009 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v009.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


EXECUTE_SLOTS = [(1, 0), (1, 1)] + [(2, timing) for timing in range(2, 8)]


def machine(opcode, *, immediate=0xA6, n=0, page=1, pc=0x20):
    state = State(n=n, pg=page, link=1, z=1, inte=0, h=0, t=1)
    state.registers = [0x90 + index for index in range(8)]
    state.registers[n] = pc
    memory = Memory(program={
        (page << 8) | pc: opcode,
        (page << 8) | ((pc + 1) & 255): immediate,
    })
    return InstructionSimulator(state, memory)


def flags_and_selectors(state):
    return state.n, state.pg, state.link, state.z, state.inte, state.h, state.t


def without_version(value):
    if isinstance(value, dict):
        return {key: without_version(item) for key, item in value.items() if key != 'version'}
    if isinstance(value, (tuple, list)):
        return [without_version(item) for item in value]
    return value


class ImmediateAndCopyTests(unittest.TestCase):
    def test_decoder_matches_all_repertory_bytes(self):
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
        self.assertEqual((len(SEQUENCES), supported), (31, 157))
        for register in range(8):
            self.assertEqual(decode(0x20 | register), 'LRI')
            self.assertEqual(decode(0x38 | register), 'CPY')

    def test_lri_every_immediate_value(self):
        for value in range(256):
            sim = machine(0x23, immediate=value)
            sim.run_instruction()
            self.assertEqual(sim.state.registers[3], value)
            self.assertEqual(sim.state.registers[0], 0x22)
            self.assertEqual(sim.state.ir, 0x23)
            self.assertEqual((sim.state.link, sim.state.z), (1, 1))

    def test_lri_all_register_pc_aliases_pages_and_boundaries(self):
        for n in range(8):
            for destination in range(8):
                for page in range(4):
                    for pc in (0x20, 0xFE, 0xFF):
                        immediate = (0, 0x80, 0xFF)[(n + destination + page) % 3]
                        sim = machine(0x20 | destination, immediate=immediate, n=n, page=page, pc=pc)
                        expected = list(sim.state.registers)
                        expected[n] = (pc + 2) & 255
                        expected[destination] = immediate
                        preserved = flags_and_selectors(sim.state)
                        memory_before = asdict(sim.memory)
                        trace = sim.run_instruction()
                        self.assertEqual(sim.state.registers, expected)
                        self.assertEqual(flags_and_selectors(sim.state), preserved)
                        self.assertEqual(asdict(sim.memory), memory_before)
                        self.assertEqual(len(trace), 16)

    def test_lri_transfer_landmarks_and_no_second_dereference(self):
        sim = machine(0x23)
        # No cell exists at 1A6: A6 is data, never an address to read.
        trace = sim.run_instruction()
        self.assertEqual([(row.phase, row.timing) for row in trace[8:]], EXECUTE_SLOTS)
        self.assertEqual(trace[9].mops, (18, 21, 31))
        self.assertEqual(trace[12].start.after.registers[0], 0x22)
        self.assertEqual(trace[13].start.after.br, 0xA6)
        self.assertEqual(trace[13].start.after.registers[3], 0x93)
        self.assertEqual(trace[14].mops, (4, 19, 22))
        self.assertEqual(trace[14].start.after.registers[3], 0xA6)
        self.assertEqual([row.timing for row in trace[8:] if 24 in row.mops], [2, 3, 4, 5])
        self.assertTrue(all(25 not in row.mops and 26 not in row.mops for row in trace))
        self.assertEqual(sim.state.ab, 0x21)
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))

    def test_lri_operand_must_arrive_at_start_of_t5(self):
        sim = machine(0x23)
        sim.memory.program_delay = 4
        for _ in range(13):
            sim.step()
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'start of T5'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(len(sim.trace), 13)
        sim.memory.program_delay = 3
        sim.step()
        self.assertEqual(sim.state.br, 0xA6)

    def test_lri_to_active_pc_changes_actual_next_fetch(self):
        for n in range(8):
            sim = machine(0x20 | n, n=n, immediate=0x80)
            sim.memory.program[0x180] = 0  # Destination NOP.
            sim.memory.program[0x122] = 1  # Wrong fall-through would fail decode.
            sim.run_instruction()
            trace = sim.run_instruction()
            self.assertEqual(trace[6].instruction, 'NOP')
            self.assertEqual(sim.state.registers[n], 0x81)

    def test_immediate_flag_opcode_does_not_replace_ir_or_change_flags(self):
        sim = machine(0x23, immediate=0x03)  # Data happens to encode EIN.
        sim.memory.program[0x122] = 0
        sim.run_instruction()
        trace = sim.run_instruction()
        self.assertIsNone(trace[2].flag_effect)
        self.assertEqual(sim.state.inte, 0)

    def test_cpy_every_byte_value_and_source_register(self):
        for source in range(8):
            for value in range(256):
                # Keep N distinct from the source to test the full byte range.
                n = (source + 1) % 8
                sim = machine(0x38 | source, n=n)
                sim.state.registers[source] = value
                sim.run_instruction()
                self.assertEqual(sim.state.registers[7], value)
                if n != 7:
                    self.assertEqual(sim.state.registers[n], 0x21)
                if source != 7:
                    self.assertEqual(sim.state.registers[source], value)

    def test_cpy_all_pc_source_x_aliases_pages_and_pc_wrap(self):
        for n in range(8):
            for source in range(8):
                for page in range(4):
                    for pc in (0x20, 0xFF):
                        sim = machine(0x38 | source, n=n, page=page, pc=pc)
                        expected = list(sim.state.registers)
                        expected[n] = (pc + 1) & 255
                        expected[7] = expected[source]
                        preserved = flags_and_selectors(sim.state)
                        memory_before = asdict(sim.memory)
                        trace = sim.run_instruction()
                        self.assertEqual(sim.state.registers, expected)
                        self.assertEqual(flags_and_selectors(sim.state), preserved)
                        self.assertEqual(asdict(sim.memory), memory_before)
                        self.assertEqual(len(trace), 16)

    def test_cpy_buffered_route_needs_no_operand_or_external_read(self):
        sim = machine(0x3B)
        del sim.memory.program[0x121]
        sim.memory.program_delay = 4  # Opcode reaches IR at end T5.
        trace = sim.run_instruction()
        self.assertEqual([(row.phase, row.timing) for row in trace[8:]], EXECUTE_SLOTS)
        self.assertEqual(trace[8].start.signals.di, 0x93)
        self.assertEqual(trace[9].mops, (19, 21, 23, 31))
        self.assertEqual(trace[13].start.signals.db, 0x93)
        self.assertEqual(trace[13].start.after.br, 0x93)
        self.assertEqual(trace[14].mops, (4, 20, 22))
        self.assertEqual(sim.state.registers[7], 0x93)
        self.assertTrue(all(not ({24, 25, 26, 27} & set(row.mops)) for row in trace[8:]))
        self.assertEqual(sim.state.ir, 0x3B)

    def test_unknown_cpy_source_fails_without_committing_slot(self):
        sim = machine(0x3B)
        sim.state.registers[3] = None
        for _ in range(13):
            sim.step()
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'DB is not valid'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(len(sim.trace), 13)
        sim.state.registers[3] = 0
        sim.step()
        sim.step()
        self.assertEqual(sim.state.registers[7], 0)

    def test_cpy_to_x_when_n_is_seven_changes_actual_next_fetch(self):
        sim = machine(0x3B, n=7)
        sim.state.registers[3] = 0x80
        sim.memory.program[0x180] = 0
        sim.memory.program[0x121] = 1
        sim.run_instruction()
        sim.run_instruction()
        self.assertEqual(sim.state.registers[7], 0x81)

    def test_lri_and_cpy_compose_with_indexed_loads(self):
        sim = machine(0x23, immediate=0x80)
        sim.memory.program.update({0x122: 0x3B, 0x123: 0x5C})  # CPY R3; LSX R4.
        sim.memory.storage[0x180] = 0x69
        for _ in range(3):
            sim.run_instruction()
        self.assertEqual(sim.state.registers[3:5], [0x80, 0x69])
        self.assertEqual(sim.state.registers[7], 0x80)
        self.assertEqual(sim.state.registers[0], 0x24)
        self.assertEqual(len(sim.trace), 56)

    def test_demo_reads_and_writes_through_the_copied_index(self):
        from cmc8.__main__ import immediate_copy_demo

        sim = immediate_copy_demo()
        self.assertEqual(len(sim.trace), 104)
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (1, 0x28))
        self.assertEqual(sim.state.registers[3:6], [0x80, 0x69, 0xA6])
        self.assertEqual(sim.state.registers[7], 0x80)
        self.assertEqual(sim.memory.storage, {0x180: 0xA6})

    def test_every_previous_opcode_retains_its_trace_and_memory_effects(self):
        catalogue, _ = load_data()
        for opcode, name in validate(catalogue).items():
            if name not in PREVIOUS_SEQUENCES:
                continue
            with self.subTest(opcode=opcode, name=name):
                current = machine(opcode, immediate=0x80)
                current.test_inputs = (0, 0, 0, 0)
                current.state.registers[7] = 0x80
                current.memory.program[0x180] = 0xA6
                current.memory.storage[0x180] = 0x69
                current.memory.devices[0x80] = 0x5A
                previous = PreviousSimulator(PreviousState(**asdict(current.state)),
                                             PreviousMemory(**asdict(current.memory)),
                                             test_inputs=current.test_inputs)
                actual = [asdict(row) for row in current.run_instruction()]
                expected = [asdict(row) for row in previous.run_instruction()]
                self.assertEqual(without_version(actual), without_version(expected))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])


if __name__ == '__main__':
    unittest.main()
