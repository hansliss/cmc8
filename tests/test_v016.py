"""Interrupt latch/acceptance ordering, entry, return and peripheral integration."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v016 import (ControlPort, InstructionLimit, InstructionSimulator,
                                 InterruptInput, Memory, ModelError, Simulator, State,
                                 evaluate, pending_interrupt)
from cmc8.versions.v016.sequences import SEQUENCES
from cmc8.versions.v015 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v015 import ControlPort as PreviousControl
from cmc8.versions.v015 import Memory as PreviousMemory, State as PreviousState
from cmc8.versions.v015.sequences import SEQUENCES as PREVIOUS_SEQUENCES
from tools.build_instruction_reference import load_data, validate


def machine(*, n=0, page=1, pc=0x20, inte=1, intr=0, level=1, program=None, control=None):
    state = State(n=n, pg=page, inte=inte, intr=intr, inta=0, link=1, z=0,
                  h=0, t=1, br=0xA6, ab=0x80, ir=0)
    state.registers = [0x90 + i for i in range(8)]
    state.registers[n] = pc
    memory = Memory(program=program if program is not None else {(page << 8) | pc: 0})
    return InstructionSimulator(state, memory, interrupts=InterruptInput(level), control=control)


def without_new_metadata(value):
    if isinstance(value, dict):
        return {key: without_new_metadata(item) for key, item in value.items()
                if key not in {'version', 'int_level', 'inta_input', 'interrupt_accepted'}}
    if isinstance(value, (tuple, list)):
        return [without_new_metadata(item) for item in value]
    return value


class InterruptDatapathTests(unittest.TestCase):
    def test_request_set_gate_and_latch_truth_table(self):
        for inte in (0, 1):
            for intr in (0, 1):
                for level in (0, 1):
                    self.assertEqual(pending_interrupt(intr, inte, level),
                                     intr | (inte & (1 - level)))
        self.assertEqual(pending_interrupt(1, None, None), 1)
        self.assertEqual(pending_interrupt(0, 0, None), 0)
        self.assertEqual(pending_interrupt(0, None, 1), 0)
        self.assertIsNone(pending_interrupt(0, 1, None))
        self.assertIsNone(pending_interrupt(None, 0, 1))
        self.assertEqual(pending_interrupt(None, 1, 0), 1)
        for args in ((2, 0, 1), (0, False, 1), (0, 1, -1)):
            with self.assertRaises(ModelError):
                pending_interrupt(*args)

    def test_acceptance_samples_request_before_entry_clear(self):
        cpu = Simulator(State(phase=0, timing=0, inte=1, intr=1, inta=0))
        controls = (28, 39, 46)
        start = cpu.capture(controls, observe_int=True, int_level=0, point='start')
        self.assertEqual(start.signals.inta_input, 1)
        self.assertEqual((start.after.inta, start.after.inte, start.after.intr), (1, 0, 0))
        end = cpu.capture(controls, observe_int=True, int_level=0, point='end')
        self.assertEqual(end.signals.inta_input, 0)  # Not another sampling edge.
        self.assertEqual((end.after.inta, end.after.intr), (1, 0))

    def test_enabling_with_low_int_sets_request_but_does_not_clock_inta(self):
        cpu = Simulator(State(phase=0, timing=2, inte=0, intr=0, inta=0))
        row = cpu.capture((38,), observe_int=True, int_level=0)
        self.assertEqual((row.after.inte, row.after.intr, row.after.inta), (1, 1, 0))

    def test_mop28_requires_known_request_and_f0t0(self):
        with self.assertRaisesRegex(ModelError, 'known INTR'):
            evaluate(State(phase=0, timing=0, intr=None), (28,))
        for phase, timing in ((0, 1), (1, 0), (3, 0)):
            with self.assertRaisesRegex(ModelError, 'only at F0T0'):
                evaluate(State(phase=phase, timing=timing, intr=0), (28,))


class InterruptIntegrationTests(unittest.TestCase):
    def test_pulse_between_steps_is_latched_without_advancing_clock(self):
        sim = machine()
        first = sim.set_interrupt(0)
        sim.set_interrupt(1)
        self.assertEqual(first.after.intr, 1)
        self.assertEqual(sim.state.intr, 1)
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))
        self.assertEqual(sim.trace, [])
        trace = sim.run_instruction()
        self.assertTrue(trace[0].interrupt_accepted)
        self.assertEqual(len(trace), 8)

    def test_masked_pulse_is_not_queued(self):
        sim = machine(inte=0)
        sim.set_interrupt(0)
        sim.set_interrupt(1)
        self.assertEqual(sim.state.intr, 0)
        sim.run_instruction()
        self.assertEqual(sim.state.n, 0)
        self.assertFalse(any(row.interrupt_accepted for row in sim.trace))

    def test_entry_all_pc_selectors_pages_and_pending_request_with_either_enable(self):
        for n in range(8):
            for page in range(4):
                for inte in (0, 1):
                    sim = machine(n=n, page=page, inte=inte, intr=1, program={})
                    expected = list(sim.state.registers)
                    expected[(n + 1) & 7] = 2
                    memory = asdict(sim.memory)
                    trace = sim.run_instruction()
                    self.assertEqual(sim.state.registers, expected)
                    self.assertEqual((sim.state.n, sim.state.pg), ((n + 1) & 7, page))
                    self.assertEqual((sim.state.inte, sim.state.intr, sim.state.inta), (0, 0, 1))
                    self.assertEqual((sim.state.link, sim.state.z, sim.state.ab, sim.state.br),
                                     (1, 0, 0x80, 0xA6))
                    self.assertEqual(asdict(sim.memory), memory)
                    self.assertEqual([(r.phase, r.timing) for r in trace], [(0, t) for t in range(8)])
                    self.assertTrue(all(row.instruction == 'INTERRUPT' for row in trace))
                    self.assertTrue(all(not ({1, 2, 24, 25, 26, 27} & set(row.mops)) for row in trace))

    def test_entry_landmarks_and_real_first_handler_fetch_use_current_page(self):
        sim = machine(page=2, intr=1, program={0x202: 0, 0x002: 1})
        entry = sim.run_instruction()
        self.assertEqual(entry[0].mops, (28, 39, 46))
        self.assertEqual((entry[0].start.after.inta, entry[0].start.after.inte,
                          entry[0].start.after.intr), (1, 0, 0))
        self.assertEqual(entry[1].start.signals.di, 2)
        self.assertEqual(entry[2].start.after.n, 1)
        self.assertEqual(entry[3].start.after.registers[1], 0x91)
        self.assertEqual(entry[4].start.after.registers[1], 2)
        fetch = sim.run_instruction()
        self.assertEqual(fetch[0].start.after.inta, 0)
        self.assertEqual(fetch[6].instruction, 'NOP')
        self.assertEqual((sim.state.pg, sim.state.registers[1]), (2, 3))

    def test_request_during_instruction_does_not_preempt_it(self):
        sim = machine(program={0x120: 0x23, 0x121: 0xA6})
        for _ in range(10):
            sim.step()
        sim.set_interrupt(0)
        sim.set_interrupt(1)
        self.assertEqual(sim.state.intr, 1)
        sim.resume_instruction()
        self.assertEqual((sim.state.registers[3], sim.state.registers[0]), (0xA6, 0x22))
        self.assertEqual(sim.state.n, 0)
        entry = sim.run_instruction()
        self.assertEqual(entry[0].instruction, 'INTERRUPT')
        self.assertEqual(sim.state.registers[0], 0x22)

    def test_request_between_exchange_writes_does_not_split_the_exchange(self):
        sim = machine(program={0x120: 0xBB})
        sim.state.registers[3], sim.state.registers[7] = 0x80, 0xA6
        for _ in range(21):
            sim.step()  # EXR has written R3 but not yet restored old R3 to X.
        sim.set_interrupt(0)
        sim.set_interrupt(1)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[3], 0xA6)
        self.assertEqual(sim.state.registers[7], 0x80)
        self.assertEqual(sim.state.n, 0)
        sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.registers[0]), (1, 0x21))

    def test_wrapped_n_returns_to_the_saved_pc_without_a_hidden_stack(self):
        sim = machine(n=7, page=3, intr=1, program={0x302: 0x0F})
        sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.registers[0]), (0, 2))
        sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[7]), (7, 3, 0x20))

    def test_ein_guarantees_following_nop_before_accepting_held_request(self):
        sim = machine(inte=0, level=0, program={0x120: 3, 0x121: 0})
        ein = sim.run_instruction()
        self.assertEqual((sim.state.inte, sim.state.intr), (0, 0))
        following = sim.run_instruction()
        self.assertEqual(following[0].start.after.inta, 0)
        self.assertEqual((following[2].start.after.inte, following[2].start.after.intr), (1, 1))
        self.assertEqual(following[6].instruction, 'NOP')
        self.assertEqual(sim.state.registers[0], 0x22)
        entry = sim.run_instruction()
        self.assertTrue(entry[0].interrupt_accepted)
        self.assertEqual(len(ein) + len(following) + len(entry), 24)

    def test_ein_rsr_finishes_return_before_a_reenabled_request_is_accepted(self):
        sim = machine(inte=1, intr=1, level=0,
                      program={0x102: 3, 0x103: 0x0F, 0x120: 0})
        sim.run_instruction()  # First entry, N=1, saved R0=20.
        sim.run_instruction()  # Handler EIN.
        rsr = sim.run_instruction()
        self.assertEqual(rsr[0].start.after.inta, 0)
        self.assertEqual((rsr[2].start.after.inte, rsr[2].start.after.intr), (1, 1))
        self.assertEqual((sim.state.n, sim.state.registers[0]), (0, 0x20))
        entry = sim.run_instruction()
        self.assertTrue(entry[0].interrupt_accepted)
        self.assertEqual(sim.state.n, 1)  # Not N=2: RSR already restored N.
        self.assertEqual(sim.state.registers[0], 0x20)

    def test_rsr_alone_does_not_unmask_or_relatch_held_int(self):
        sim = machine(intr=1, level=0, program={0x102: 0x0F, 0x120: 0})
        sim.run_instruction()
        sim.run_instruction()
        self.assertEqual((sim.state.n, sim.state.inte, sim.state.intr), (0, 0, 0))
        following = sim.run_instruction()
        self.assertEqual(following[6].instruction, 'NOP')
        self.assertFalse(following[0].interrupt_accepted)

    def test_pending_request_survives_deferred_din_mask(self):
        sim = machine(program={0x120: 2, 0x121: 0})
        sim.run_instruction()  # DIN, whose effect is still deferred.
        sim.step()            # Following fetch T0 samples no request.
        sim.set_interrupt(0)
        sim.set_interrupt(1)  # Latch request while enable is still high.
        sim.resume_instruction()
        self.assertEqual((sim.state.inte, sim.state.intr), (0, 1))
        self.assertEqual(sim.state.registers[0], 0x22)
        entry = sim.run_instruction()
        self.assertTrue(entry[0].interrupt_accepted)

    def test_explicit_reenable_can_allow_nested_interrupts(self):
        sim = machine(intr=1, level=0, program={0x102: 3, 0x103: 0})
        sim.run_instruction()  # Entry to N=1.
        sim.run_instruction()  # EIN.
        sim.run_instruction()  # NOP; EIN takes effect and request latches.
        sim.run_instruction()  # Nested entry to N=2.
        self.assertEqual((sim.state.n, sim.state.registers[1], sim.state.registers[2]), (2, 4, 2))
        self.assertEqual(sum(row.interrupt_accepted for row in sim.trace), 2)

    def test_consecutive_ein_exposes_retained_ir_edge_case_without_hidden_suppression(self):
        # This records the selected IR-only hypothesis, not a proven silicon case.
        sim = machine(inte=0, level=0, program={0x120: 3, 0x121: 3, 0x102: 0})
        sim.run_instruction()
        sim.run_instruction()
        entry = sim.run_instruction()
        self.assertTrue(entry[0].interrupt_accepted)
        self.assertEqual(sim.state.inte, 0)
        self.assertTrue(all(row.flag_effect is None for row in entry))
        handler = sim.run_instruction()
        self.assertEqual(handler[2].flag_effect.name, 'EIN')
        self.assertEqual((sim.state.inte, sim.state.intr), (1, 1))

    def test_interrupt_request_waits_for_scw_acknowledgement_and_completion(self):
        sim = machine(program={0x120: 8, 0x121: 0xA6}, control=ControlPort(scwr=1))
        with self.assertRaises(InstructionLimit):
            sim.run_instruction(max_slots=24)
        self.assertEqual(sim.state.phase, 3)
        sim.set_interrupt(0)
        sim.set_interrupt(1)
        for _ in range(8):
            sim.step()
        self.assertEqual(sim.state.n, 0)
        self.assertEqual(sim.state.phase, 3)
        sim.control.scwr = 0
        sim.resume_instruction()
        self.assertEqual(sim.state.intr, 1)
        self.assertEqual(len(sim.control.strobes), 1)
        entry = sim.run_instruction()
        self.assertTrue(entry[0].interrupt_accepted)
        self.assertEqual(sim.state.registers[0], 0x22)

    def test_pending_edge_at_final_slot_is_taken_only_at_next_boundary(self):
        sim = machine(program={0x120: 0})
        for _ in range(7):
            sim.step()
        sim.set_interrupt(0)
        sim.set_interrupt(1)
        last = sim.step()
        self.assertFalse(last.interrupt_accepted)
        self.assertEqual(sim.state.n, 0)
        entry = sim.run_instruction()
        self.assertTrue(entry[0].interrupt_accepted)
        self.assertEqual(sim.state.registers[0], 0x21)

    def test_unknown_initial_request_is_not_assumed_clear(self):
        sim = machine(inte=0)
        sim.state.intr = None
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'initialize it explicitly'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.trace, [])

    def test_unknown_pin_is_harmless_while_disabled_but_not_while_enabled(self):
        sim = machine(inte=0, level=None)
        sim.run_instruction()
        self.assertEqual(sim.state.intr, 0)
        sim = machine(inte=1, level=None)
        with self.assertRaises(ModelError):
            sim.step()

    def test_bad_input_change_is_atomic_and_optional_integration_is_explicit(self):
        sim = machine()
        before = deepcopy(sim.state)
        with self.assertRaises(ModelError):
            sim.set_interrupt(False)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.interrupts.level, 1)
        plain = InstructionSimulator(State(n=0), Memory())
        with self.assertRaisesRegex(ModelError, 'Provide InterruptInput'):
            plain.set_interrupt(0)

    def test_no_automatic_page_or_flag_stack_is_added(self):
        sim = machine(page=2, intr=1, program={0x202: 0xF1, 0x203: 0x40, 0x140: 0x0F})
        sim.run_instruction()  # Entry leaves PG=2.
        sim.run_instruction()  # Handler JMP changes PG=1.
        sim.run_instruction()  # RSR restores N but leaves PG=1.
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 1, 0x20))

    def test_entry_can_be_resumed_after_host_limit(self):
        sim = machine(intr=1)
        with self.assertRaises(InstructionLimit):
            sim.run_instruction(max_slots=3)
        self.assertEqual(sim.state.n, 1)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 8)
        self.assertEqual(sim.state.registers[1], 2)
        self.assertEqual(sum(row.interrupt_accepted for row in sim.trace), 1)

    def test_all_old_opcodes_remain_compatible_without_interrupt_integration(self):
        catalogue, _ = load_data()
        for opcode, name in validate(catalogue).items():
            with self.subTest(opcode=opcode):
                state = State(n=0, pg=1, link=1, z=0, inte=0, intr=0, inta=0)
                state.registers = [0x90 + i for i in range(8)]
                state.registers[0], state.registers[7] = 0x20, 0x80
                memory = Memory(program={0x120: opcode, 0x121: 0x80, 0x180: 0xA6},
                                storage={0x180: 0x69}, devices={0x80: 0x5A})
                current = InstructionSimulator(state, memory, control=ControlPort(scwr=0),
                                               test_inputs=(0, 0, 0, 0))
                previous = PreviousSimulator(PreviousState(**asdict(state)),
                                             PreviousMemory(**asdict(memory)),
                                             control=PreviousControl(scwr=0), test_inputs=(0, 0, 0, 0))
                self.assertEqual(without_new_metadata([asdict(r) for r in current.run_instruction()]),
                                 without_new_metadata([asdict(r) for r in previous.run_instruction()]))
                self.assertEqual(asdict(current.memory), asdict(previous.memory))
                self.assertEqual(asdict(current.control), asdict(previous.control))
                self.assertEqual(SEQUENCES[name], PREVIOUS_SEQUENCES[name])

    def test_every_opcode_has_the_same_effect_with_a_quiet_interrupt_input(self):
        catalogue, _ = load_data()
        for opcode in validate(catalogue):
            with self.subTest(opcode=opcode):
                sim = machine(program={0x120: opcode, 0x121: 0x80, 0x180: 0xA6},
                              inte=0, control=ControlPort(scwr=0))
                sim.test_inputs = (0, 0, 0, 0)
                sim.state.registers[7] = 0x80
                sim.memory.storage[0x180] = 0x69
                sim.memory.devices[0x80] = 0x5A
                baseline = PreviousSimulator(PreviousState(**asdict(sim.state)),
                                             PreviousMemory(**asdict(sim.memory)),
                                             control=PreviousControl(scwr=0),
                                             test_inputs=sim.test_inputs)
                trace = sim.run_instruction()
                baseline.run_instruction()
                self.assertEqual(asdict(sim.state), asdict(baseline.state))
                self.assertEqual(asdict(sim.memory), asdict(baseline.memory))
                self.assertEqual(asdict(sim.control), asdict(baseline.control))
                self.assertFalse(any(row.interrupt_accepted for row in trace))

    def test_demo_completes_handler_and_resumes_main_program(self):
        from cmc8.__main__ import interrupt_demo

        sim = interrupt_demo()
        self.assertEqual(len(sim.trace), 80)
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 1, 0x24))
        self.assertEqual(sim.state.registers[3:5], [0xA6, 0x69])
        self.assertEqual((sim.state.inte, sim.state.intr, sim.state.inta), (1, 0, 0))
        entries = [i for i, row in enumerate(sim.trace) if row.interrupt_accepted]
        self.assertEqual(entries, [16])
        self.assertEqual(sim.trace[10].flag_effect.name, 'EIN')


if __name__ == '__main__':
    unittest.main()
