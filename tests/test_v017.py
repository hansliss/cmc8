"""Synchronous T7 reset sampling, sourced reset landmarks and integration."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v017 import (ControlPort, InstructionLimit, InstructionSimulator, InterruptInput,
                                 Memory, ModelError, ResetInput, Simulator, State, evaluate)
from cmc8.versions.v016 import (ControlPort as OldControl, InstructionSimulator as OldSimulator,
                                 Memory as OldMemory, State as OldState)
from tools.build_instruction_reference import load_data, validate


def machine(*, opcode=0, reset_level=1, reset_sampled=False, interrupts=None, control=None):
    state = State(n=3, pg=2, ir=0, inte=1, intr=0, inta=1, link=1, z=1,
                  wait=0, sse=1, h=1, t=1, alu_a=0xA6, ab=0x80, br=0x69)
    state.registers = [0x90+i for i in range(8)]
    state.registers[3], state.registers[7] = 0x20, 0x80
    return InstructionSimulator(state, Memory(program={0x220: opcode, 0x221: 0x80,
                                                       0x280: 0xA6, 0: 0},
                                               storage={0x280: 0x69}, devices={0x80: 0x5A}),
                                reset=ResetInput(reset_level), reset_sampled=reset_sampled,
                                interrupts=interrupts, control=control)


def normalized(value):
    """Remove only added trace metadata and the quiet reset sampling control."""
    if isinstance(value, dict):
        return {key: (tuple(m for m in item if m != 47) if key == 'mops' else normalized(item))
                for key, item in value.items()
                if key not in {'version', 'reset_request', 'reset_level', 'clear_inta',
                               'reset_sampled', 'reset_cycle'}}
    if isinstance(value, (tuple, list)):
        return [normalized(item) for item in value]
    return value


class ResetDatapathTests(unittest.TestCase):
    def test_mop47_gate_is_t7_only_and_requires_a_known_level(self):
        for phase in range(4):
            for level in (0, 1):
                row = evaluate(State(phase=phase, timing=7), (47,), reset_level=level)
                self.assertEqual(row.reset_request, 1-level)
                self.assertEqual(row.writes, {})
        for timing in range(7):
            with self.assertRaisesRegex(ModelError, 'only at T7'):
                evaluate(State(timing=timing), (47,), reset_level=0)
        with self.assertRaisesRegex(ModelError, 'known RESET'):
            evaluate(State(timing=7), (47,))

    def test_inta_clear_does_not_sample_pending_interrupt(self):
        state = State(phase=0, timing=0, inta=1, inte=1, intr=1)
        row = Simulator(state).capture((42,), clear_inta=True)
        self.assertEqual(row.after.inta, 0)
        self.assertEqual((row.after.inte, row.after.intr, row.after.pg), (1, 1, 0))
        with self.assertRaises(ModelError):
            evaluate(state, (28,), clear_inta=True)
        with self.assertRaises(ModelError):
            evaluate(State(phase=0, timing=1), (), clear_inta=True)


class ResetIntegrationTests(unittest.TestCase):
    def test_unknown_power_on_state_can_start_after_an_explicit_prior_t7_sample(self):
        sim = InstructionSimulator(State(), Memory(program={0: 0}),
                                   reset=ResetInput(1), reset_sampled=True)
        trace = sim.run_instruction()
        self.assertEqual(len(trace), 8)
        self.assertTrue(all(row.instruction == 'RESET' for row in trace))
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0], sim.state.inta),
                         (0, 0, 0, 0))
        self.assertEqual(sim.state.registers[1:], [None]*7)
        for field in ('ir', 'br', 'ab', 'inte', 'intr', 'link', 'z', 'sse', 'wait', 'alu_a'):
            self.assertIsNone(getattr(sim.state, field), field)
        sim.run_instruction()
        self.assertEqual(sim.state.registers[0], 1)

    def test_source_landmarks_and_only_documented_storage_is_cleared(self):
        for n in range(8):
            for pg in range(4):
                sim = machine(reset_sampled=True)
                sim.state.n, sim.state.pg = n, pg
                before = deepcopy(sim.state)
                memory = deepcopy(sim.memory)
                trace = sim.run_instruction()
                self.assertEqual(trace[0].mops, (42,))
                self.assertTrue(trace[0].start.signals.clear_inta)
                self.assertEqual((trace[0].start.after.inta, trace[0].start.after.pg), (0, 0))
                self.assertEqual(trace[1].start.signals.di, 0)
                self.assertEqual(trace[2].start.after.n, 0)
                self.assertEqual(trace[3].start.after.registers[0], before.registers[0])
                self.assertEqual(trace[4].start.after.registers[0], 0)
                self.assertTrue(all(row.reset_cycle for row in trace))
                expected = deepcopy(before)
                expected.n, expected.pg, expected.inta = 0, 0, 0
                expected.registers[0] = 0
                expected.phase, expected.timing = 0, 0
                self.assertEqual(sim.state, expected)
                self.assertEqual(sim.memory, memory)
                self.assertEqual(sim.control.strobes, [])
                self.assertTrue(all(not ({1, 2, 24, 25, 26, 27} & set(row.mops)) for row in trace))

    def test_low_pulse_outside_t7_is_not_latched(self):
        sim = machine()
        sim.set_reset(0)
        for _ in range(7):
            sim.step()
        sim.set_reset(1)
        sim.resume_instruction()
        self.assertFalse(any(row.reset_sampled for row in sim.trace))
        self.assertEqual((sim.state.n, sim.state.pg), (3, 2))
        sim.memory.program[0x221] = 0
        self.assertEqual(sim.run_instruction()[6].instruction, 'NOP')

    def test_sample_is_retained_after_pin_returns_high(self):
        sim = machine()
        for _ in range(7):
            sim.step()
        sim.set_reset(0)
        sample = sim.step()
        self.assertTrue(sample.reset_sampled)
        self.assertEqual((sim.state.n, sim.state.pg), (3, 2))
        sim.set_reset(1)
        self.assertEqual(sim.run_instruction()[0].instruction, 'RESET')
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 0, 0))
        sim.run_instruction()
        self.assertEqual(sim.state.registers[0], 1)

    def test_held_reset_repeats_cycles_without_fetch_or_extra_side_effects(self):
        sim = machine(reset_level=0, reset_sampled=True)
        for _ in range(3):
            trace = sim.run_instruction()
            self.assertTrue(trace[-1].reset_sampled)
            self.assertEqual(sim.state.registers[0], 0)
            self.assertEqual(sim.state.ir, 0)
        sim.set_reset(1)
        self.assertEqual(sim.run_instruction()[0].instruction, 'RESET')
        self.assertEqual(sim.run_instruction()[6].instruction, 'NOP')

    def test_reset_interrupts_a_multicycle_instruction_after_fetch(self):
        sim = machine(opcode=0x23, reset_level=0)  # LRI R3,80; destination aliases PC.
        trace = sim.run_instruction()
        self.assertEqual(len(trace), 8)
        self.assertEqual(sim.state.registers[3], 0x21)
        sim.set_reset(1)
        sim.run_instruction()
        self.assertEqual(sim.state.registers[3], 0x21)
        self.assertEqual(sim.state.registers[0], 0)

    def test_reset_after_operand_cycle_prevents_store_without_undoing_pc_increment(self):
        sim = machine(opcode=0x73)  # SRS R3,80.
        for _ in range(15):
            sim.step()
        sim.set_reset(0)
        sim.step()
        sim.set_reset(1)
        trace = sim.run_instruction()
        self.assertEqual(trace[0].instruction, 'RESET')
        self.assertEqual(sim.state.registers[3], 0x22)
        self.assertEqual(sim.memory.storage[0x280], 0x69)
        self.assertFalse(any(row.memory_write for row in sim.trace))

    def test_reset_after_store_commit_preserves_external_write(self):
        sim = machine(opcode=0x73)
        for _ in range(23):
            sim.step()
        self.assertEqual(sim.memory.storage[0x280], 0x22)
        sim.set_reset(0)
        sim.step()
        sim.set_reset(1)
        sim.run_instruction()
        self.assertEqual(sim.memory.storage[0x280], 0x22)

    def test_reset_escapes_scwr_wait_without_clearing_peripheral_or_restrobing(self):
        sim = machine(opcode=8, control=ControlPort(scwr=1))
        for _ in range(31):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (3, 7))
        self.assertEqual(len(sim.control.strobes), 1)
        sim.set_reset(0)
        sim.step()
        sim.set_reset(1)
        trace = sim.run_instruction()
        self.assertEqual(trace[0].instruction, 'RESET')
        self.assertEqual(sim.control.value, 0x80)
        self.assertEqual(len(sim.control.strobes), 1)
        self.assertEqual(sim.state.wait, 1)  # No printed WAIT clear.
        sim.run_instruction()
        self.assertEqual(sim.state.wait, 0)  # Ordinary fetch's ready check.

    def test_reset_selection_precedes_irq_without_silently_clearing_the_request(self):
        sim = machine(reset_sampled=True, interrupts=InterruptInput(1))
        sim.state.intr = 1
        trace = sim.run_instruction()
        self.assertEqual(trace[0].instruction, 'RESET')
        self.assertEqual((sim.state.inte, sim.state.intr, sim.state.inta), (1, 1, 0))
        entry = sim.run_instruction()
        self.assertEqual(entry[0].instruction, 'INTERRUPT')
        self.assertEqual((sim.state.n, sim.state.registers[0], sim.state.registers[1]), (1, 0, 2))

    def test_reset_can_be_sampled_during_irq_entry(self):
        sim = machine(reset_level=0, interrupts=InterruptInput(1))
        sim.state.intr = 1
        self.assertEqual(sim.run_instruction()[0].instruction, 'INTERRUPT')
        sim.set_reset(1)
        self.assertEqual(sim.run_instruction()[0].instruction, 'RESET')
        self.assertEqual((sim.state.inta, sim.state.n, sim.state.pg), (0, 0, 0))

    def test_reset_does_not_initialize_unknown_interrupt_enable_or_request(self):
        sim = InstructionSimulator(State(), Memory(), reset=ResetInput(1),
                                   reset_sampled=True, interrupts=InterruptInput(1))
        sim.run_instruction()
        self.assertIsNone(sim.state.inte)
        self.assertIsNone(sim.state.intr)
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'known INTR'):
            sim.step()
        self.assertEqual(sim.state, before)

    def test_retained_ein_can_reenable_after_reset_under_the_existing_ir_model(self):
        sim = machine(opcode=3, reset_level=0)
        sim.state.inte = 0
        sim.run_instruction()  # EIN fetched, reset sampled before its deferred effect.
        sim.set_reset(1)
        reset = sim.run_instruction()
        self.assertTrue(all(row.flag_effect is None for row in reset))
        self.assertEqual(sim.state.inte, 0)
        following = sim.run_instruction()
        self.assertEqual(following[2].flag_effect.name, 'EIN')
        self.assertEqual(sim.state.inte, 1)

    def test_unknown_reset_at_t7_rolls_back_and_retry_samples_once(self):
        sim = machine(reset_level=None)
        for _ in range(7):
            sim.step()
        before = deepcopy(sim.state)
        with self.assertRaisesRegex(ModelError, 'known RESET'):
            sim.step()
        self.assertEqual(sim.state, before)
        self.assertEqual(len(sim.trace), 7)
        sim.set_reset(0)
        self.assertTrue(sim.step().reset_sampled)
        sim.set_reset(1)
        self.assertEqual(sim.run_instruction()[0].instruction, 'RESET')

    def test_partial_reset_error_restores_pending_controller_selection(self):
        sim = machine(reset_sampled=True)
        sim.state.pg = 4  # Deliberately invalid experiment state at entry.
        with self.assertRaises(ModelError):
            sim.step()
        sim.state.pg = 2
        self.assertEqual(sim.run_instruction()[0].instruction, 'RESET')

    def test_pin_validation_and_explicit_bootstrap_contract(self):
        for level in (False, 2, -1):
            with self.assertRaises(ModelError):
                ResetInput(level)
        sim = machine()
        before = deepcopy(sim.state)
        with self.assertRaises(ModelError):
            sim.set_reset(False)
        self.assertEqual(sim.reset.level, 1)
        self.assertEqual(sim.state, before)
        plain = InstructionSimulator(State(), Memory())
        with self.assertRaises(ModelError):
            plain.set_reset(0)
        with self.assertRaises(ModelError):
            InstructionSimulator(State(), Memory(), reset_sampled=True)

    def test_all_opcodes_match_v016_with_reset_off_or_quiet(self):
        catalogue, _ = load_data()
        for opcode in validate(catalogue):
            for enabled in (False, True):
                with self.subTest(opcode=opcode, reset=enabled):
                    sim = machine(opcode=opcode, control=ControlPort(scwr=0))
                    sim.test_inputs = (0, 1, 0, 1)
                    if not enabled:
                        sim.reset = None
                    old = OldSimulator(OldState(**asdict(sim.state)), OldMemory(**asdict(sim.memory)),
                                       test_inputs=sim.test_inputs, control=OldControl(scwr=0))
                    actual = sim.run_instruction()
                    expected = old.run_instruction()
                    self.assertEqual(normalized([asdict(row) for row in actual]),
                                     normalized([asdict(row) for row in expected]))
                    self.assertEqual(asdict(sim.state), asdict(old.state))
                    self.assertEqual(asdict(sim.memory), asdict(old.memory))
                    self.assertEqual(asdict(sim.control), asdict(old.control))

    def test_each_opcode_can_be_replaced_at_each_of_its_machine_cycle_boundaries(self):
        catalogue, _ = load_data()
        for opcode in validate(catalogue):
            baseline = machine(opcode=opcode, control=ControlPort(scwr=0))
            baseline.test_inputs = (0, 1, 0, 1)
            ordinary = baseline.run_instruction()
            for end in range(8, len(ordinary)+1, 8):
                with self.subTest(opcode=opcode, end=end):
                    sim = machine(opcode=opcode, control=ControlPort(scwr=0))
                    sim.test_inputs = (0, 1, 0, 1)
                    for _ in range(end-1):
                        sim.step()
                    sim.set_reset(0)
                    self.assertTrue(sim.step().reset_sampled)
                    sim.set_reset(1)
                    expected = deepcopy(sim.state)
                    memory, control = deepcopy(sim.memory), deepcopy(sim.control)
                    expected.n, expected.pg, expected.inta = 0, 0, 0
                    expected.registers[0] = 0
                    event = sim.run_instruction()
                    self.assertTrue(all(row.reset_cycle for row in event))
                    self.assertEqual(sim.state, expected)
                    self.assertEqual(sim.memory, memory)
                    self.assertEqual(sim.control, control)
                    # The abandoned instruction must not resume after reset.
                    next_event = sim.run_instruction()
                    self.assertEqual(next_event[6].instruction, 'NOP')
                    self.assertEqual(sim.state.n, 0)
                    self.assertEqual(sim.state.pg, 0)
                    self.assertEqual(sim.state.registers[0], 1)

    def test_reset_cycle_can_be_resumed_after_host_budget_without_reselection(self):
        sim = machine(reset_sampled=True)
        with self.assertRaises(InstructionLimit):
            sim.run_instruction(max_slots=3)
        self.assertEqual((sim.state.n, sim.state.timing), (0, 3))
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 8)
        self.assertTrue(all(row.instruction == 'RESET' for row in sim.trace))
        self.assertEqual(sim.state.registers[0], 0)

    def test_cli_demo_starts_program_on_page_zero(self):
        from cmc8.__main__ import reset_demo
        sim = reset_demo()
        self.assertEqual(len(sim.trace), 32)
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0],
                          sim.state.registers[3], sim.state.inta), (0, 0, 2, 0xA6, 0))
        self.assertEqual(sum(row.reset_sampled for row in sim.trace), 1)
        self.assertEqual(sum(row.reset_cycle for row in sim.trace), 8)


if __name__ == '__main__':
    unittest.main()
