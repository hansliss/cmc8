"""Control-byte strobing, active-low acknowledgement and complete wait cycles."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v015 import (ControlPort, InstructionLimit, InstructionSimulator,
                                 Memory, ModelError, State, evaluate)
from cmc8.versions.v015.sequences import SEQUENCES, decode
from cmc8.versions.v014 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v014 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v014.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


def machine(opcode=8, *, value=0xA6, n=0, page=1, pc=0x20, control=None):
    state = State(n=n, pg=page, link=1, z=1, inte=0, h=0, t=1, sse=1)
    state.registers = [0x90 + i for i in range(8)]
    state.registers[n] = pc
    memory = Memory(program={(page << 8) | pc: opcode,
                             (page << 8) | ((pc + 1) & 255): value})
    return InstructionSimulator(state, memory, control=control)


def without_new_metadata(value):
    if isinstance(value, dict):
        return {key: without_new_metadata(item) for key, item in value.items()
                if key not in {'version', 'scwr_input', 'strcs', 'control_strobe', 'scwr', 'waiting'}}
    if isinstance(value, (list, tuple)):
        return [without_new_metadata(item) for item in value]
    return value


class HandshakeDatapathTests(unittest.TestCase):
    def test_mop50_samples_raw_active_low_pin_at_t4(self):
        for level in (0, 1):
            signals = evaluate(State(timing=4), (24, 50), scwr=level)
            self.assertEqual(signals.writes, {'wait': level})
            self.assertEqual(signals.scwr_input, level)
        for state, level in ((State(timing=4), None), (State(timing=3), 0)):
            with self.assertRaises(ModelError):
                evaluate(state, (50,), scwr=level)

    def test_strcs_is_a_named_output_without_an_invented_mop_number(self):
        signals = evaluate(State(), (24,), external_db=0xA6, strcs=True)
        self.assertEqual(signals.outputs, ('PME', 'STRCS'))
        self.assertEqual(signals.writes, {})
        for kwargs in ({'scwr': 2}, {'scwr': False}, {'strcs': 1}):
            with self.assertRaises(ModelError):
                evaluate(State(), (), **kwargs)

    def test_control_port_inputs_and_automatic_delay_are_validated(self):
        for kwargs in ({'scwr': 2}, {'scwr': False}, {'ack_after': -1}, {'ack_after': True}):
            with self.assertRaises(ModelError):
                ControlPort(**kwargs)


class ControlInstructionTests(unittest.TestCase):
    def test_all_43_families_and_239_variants_decode(self):
        catalogue, _ = load_data()
        encodings = validate(catalogue)
        self.assertEqual(len(SEQUENCES), 43)
        for opcode in range(256):
            if opcode in encodings:
                self.assertEqual(decode(opcode), encodings[opcode])
            else:
                with self.assertRaises(ValueError):
                    decode(opcode)

    def test_all_control_byte_values_for_both_instructions(self):
        for opcode in (8, 9):
            for value in range(256):
                sim = machine(opcode, value=value, control=ControlPort(scwr=0))
                trace = sim.run_instruction()
                self.assertEqual(sim.control.value, value)
                self.assertEqual(len(sim.control.strobes), 1)
                self.assertEqual(sim.control.strobes[0].value, value)
                self.assertEqual(sim.state.registers[0], 0x22)
                self.assertEqual(len(trace), 24)

    def test_all_pc_registers_pages_and_operand_wrap(self):
        for opcode in (8, 9):
            for n in range(8):
                for page in range(4):
                    for pc in (0x20, 0xFE, 0xFF):
                        sim = machine(opcode, n=n, page=page, pc=pc, control=ControlPort(scwr=0))
                        expected = list(sim.state.registers)
                        expected[n] = (pc + 2) & 255
                        memory = asdict(sim.memory)
                        sim.run_instruction()
                        self.assertEqual(sim.state.registers, expected)
                        self.assertEqual(sim.state.ab, (pc + 1) & 255)
                        self.assertEqual(sim.state.br, (pc + 2) & 255)
                        self.assertEqual((sim.state.n, sim.state.pg, sim.state.link, sim.state.z,
                                          sim.state.inte, sim.state.h, sim.state.t, sim.state.sse),
                                         (n, page, 1, 1, 0, 0, 1, 1))
                        self.assertEqual(asdict(sim.memory), memory)
                        self.assertEqual(sim.control.strobes[0].address,
                                         (page << 8) | ((pc + 1) & 255))

    def test_strobe_and_bus_landmarks_follow_figures_6_17_and_6_18(self):
        sim = machine(control=ControlPort(scwr=0))
        trace = sim.run_instruction()
        self.assertEqual(trace[12].start.after.registers[0], 0x22)
        self.assertEqual(trace[13].mops, (24,))  # No control-byte capture in BR.
        self.assertEqual(trace[13].start.after.br, 0x22)
        self.assertEqual([(r.phase, r.timing) for r in trace if r.strcs], [(1, 6)])
        strobe = trace[14]
        self.assertEqual(strobe.start.signals.db, 0xA6)
        self.assertEqual(strobe.control_strobe.slot, 14)
        self.assertEqual(strobe.start.signals.outputs, ('PME', 'STRCS'))
        self.assertEqual([i for i, r in enumerate(trace[8:], 8) if 24 in r.mops], list(range(10, 22)))
        self.assertEqual(trace[20].mops, (24, 50))
        self.assertEqual(trace[20].start.signals.scwr_input, 0)
        self.assertEqual(trace[22].mops, ())
        self.assertEqual(trace[23].mops, (30,))
        self.assertTrue(all(not ({23, 25, 26, 27} & set(r.mops)) for r in trace))

    def test_scs_ignores_unknown_and_high_acknowledgement(self):
        for pin in (None, 0, 1):
            sim = machine(9, control=ControlPort(scwr=pin))
            trace = sim.run_instruction()
            self.assertEqual(len(trace), 24)
            self.assertTrue(all(50 not in r.mops for r in trace))
            self.assertFalse(any(r.waiting for r in trace))

    def test_flags_and_provisional_alu_latch_are_preserved(self):
        for opcode in (8, 9):
            for link in (0, 1):
                for z in (0, 1):
                    for inte in (0, 1):
                        sim = machine(opcode, control=ControlPort(ack_after=20))
                        sim.state.link, sim.state.z, sim.state.inte = link, z, inte
                        sim.state.alu_a = 0x55
                        sim.run_instruction()
                        self.assertEqual((sim.state.link, sim.state.z, sim.state.inte,
                                          sim.state.alu_a), (link, z, inte, 0x55))

    def test_ack_delays_are_quantized_to_complete_eight_slot_waits(self):
        for delay in range(40):
            waits = max(0, (delay - 6 + 7) // 8)
            sim = machine(control=ControlPort(ack_after=delay))
            trace = sim.run_instruction()
            self.assertEqual(len(trace), 24 + 8 * waits)
            samples = [i for i, row in enumerate(trace) if 50 in row.mops]
            self.assertEqual(samples, [20 + 8 * i for i in range(waits + 1)])
            self.assertEqual(sim.state.wait, 0)
            self.assertEqual(len(sim.control.strobes), 1)

    def test_book_two_wait_cycles_hold_bus_and_do_not_repeat_instruction_actions(self):
        sim = machine(control=ControlPort(ack_after=20))
        trace = sim.run_instruction()
        self.assertEqual(len(trace), 40)
        self.assertEqual([(i, r.phase, r.timing, r.scwr) for i, r in enumerate(trace) if 50 in r.mops],
                         [(20, 2, 4, 1), (28, 3, 4, 1), (36, 3, 4, 0)])
        self.assertEqual(trace[37].phase, 2)
        self.assertEqual(trace[37].timing, 5)
        for row in trace[13:38]:
            self.assertEqual((row.end.after.ab, row.end.after.pg, row.end.after.registers[0],
                              row.end.after.br, row.end.after.ir), (0x21, 1, 0x22, 0x22, 8))
            self.assertEqual(row.start.signals.db, 0xA6)
            self.assertIn(24, row.mops)
        for row in trace:
            if row.phase == 3:
                self.assertTrue(set(row.mops) <= {24, 50})
        self.assertEqual(len(sim.control.strobes), 1)
        self.assertFalse(trace[36].waiting)
        self.assertNotIn('PME', trace[38].start.signals.outputs)

    def test_low_pulse_between_t4_samples_is_not_queued(self):
        port = ControlPort(scwr=1)
        sim = machine(control=port)
        for _ in range(21):
            sim.step()
        port.scwr = 0
        sim.step()
        sim.step()
        port.scwr = 1
        for _ in range(6):
            sim.step()
        self.assertEqual((sim.trace[28].scwr, sim.trace[28].waiting), (1, True))
        port.scwr = 0
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 40)

    def test_unknown_acknowledgement_can_be_supplied_and_resumed_without_restrobing(self):
        sim = machine()
        for _ in range(20):
            sim.step()
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'known /SCWR'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(len(sim.control.strobes), 1)
        self.assertEqual(sim.control.value, 0xA6)
        sim.control.scwr = 0
        resumed = sim.resume_instruction()
        self.assertEqual(len(resumed), 4)
        self.assertEqual(len(sim.trace), 24)
        self.assertEqual(len(sim.control.strobes), 1)

    def test_run_guard_preserves_waiting_progress_and_resumption(self):
        sim = machine(control=ControlPort(scwr=1))
        with self.assertRaises(InstructionLimit):
            sim.run_instruction(max_slots=28)
        self.assertEqual((sim.state.phase, sim.state.timing, sim.state.wait), (3, 4, 1))
        self.assertEqual(len(sim.trace), 28)
        self.assertEqual(len(sim.control.strobes), 1)
        sim.control.scwr = 0
        resumed = sim.resume_instruction()
        self.assertEqual(len(resumed), 4)
        self.assertEqual(len(sim.trace), 32)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertEqual(len(sim.control.strobes), 1)

    def test_unacknowledged_control_is_a_persistent_wait_not_a_completed_halt(self):
        sim = machine(control=ControlPort(scwr=1))
        with self.assertRaises(InstructionLimit):
            sim.run_instruction(max_slots=40)
        self.assertEqual(sim.state.phase, 3)
        self.assertEqual(sim.state.wait, 1)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertIn('PME', sim.trace[-1].start.signals.outputs)
        self.assertNotIn(30, sim.trace[-1].mops)

    def test_partial_ordinary_instruction_can_also_be_resumed(self):
        sim = machine(0, value=1)
        with self.assertRaises(InstructionLimit):
            sim.run_instruction(max_slots=3)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 8)
        for budget in (0, -1, True):
            with self.assertRaises(ModelError):
                sim.run_instruction(max_slots=budget)
        with self.assertRaises(ModelError):
            sim.resume_instruction()

    def test_control_byte_must_be_ready_at_strobe_not_at_f1t5(self):
        sim = machine(9)
        for _ in range(8):
            sim.step()
        sim.memory.program_delay = 5
        for _ in range(6):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (1, 6))
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'STRCS rising'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.control.strobes, [])
        sim.memory.program_delay = 4
        sim.resume_instruction()
        self.assertEqual(sim.control.value, 0xA6)
        self.assertEqual(len(sim.control.strobes), 1)

    def test_missing_control_byte_does_not_capture_a_latch_value(self):
        sim = machine(9)
        del sim.memory.program[0x121]
        for _ in range(14):
            sim.step()
        with self.assertRaises(ModelError):
            sim.step()
        self.assertIsNone(sim.control.value)
        self.assertEqual(sim.control.strobes, [])

    def test_unstable_strobe_data_rolls_back_without_external_capture(self):
        class UnstableMemory(Memory):
            unstable = True

            def read(self, space, address, elapsed):
                value = super().read(space, address, elapsed)
                if self.unstable and address == 0x121 and elapsed > 4:
                    return value ^ 1
                return value

        sim = machine(9)
        sim.memory = UnstableMemory(program=sim.memory.program)
        for _ in range(14):
            sim.step()
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'changed during STRCS'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.control.strobes, [])
        sim.memory.unstable = False
        sim.resume_instruction()
        self.assertEqual(sim.control.value, 0xA6)

    def test_control_byte_that_encodes_ein_is_not_an_instruction(self):
        for opcode in (8, 9):
            sim = machine(opcode, value=3, control=ControlPort(scwr=0))
            sim.memory.program[0x122] = 0
            sim.run_instruction()
            trace = sim.run_instruction()
            self.assertEqual(sim.state.inte, 0)
            self.assertIsNone(trace[2].flag_effect)
            self.assertEqual(sim.control.value, 3)

    def test_following_instruction_fetches_after_both_bytes_on_the_same_page(self):
        sim = machine(control=ControlPort(ack_after=20), page=3, pc=0xFF)
        sim.memory.program[0x301] = 0
        sim.run_instruction()
        trace = sim.run_instruction()
        self.assertEqual(trace[6].instruction, 'NOP')
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (3, 2))
        self.assertEqual(sim.control.strobes[0].address, 0x300)

    def test_repeated_control_commands_each_strobe_once(self):
        port = ControlPort(ack_after=20)
        sim = machine(9, value=4, control=port)
        sim.memory.program.update({0x122: 8, 0x123: 0xA6, 0x124: 0})
        sim.run_instruction()
        sim.run_instruction()
        sim.run_instruction()
        self.assertEqual([event.value for event in port.strobes], [4, 0xA6])
        self.assertEqual([event.slot for event in port.strobes], [14, 38])
        self.assertEqual(len(sim.trace), 72)
        self.assertEqual(sim.state.registers[0], 0x25)

    def test_every_previous_opcode_retains_trace_and_memory(self):
        catalogue, _ = load_data()
        for opcode, name in validate(catalogue).items():
            if name not in PREVIOUS_SEQUENCES:
                continue
            with self.subTest(opcode=opcode):
                current = machine(opcode, value=0x80)
                current.test_inputs = (0, 0, 0, 0)
                current.state.registers[7] = 0x80
                current.memory.program[0x180] = 0xA6
                current.memory.storage[0x180] = 0x69
                current.memory.devices[0x80] = 0x5A
                previous = PreviousSimulator(PreviousState(**asdict(current.state)),
                                             PreviousMemory(**asdict(current.memory)),
                                             test_inputs=current.test_inputs)
                self.assertEqual(without_new_metadata([asdict(r) for r in current.run_instruction()]),
                                 without_new_metadata([asdict(r) for r in previous.run_instruction()]))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])
                self.assertEqual(current.control.strobes, [])

    def test_demo_captures_both_commands_and_waits_only_for_scw(self):
        from cmc8.__main__ import control_signal_demo

        sim = control_signal_demo()
        self.assertEqual(len(sim.trace), 72)
        self.assertEqual((sim.state.pg, sim.state.registers[0]), (1, 0x25))
        self.assertEqual([event.value for event in sim.control.strobes], [4, 0xA6])
        self.assertEqual([(r.phase, r.timing, r.scwr) for r in sim.trace if 50 in r.mops],
                         [(2, 4, 1), (3, 4, 1), (3, 4, 0)])


if __name__ == '__main__':
    unittest.main()
