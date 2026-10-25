"""Whole-model checks against a direct, instruction-level reference.

The reference deliberately does not import MOP tables or datapath functions.
It checks the selected architectural semantics, not the historical silicon
or the inferred placement of internal signals.
"""
from copy import deepcopy
import random
import unittest

from cmc8.versions.v016 import ControlPort, InstructionSimulator, InterruptInput, Memory, State
from tools.build_instruction_reference import load_data, validate


FLAGS = {'DIN', 'EIN', 'REL', 'SEL', 'REZ', 'SEZ'}
LOADS = {'LRD', 'LRM', 'LRS', 'LRX', 'LSX'}
STORES = {'SRD', 'SRM', 'SRS', 'SRX', 'SSX'}
INDEXED = {'LRX', 'LSX', 'SRX', 'SSX'}


def reference(state, memory, entry, opcode, operand, pins):
    """Apply one instruction after ordinary fetch, using plain byte arithmetic."""
    result, memories = deepcopy(state), deepcopy(memory)
    r = result.registers
    n, a = result.n, opcode & 7
    r[n] = (r[n] + entry['length_bytes']) & 255
    name = entry['mnemonic']
    if name in LOADS | STORES:
        space = ('devices' if name.endswith('D') else
                 'storage' if name in {'LRS', 'SRS', 'LSX', 'SSX'} else 'program')
        address = r[7] if name in INDEXED else operand
        if space != 'devices':
            address |= result.pg << 8
        cells = getattr(memories, space)
        if name in LOADS:
            r[a] = cells[address]
        else:
            cells[address] = r[a]
    elif name == 'LRI':
        r[a] = operand
    elif name == 'CPY':
        r[7] = r[a]
    elif name == 'EXR':
        r[a], r[7] = r[7], r[a]
    elif name in {'AND', 'XOR', 'ANI', 'XRI'}:
        left, right = r[a], r[7] if name in {'AND', 'XOR'} else operand
        value = left & right if name in {'AND', 'ANI'} else left ^ right
        r[7 if name in {'AND', 'XOR'} else a] = value
        result.z = int(value == 0)
    elif name in {'INR', 'DCR'}:
        r[a] = (r[a] + (1 if name == 'INR' else -1)) & 255
        result.z = int(r[a] == 0)
    elif name in {'ROR', 'SHR', 'RRL'}:
        value = r[a]
        high = value & 1 if name == 'ROR' else result.link if name == 'RRL' else 0
        r[a] = (value >> 1) | (high << 7)
        if name == 'RRL':
            result.link = value & 1
    elif name == 'JMP':
        r[n], result.pg = operand, opcode & 3
    elif name == 'JCR':
        r[n] = r[a]
    elif name == 'JSR':
        result.n = (n + 1) & 7
        r[result.n] = operand
    elif name == 'RSR':
        result.n = (n - 1) & 7
    elif name.startswith(('BB', 'BZ', 'BL', 'BT')):
        kind = name[1]
        condition = {'B': r[a] & 1, 'Z': result.z,
                     'L': result.link, 'T': pins[opcode & 3]}[kind]
        if condition == int(name[-1]):
            r[n] = operand
            if kind in {'Z', 'L'}:
                result.pg = opcode & 3
    elif name not in FLAGS | {'NOP', 'SCS', 'SCW'}:
        raise AssertionError(f'Missing independent semantics: {name}')
    # Flag opcodes act during the next fetch, not before this boundary.
    return result, memories


