"""EXR semantics under explicit H019 ALU-input holding-latch assumptions."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v014 import InstructionSimulator, Memory, ModelError, Simulator, State, evaluate
from cmc8.versions.v014.sequences import SEQUENCES, decode
from cmc8.versions.v013 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v013 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v013.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


def machine(opcode=0xBB, *, n=0, page=1, pc=0x20):
    state = State(n=n, pg=page, link=1, z=1, inte=0, h=0, t=1)
    state.registers = [0x90 + i for i in range(8)]
    state.registers[n] = pc
    return InstructionSimulator(state, Memory(program={(page << 8) | pc: opcode}))


def without_new_metadata(value):
    if isinstance(value, dict):
        return {key: without_new_metadata(item) for key, item in value.items()
                if key not in {'version', 'alu_a', 'alu_a_mode', 'alu_a_value'}}
    if isinstance(value, (list, tuple)):
        return [without_new_metadata(item) for item in value]
    return value


class HoldingLatchTests(unittest.TestCase):
    def test_restricted_transfer_search_and_xor_alias_counterexample(self):
        from experiments.exchange_routes import transfer_states, xor_swap

        self.assertFalse(any(state[:2] == ('b', 'a') for state in transfer_states()))
        self.assertEqual(xor_swap(0x80, 0xA6), (0xA6, 0x80))
        self.assertEqual(xor_swap(0x81, 0x81, same_register=True), (0, 0))

    def test_input_hold_survives_register_overwrite_and_reloads_br(self):
        state = State(ir=0xBB, br=0xA6)
        state.registers[3] = 0x80
        cpu = Simulator(state)
        cpu.capture((19, 21, 7), alu_a_mode='capture')
        cpu.capture((4, 19, 22))
        self.assertEqual(cpu.state.registers[3], 0xA6)
        row = cpu.capture((12,), alu_a_mode='held')
        self.assertEqual((row.signals.alu_a_value, row.after.br), (0x80, 0x80))
        cpu.capture((4, 20, 22))
        self.assertEqual(cpu.state.registers[7], 0x80)

    def test_end_observation_does_not_recapture_holding_latch(self):
        state = State(ir=0xBB)
        state.registers[3] = 0x80
        cpu = Simulator(state)
        cpu.capture((19, 21, 7), alu_a_mode='capture', point='start')
        cpu.state.registers[3] = 0xA6
        row = cpu.capture((19, 21, 7), alu_a_mode='capture', point='end')
        self.assertEqual(row.signals.alu_a_value, 0xA6)
        self.assertEqual(row.after.alu_a, 0x80)

    def test_named_modes_are_explicit_and_conflicts_fail(self):
        state = State(ir=0xBB, alu_a=0x80)
        self.assertIsNone(evaluate(state, (12,)).mux)  # Holding is never implicit.
        self.assertEqual(evaluate(state, (12,), alu_a_mode='held').mux, 0x80)
        for controls, mode in (((), 'capture'), ((7,), 'held'), ((), 'register')):
            with self.subTest(mode=mode), self.assertRaises(ModelError):
                evaluate(state, controls, alu_a_mode=mode)
        self.assertIsNone(evaluate(State(), (12,), alu_a_mode='held').mux)


class ExchangeInstructionTests(unittest.TestCase):
    def test_decoder_matches_all_repertory_bytes(self):
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
        self.assertEqual((len(SEQUENCES), count), (41, 237))
        for a in range(8):
            self.assertEqual(decode(0xB8 | a), 'EXR')

    def test_all_values_with_distinct_equal_and_complement_partners(self):
        for value in range(256):
            for x in (0, 255, 0x55, 0xAA, value, value ^ 255):
                sim = machine()
                sim.state.registers[3], sim.state.registers[7] = value, x
                sim.run_instruction()
                self.assertEqual((sim.state.registers[3], sim.state.registers[7]), (x, value))
                self.assertEqual((sim.state.link, sim.state.z), (1, 1))

    def test_all_register_pc_x_aliases_pages_and_pc_wrap(self):
        for n in range(8):
            for a in range(8):
                for page in range(4):
                    for pc in (0x20, 0xFE, 0xFF):
                        sim = machine(0xB8 | a, n=n, page=page, pc=pc)
                        expected = list(sim.state.registers)
                        expected[n] = (pc + 1) & 255
                        expected[a], expected[7] = expected[7], expected[a]
                        memory = asdict(sim.memory)
                        trace = sim.run_instruction()
                        self.assertEqual(sim.state.registers, expected)
                        self.assertEqual((sim.state.n, sim.state.pg, sim.state.link, sim.state.z,
                                          sim.state.inte, sim.state.h, sim.state.t), (n, page, 1, 1, 0, 0, 1))
                        self.assertEqual(asdict(sim.memory), memory)
                        self.assertEqual([(r.phase, r.timing) for r in trace],
                                         [(phase, timing) for phase in range(3) for timing in range(8)])

    def test_every_self_exchange_preserves_x_and_uses_same_schedule(self):
        for value in range(256):
            sim = machine(0xBF)
            sim.state.registers[7] = value
            trace = sim.run_instruction()
            self.assertEqual(sim.state.registers[7], value)
            self.assertEqual(sim.state.registers[0], 0x21)
            self.assertEqual([r.mops for r in trace], [slot for phase in SEQUENCES['EXR'] for slot in phase])

    def test_exchange_preserves_every_flag_combination(self):
        for link in (0, 1):
            for z in (0, 1):
                for inte in (0, 1):
                    sim = machine()
                    sim.state.link, sim.state.z, sim.state.inte = link, z, inte
                    sim.run_instruction()
                    self.assertEqual((sim.state.link, sim.state.z, sim.state.inte), (link, z, inte))

    def test_transfer_landmarks_show_both_old_values_are_preserved(self):
        sim = machine()
        sim.state.registers[3], sim.state.registers[7] = 0x80, 0xA6
        trace = sim.run_instruction()
        self.assertEqual(trace[13].start.after.br, 0xA6)
        self.assertEqual(trace[16].start.signals.alu_a_mode, 'capture')
        self.assertEqual(trace[16].start.after.alu_a, 0x80)
        self.assertEqual(trace[19].start.after.registers[3], 0x80)
        self.assertEqual(trace[20].start.after.registers[3], 0xA6)
        self.assertEqual(trace[20].start.after.registers[7], 0xA6)
        self.assertEqual(trace[21].start.signals.alu_a_mode, 'held')
        self.assertEqual(trace[21].start.after.br, 0x80)
        self.assertEqual(trace[22].start.after.registers[7], 0x80)
        self.assertEqual(sim.state.ab, 0x21)
        self.assertTrue(all(not ({24, 25, 26, 27, 32, 33} & set(r.mops)) for r in trace[8:]))

    def test_no_operand_or_execute_external_read(self):
        sim = machine()
        sim.memory.program_delay = 4
        sim.run_instruction()  # Only the opcode must reach transparent IR.
        self.assertEqual(sim.state.registers[0], 0x21)

    def test_unknown_inputs_fail_before_register_exchange_starts(self):
        for register, failure_slot in ((7, 13), (3, 16)):
            sim = machine()
            sim.state.registers[register] = None
            sim.state.alu_a = 0xEE  # A stale held value must not be substituted.
            for _ in range(failure_slot):
                sim.step()
            before = deepcopy(sim.state)
            with self.assertRaises(ModelError):
                sim.step()
            self.assertEqual(sim.state, before)
            self.assertEqual(len(sim.trace), failure_slot)
            sim.state.registers[register] = 0
            sim.step()

    def test_two_exchanges_restore_both_data_registers(self):
        for value in range(256):
            sim = machine()
            sim.state.registers[3], sim.state.registers[7] = value, value ^ 0xA6
            sim.memory.program[0x121] = 0xBB
            sim.run_instruction()
            sim.run_instruction()
            self.assertEqual((sim.state.registers[3], sim.state.registers[7]), (value, value ^ 0xA6))
            self.assertEqual(sim.state.registers[0], 0x22)

    def test_active_pc_exchange_controls_actual_next_fetch(self):
        for n, a in ((0, 0), (7, 3), (7, 7)):
            sim = machine(0xB8 | a, n=n)
            if n == 7:
                target = 0x21 if a == 7 else 0x80
                sim.state.registers[3] = 0x80
            else:
                target = 0x80
                sim.state.registers[7] = target
            sim.run_instruction()
            self.assertEqual(sim.state.registers[n], target)
            sim.memory.program[0x100 | target] = 0
            sim.run_instruction()
            self.assertEqual(sim.state.registers[n], target + 1)

    def test_exchange_initializes_index_then_restores_it(self):
        sim = machine()
        sim.state.registers[3], sim.state.registers[7] = 0x80, 0xA6
        sim.memory.program.update({0x121: 0x5C, 0x122: 0xBB})  # LSX R4; EXR R3.
        sim.memory.storage[0x180] = 0x69
        for _ in range(3):
            sim.run_instruction()
        self.assertEqual(sim.state.registers[3], 0x80)
        self.assertEqual(sim.state.registers[4], 0x69)
        self.assertEqual(sim.state.registers[7], 0xA6)
        self.assertEqual(len(sim.trace), 72)

    def test_zero_branch_sees_preserved_flag_not_exchange_data(self):
        for z in (0, 1):
            sim = machine()
            sim.state.z = z
            sim.state.registers[3], sim.state.registers[7] = 0, 0x80
            sim.memory.program.update({0x121: 0xE9, 0x122: 0x80})  # BZ1 page1.
            sim.run_instruction()
            trace = sim.run_instruction()
            self.assertEqual(trace[-2].branch_taken, z == 1)

    def test_previous_opcodes_preserve_trace_and_memory(self):
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
                old_state = asdict(current.state)
                del old_state['alu_a']
                previous = PreviousSimulator(PreviousState(**old_state), PreviousMemory(**asdict(current.memory)),
                                             test_inputs=current.test_inputs)
                self.assertEqual(without_new_metadata([asdict(row) for row in current.run_instruction()]),
                                 without_new_metadata([asdict(row) for row in previous.run_instruction()]))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])

    def test_demo_uses_and_restores_index_via_exchange(self):
        from cmc8.__main__ import exchange_demo

        sim = exchange_demo()
        self.assertEqual(len(sim.trace), 112)
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (1, 0x28))
        self.assertEqual(sim.state.registers[3:5], [0x80, 0x69])
        self.assertEqual(sim.state.registers[7], 0xA6)
        modes = [row.start.signals.alu_a_mode for row in sim.trace
                 if row.start.signals.alu_a_mode != 'di']
        self.assertEqual(modes, ['capture', 'held', 'capture', 'held'])


if __name__ == '__main__':
    unittest.main()