class HolisticTests(unittest.TestCase):
    def test_all_encodings_with_every_pc_selector_and_boundary_addresses(self):
        catalogue, _ = load_data()
        entries = {item['mnemonic']: item for item in catalogue['instructions']}
        rng = random.Random(0xC8)  # Stable experiment inputs.
        count = 0
        for opcode, name in validate(catalogue).items():
            entry = entries[name]
            for n in range(8):
                for pc in (0, 254, 255):
                    with self.subTest(opcode=opcode, n=n, pc=pc):
                        page = (n + pc) & 3
                        state = State(n=n, pg=page, ir=0, link=rng.randrange(2),
                                      z=rng.randrange(2), inte=rng.randrange(2),
                                      intr=0, inta=0, h=0, t=0)
                        state.registers = [rng.randrange(256) for _ in range(8)]
                        state.registers[n] = pc
                        operand = rng.randrange(256)
                        index = (pc + 1) & 255 if n == 7 else state.registers[7]
                        program = {(page << 8) | operand: rng.randrange(256),
                                   (page << 8) | index: rng.randrange(256)}
                        program[(page << 8) | pc] = opcode
                        program[(page << 8) | ((pc + 1) & 255)] = operand
                        memory = Memory(program=program,
                                        storage={(page << 8) | address: rng.randrange(256)
                                                 for address in (operand, index)},
                                        devices={operand: rng.randrange(256)})
                        pins = tuple(rng.randrange(2) for _ in range(4))
                        expected, expected_memory = reference(state, memory, entry, opcode,
                                                               operand, pins)
                        sim = InstructionSimulator(state, memory, test_inputs=pins,
                                                   control=ControlPort(scwr=0))
                        trace = sim.run_instruction()
                        self.assertEqual(len(trace), entry['base_cycles'] * 8)
                        self.assertEqual(sim.state.registers, expected.registers)
                        for field in ('n', 'pg', 'link', 'z', 'inte', 'intr', 'inta'):
                            self.assertEqual(getattr(sim.state, field), getattr(expected, field), field)
                        self.assertEqual(sim.memory, expected_memory)
                        strobes = sim.control.strobes
                        self.assertEqual([s.value for s in strobes],
                                         [operand] if name in {'SCS', 'SCW'} else [])
                        writes = [t.memory_write for t in trace if t.memory_write is not None]
                        self.assertEqual(len(writes), int(name in STORES))
                        self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))
                        count += 1
        self.assertEqual(count, 5736)

    def test_each_deferred_flag_before_every_opcode_and_following_fetch(self):
        catalogue, _ = load_data()
        entries = {item['mnemonic']: item for item in catalogue['instructions']}
        effects = {2: ('inte', 0), 3: ('inte', 1), 4: ('link', 0),
                   5: ('link', 1), 6: ('z', 0), 7: ('z', 1)}
        for flag_opcode, (field, value) in effects.items():
            for opcode, name in validate(catalogue).items():
                with self.subTest(flag=flag_opcode, opcode=opcode):
                    state = State(n=0, pg=2, ir=0, inte=1-value, link=1-value,
                                  z=1-value, intr=0, inta=0, h=0, t=0)
                    state.registers = [0xFE, 0x41, 0x52, 0x63, 0x74, 0x85, 0x96, 0xA7]
                    # The first opcode sits at FE; the next opcode is at FF,
                    # and its optional operand wraps to 00 on the same page.
                    memory = Memory(program={0x2FE: flag_opcode, 0x2FF: opcode,
                                             0x200: 0x80, 0x280: 0x69, 0x2A7: 0x96},
                                    storage={0x280: 0x69, 0x2A7: 0x96},
                                    devices={0x80: 0x5A})
                    sim = InstructionSimulator(state, memory, test_inputs=(0, 1, 0, 1),
                                               control=ControlPort(scwr=0))
                    sim.run_instruction()
                    self.assertEqual(getattr(sim.state, field), 1-value)
                    expected = deepcopy(state)
                    expected.registers[0] = 0xFF
                    setattr(expected, field, value)
                    expected, expected_memory = reference(expected, memory, entries[name],
                                                           opcode, 0x80, (0, 1, 0, 1))
                    sim.run_instruction()
                    self.assertEqual(sim.state.registers, expected.registers)
                    self.assertEqual(sim.memory, expected_memory)
                    for flag in ('inte', 'link', 'z'):
                        self.assertEqual(getattr(sim.state, flag), getattr(expected, flag))
                    # Observe a third fetch to distinguish a deferred second
                    # flag opcode from an already applied first flag effect.
                    address = (sim.state.pg << 8) | sim.state.registers[sim.state.n]
                    sim.memory.program[address] = 0
                    if opcode in effects:
                        next_field, next_value = effects[opcode]
                        setattr(expected, next_field, next_value)
                    for _ in range(3):
                        sim.step()
                    for flag in ('inte', 'link', 'z'):
                        self.assertEqual(getattr(sim.state, flag), getattr(expected, flag))

    def test_every_opcode_finishes_before_a_mid_fetch_request_is_serviced(self):
        catalogue, _ = load_data()
        entries = {item['mnemonic']: item for item in catalogue['instructions']}
        for opcode, name in validate(catalogue).items():
            with self.subTest(opcode=opcode):
                state = State(n=0, pg=2, ir=0, inte=1, link=1, z=0,
                              intr=0, inta=0, h=0, t=0)
                state.registers = [0x20, 0x41, 0x52, 0x63, 0x74, 0x85, 0x96, 0xA7]
                memory = Memory(program={0x220: opcode, 0x221: 0x80,
                                         0x280: 0x69, 0x2A7: 0x96},
                                storage={0x280: 0x69, 0x2A7: 0x96}, devices={0x80: 0x5A})
                expected, expected_memory = reference(state, memory, entries[name], opcode,
                                                       0x80, (0, 1, 0, 1))
                sim = InstructionSimulator(state, memory, test_inputs=(0, 1, 0, 1),
                                           interrupts=InterruptInput(1), control=ControlPort(scwr=0))
                for _ in range(3):
                    sim.step()
                sim.set_interrupt(0)
                sim.set_interrupt(1)
                sim.resume_instruction()
                self.assertEqual(sim.state.registers, expected.registers)
                self.assertEqual(sim.state.n, expected.n)
                self.assertEqual(sim.state.pg, expected.pg)
                self.assertEqual(sim.memory, expected_memory)
                self.assertFalse(any(row.interrupt_accepted for row in sim.trace))
                self.assertEqual(sim.state.intr, 1)
                expected.registers[(expected.n + 1) & 7] = 2
                entry = sim.run_instruction()
                self.assertEqual(len(entry), 8)
                self.assertTrue(entry[0].interrupt_accepted)
                self.assertEqual(sim.state.registers, expected.registers)
                self.assertEqual(sim.state.n, (expected.n + 1) & 7)
                self.assertEqual(sim.state.pg, expected.pg)
                self.assertEqual((sim.state.inte, sim.state.intr, sim.state.inta), (0, 0, 1))
                self.assertEqual(sim.memory, expected_memory)


if __name__ == '__main__':
    unittest.main()
