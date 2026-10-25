"""Shared wait continuation, documented HALT latch and SSE handshake."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from cmc8.versions.v018 import (ControlPort, InstructionLimit, InstructionSimulator,
                                 InterruptInput, Memory, ModelError, ResetInput,
                                 RunInputs, Simulator, State, evaluate)
from cmc8.versions.v017 import (ControlPort as OldControl, InstructionSimulator as OldSimulator,
                                 Memory as OldMemory, State as OldState)
from tools.build_instruction_reference import load_data, validate


def machine(opcode=0x53, *, memr=0, halt=1, ss=1, sse=1, control=None,
            delay=0, reset=None, interrupts=None):
    state = State(n=0, pg=1, ir=0, inte=0, intr=0, inta=0, link=1, z=0,
                  h=0, t=0, sse=sse)
    state.registers = [0x20, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x80]
    memory = Memory(program={0x120: opcode, 0x121: 0x80, 0x180: 0xA6,
                             0x122: 0, 0: 0}, storage={0x180: 0x69}, devices={0x80: 0x5A},
                    program_delay=delay, storage_delay=delay, device_delay=delay)
    return InstructionSimulator(state, memory, run_inputs=RunInputs(memr=memr, halt=halt, ss=ss),
                                control=control, test_inputs=(0, 1, 0, 1),
                                reset=reset, interrupts=interrupts)


def run_with_one_wait_per_read(sim):
    """External stimulus: busy at each ordinary T4, ready in its first wait loop."""
    for _ in range(256):
        if sim.state.phase == 3 and sim.state.timing == 3:
            sim.set_run_inputs(memr=0)
        elif sim.state.phase != 3 and sim.state.timing == 4:
            sim.set_run_inputs(memr=1)
        sim.step()
        if (sim.state.phase, sim.state.timing) == (0, 0):
            return sim.trace
    raise AssertionError('Stimulated instruction did not finish')


def architecture(state):
    return {name: value for name, value in asdict(state).items()
            if name not in {'halt'}}


class WaitDatapathTests(unittest.TestCase):
    def test_memr_and_halt_or_gate_at_t4_and_output_mask(self):
        for ready in (False, True):
            for halt in (0, 1):
                signal = evaluate(State(timing=4, wait=1), (29,),
                                  memory_ready=ready, halt_wait=halt)
                self.assertEqual(signal.writes['wait'], int(not ready or halt))
                self.assertEqual(signal.wait_pin, 1)
        self.assertEqual(evaluate(State(timing=5, wait=1), ()).wait_pin, 0)
        self.assertEqual(evaluate(State(timing=3, wait=0), ()).wait_pin, 1)
        self.assertEqual(evaluate(State(timing=4), (29,), memory_ready=None,
                                  halt_wait=1).writes['wait'], 1)
        with self.assertRaises(ModelError):
            evaluate(State(timing=4), (29,), memory_ready=None)
        with self.assertRaises(ModelError):
            evaluate(State(timing=3), (29,), memory_ready=False)

    def test_halt_latch_set_window_and_asynchronous_release(self):
        cpu = Simulator(State(phase=0, timing=2, halt=0))
        cpu.capture((), observe_halt=True, halt_level=0, halt_set=True)
        self.assertEqual(cpu.state.halt, 1)
        cpu.capture((), observe_halt=True, halt_level=0)
        self.assertEqual(cpu.state.halt, 1)
        cpu.capture((), observe_halt=True, halt_level=1)
        self.assertEqual(cpu.state.halt, 0)
        cpu.capture((), observe_halt=True, halt_level=0)
        self.assertEqual(cpu.state.halt, 0)


class MemoryWaitTests(unittest.TestCase):
    def test_figure_4_16_one_wait_in_each_lrs_phase(self):
        sim = machine(delay=8)
        trace = run_with_one_wait_per_read(sim)
        self.assertEqual(len(trace), 48)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertEqual(sim.state.registers[3], 0x69)
        entries = [r for r in trace if r.timing == 4 and r.end.after.wait == 1]
        self.assertEqual([r.resume_phase for r in entries], [0, 1, 2])
        self.assertEqual([r.mops for r in entries], [(29, 24), (29, 24), (29, 25)])
        for r in entries[:2]:
            self.assertNotIn(22, r.mops)
            self.assertEqual(r.start.before.registers[0], r.end.after.registers[0])
        for phase in (0, 1, 2):
            paused = [r for r in trace if r.phase == 3 and r.resume_phase == phase]
            self.assertEqual(len(paused), 8)
            self.assertFalse(any(1 in r.mops or 2 in r.mops for r in paused))
            self.assertTrue(all(r.start.signals.wait_pin == 1 for r in paused if r.timing == 4))
        self.assertEqual(sum(12 in r.mops for r in trace), 2)

    def test_every_encoding_waits_for_each_external_read_and_retains_its_result(self):
        catalogue, _ = load_data()
        entries = {e['mnemonic']: e for e in catalogue['instructions']}
        loads = {'LRS', 'LRM', 'LRD', 'LRX', 'LSX'}
        for opcode, name in validate(catalogue).items():
            with self.subTest(opcode=opcode):
                baseline = machine(opcode, control=ControlPort(scwr=0))
                ordinary = baseline.run_instruction()
                sim = machine(opcode, delay=8, control=ControlPort(scwr=0))
                trace = run_with_one_wait_per_read(sim)
                reads = 1 + int(entries[name]['length_bytes'] == 2) + int(name in loads)
                self.assertEqual(len(trace), len(ordinary)+8*reads)
                self.assertEqual(architecture(sim.state), architecture(baseline.state))
                for space in ('program', 'storage', 'devices'):
                    self.assertEqual(getattr(sim.memory, space), getattr(baseline.memory, space))
                self.assertEqual([s.value for s in sim.control.strobes],
                                 [s.value for s in baseline.control.strobes])
                self.assertEqual(sum(r.memory_write is not None for r in trace),
                                 sum(r.memory_write is not None for r in ordinary))

    def test_busy_pulse_between_checks_is_not_queued(self):
        sim = machine(0)
        for _ in range(3): sim.step()
        sim.set_run_inputs(memr=1)
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 8)

    def test_memory_enable_and_access_age_are_retained_during_repeated_waits(self):
        sim = machine(0, memr=1, delay=20)
        for _ in range(28): sim.step()
        self.assertEqual(sim.state.registers[0], 0x20)
        self.assertTrue(all(24 in r.mops for r in sim.trace[2:]))
        self.assertEqual(sim._enabled_since, 2)
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 32)
        self.assertEqual(sim.state.registers[0], 0x21)

    def test_ready_after_t4_waits_until_next_t4(self):
        sim = machine(0, memr=1)
        for _ in range(5): sim.step()
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 16)

    def test_data_must_still_be_valid_after_external_ready_release(self):
        sim = machine(0, delay=20)
        for _ in range(5): sim.step()
        with self.assertRaises(ModelError): sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (0, 5))


class HaltStepTests(unittest.TestCase):
    def test_halt_stops_fetch_before_pc_write_then_releases_without_restarting(self):
        sim = machine(halt=0)
        for _ in range(28): sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (3, 4))
        self.assertEqual(sim.state.registers[0], 0x20)
        self.assertEqual(sim.state.br, 0x21)
        self.assertEqual(sim.state.ab, 0x20)
        self.assertEqual(sim.state.sse, 1)
        sim.set_run_inputs(halt=1)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 48)
        self.assertEqual(sim.state.registers[3], 0x69)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertEqual(sum(12 in r.mops for r in sim.trace), 2)

    def test_halt_asserted_after_t2_affects_next_instruction_not_current_execute(self):
        sim = machine()
        for _ in range(3): sim.step()
        sim.set_run_inputs(halt=0)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 24)
        with self.assertRaises(InstructionLimit): sim.run_instruction(max_slots=16)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertEqual(sim.state.phase, 3)

    def test_halt_high_after_t2_clears_latch_before_t4(self):
        sim = machine(0, halt=0)
        for _ in range(3): sim.step()
        self.assertEqual(sim.state.halt, 1)
        sim.set_run_inputs(halt=1)
        self.assertEqual(sim.state.halt, 0)
        sim.resume_instruction()
        self.assertEqual(len(sim.trace), 8)

    def test_single_step_allows_one_instruction_until_ss_is_released_and_rearmed(self):
        sim = machine(halt=0)
        for _ in range(10): sim.step()
        sim.set_run_inputs(ss=0)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[3], 0x69)
        self.assertEqual(sim.state.sse, 0)
        with self.assertRaises(InstructionLimit): sim.run_instruction(max_slots=24)
        self.assertEqual(sim.state.registers[0], 0x22)
        sim.set_run_inputs(ss=1)
        for _ in range(8): sim.step()
        self.assertEqual(sim.state.sse, 1)
        sim.set_run_inputs(ss=0)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[0], 0x23)
        self.assertEqual(sim.state.sse, 0)

    def test_step_permission_survives_memory_waits_and_memr_still_blocks(self):
        sim = machine(halt=0, ss=0, memr=1)
        for _ in range(20): sim.step()
        self.assertEqual(sim.state.phase, 3)
        self.assertEqual(sim.state.sse, 0)
        self.assertEqual(sim.state.registers[0], 0x20)
        self.assertTrue(sim._step_release)
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[3], 0x69)
        self.assertFalse(sim._step_release)
        with self.assertRaises(InstructionLimit): sim.run_instruction(max_slots=16)
        self.assertEqual(sim.state.registers[0], 0x22)

    def test_ss_is_ignored_when_halt_is_high(self):
        for level in (0, 1, None):
            sim = machine(0, ss=level, sse=None)
            sim.run_instruction()
            self.assertEqual(len(sim.trace), 8)
            self.assertIsNone(sim.state.sse)

    def test_ss_high_initializes_unknown_sse_before_first_step(self):
        sim = machine(0, halt=0, ss=1, sse=None)
        for _ in range(5): sim.step()
        self.assertEqual(sim.state.sse, 1)
        sim.set_run_inputs(ss=0)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[0], 0x21)

    def test_unknown_ss_or_sse_cannot_grant_a_step(self):
        for ss, sse in ((None, 1), (0, None)):
            sim = machine(0, halt=0, ss=ss, sse=sse)
            for _ in range(3): sim.step()
            before = deepcopy(sim.state)
            with self.assertRaises(ModelError): sim.step()
            self.assertEqual(sim.state, before)
            self.assertFalse(sim._step_release)


class ExecutionIntegrationTests(unittest.TestCase):
    def test_interrupt_request_is_retained_during_halt_and_serviced_after_completion(self):
        sim = machine(halt=0, interrupts=InterruptInput(1))
        sim.state.inte = 1
        for _ in range(16): sim.step()
        sim.set_interrupt(0)
        sim.set_interrupt(1)
        for _ in range(16): sim.step()
        self.assertEqual((sim.state.n, sim.state.intr), (0, 1))
        self.assertFalse(any(r.interrupt_accepted for r in sim.trace))
        sim.set_run_inputs(halt=1)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[3], 0x69)
        self.assertEqual(sim.run_instruction()[0].instruction, 'INTERRUPT')
        self.assertEqual((sim.state.n, sim.state.registers[0], sim.state.registers[1]), (1, 0x22, 2))

    def test_reset_escapes_memory_and_halt_waits(self):
        for pins in ({'memr': 1}, {'halt': 0}):
            sim = machine(reset=ResetInput(1), **pins)
            for _ in range(15): sim.step()
            self.assertEqual((sim.state.phase, sim.state.timing), (3, 7))
            sim.set_reset(0)
            self.assertTrue(sim.step().reset_sampled)
            sim.set_reset(1)
            self.assertIsNone(sim._pause)
            event = sim.run_instruction()
            self.assertTrue(all(r.reset_cycle for r in event))
            self.assertEqual((sim.state.n, sim.state.pg, sim.state.registers[0]), (0, 0, 0))
            sim.set_run_inputs(memr=0, halt=1)
            sim.run_instruction()
            self.assertEqual(sim.state.registers[0], 1)

    def test_reset_discards_step_permission_without_inventing_sse_rearm(self):
        sim = machine(halt=0, ss=0, memr=1, reset=ResetInput(1))
        for _ in range(15): sim.step()
        self.assertTrue(sim._step_release)
        sim.set_reset(0)
        sim.step()
        sim.set_reset(1)
        sim.set_run_inputs(memr=0)
        sim.run_instruction()
        self.assertFalse(sim._step_release)
        self.assertEqual(sim.state.sse, 0)
        with self.assertRaises(InstructionLimit): sim.run_instruction(max_slots=16)
        self.assertEqual(sim.state.registers[0], 0)

    def test_scwr_wait_and_halt_have_separate_resume_points(self):
        sim = machine(8, control=ControlPort(scwr=1))
        for _ in range(24): sim.step()
        self.assertEqual(sim._pause.phase, 2)
        self.assertEqual(sim._pause.kind, 'scwr')
        sim.set_run_inputs(halt=0)
        sim.control.scwr = 0
        sim.resume_instruction()
        self.assertEqual(len(sim.control.strobes), 1)
        with self.assertRaises(InstructionLimit): sim.run_instruction(max_slots=16)
        self.assertEqual(sim._pause.phase, 0)
        self.assertEqual(sim.state.registers[0], 0x22)

    def test_control_byte_waits_for_memory_then_scwr_without_restrobing(self):
        sim = machine(8, delay=8, control=ControlPort(ack_after=20))
        trace = run_with_one_wait_per_read(sim)
        self.assertEqual(len(trace), 56)
        self.assertEqual(len(sim.control.strobes), 1)
        self.assertEqual(sim.control.value, 0x80)
        self.assertEqual(sim.control.strobes[0].slot, 30)
        self.assertEqual(sim.state.registers[0], 0x22)
        self.assertEqual(sum(50 in r.mops for r in trace), 3)
        self.assertIsNone(sim._pause)

    def test_all_encodings_run_once_per_single_step(self):
        catalogue, _ = load_data()
        for opcode in validate(catalogue):
            with self.subTest(opcode=opcode):
                ordinary = machine(opcode, control=ControlPort(scwr=0))
                expected = ordinary.run_instruction()
                stepped = machine(opcode, halt=0, ss=0, control=ControlPort(scwr=0))
                actual = stepped.run_instruction()
                self.assertEqual(len(actual), len(expected))
                expected_state = architecture(ordinary.state)
                expected_state['sse'] = 0
                self.assertEqual(architecture(stepped.state), expected_state)
                self.assertEqual(stepped.memory, ordinary.memory)
                self.assertEqual([s.value for s in stepped.control.strobes],
                                 [s.value for s in ordinary.control.strobes])

    def test_all_encodings_match_v017_with_integration_off_or_quiet(self):
        catalogue, _ = load_data()
        for opcode in validate(catalogue):
            for enabled in (False, True):
                with self.subTest(opcode=opcode, enabled=enabled):
                    current = machine(opcode, control=ControlPort(scwr=0))
                    if not enabled: current.run_inputs = None
                    old = OldSimulator(OldState(**architecture(current.state)),
                                       OldMemory(**asdict(current.memory)),
                                       control=OldControl(scwr=0), test_inputs=(0, 1, 0, 1))
                    actual, expected = current.run_instruction(), old.run_instruction()
                    self.assertEqual(len(actual), len(expected))
                    self.assertEqual(architecture(current.state), asdict(old.state))
                    self.assertEqual(asdict(current.memory), asdict(old.memory))
                    self.assertEqual(asdict(current.control), asdict(old.control))

    def test_delayed_ein_effect_occurs_once_across_wait_loops(self):
        sim = machine(3)
        sim.memory.program[0x121] = 0
        sim.run_instruction()
        sim.set_run_inputs(memr=1)
        with self.assertRaises(InstructionLimit): sim.run_instruction(max_slots=24)
        self.assertEqual(sim.state.inte, 1)
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        effects = [r.flag_effect for r in sim.trace if r.flag_effect is not None]
        self.assertEqual([e.name for e in effects], ['EIN'])

    def test_unknown_memr_preserves_granted_step_and_retry_continuation(self):
        sim = machine(0, halt=0, ss=0, memr=None)
        for _ in range(4): sim.step()
        self.assertTrue(sim._step_release)
        before = deepcopy(sim.state)
        with self.assertRaises(ModelError): sim.step()
        self.assertEqual(sim.state, before)
        self.assertTrue(sim._step_release)
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[0], 0x21)
        self.assertEqual(sim.state.sse, 0)

    def test_unknown_memr_is_dominated_by_halt_until_step_or_release(self):
        sim = machine(0, halt=0, memr=None)
        for _ in range(8): sim.step()
        self.assertEqual(sim.state.phase, 3)
        sim.set_run_inputs(ss=0)
        for _ in range(4): sim.step()
        self.assertEqual(sim.state.timing, 4)
        with self.assertRaises(ModelError): sim.step()
        sim.set_run_inputs(memr=0)
        sim.resume_instruction()
        self.assertEqual(sim.state.registers[0], 0x21)

    def test_input_validation_is_atomic_and_integration_explicit(self):
        for name in ('memr', 'halt', 'ss'):
            with self.assertRaises(ModelError): RunInputs(**{name: False})
        sim = machine(0)
        before = deepcopy(sim.state)
        pins = deepcopy(sim.run_inputs)
        for changes in ({'ss': 2}, {'memr': False}, {'unknown': 0}):
            with self.assertRaises(ModelError): sim.set_run_inputs(**changes)
            self.assertEqual(sim.state, before)
            self.assertEqual(sim.run_inputs, pins)
        sim.run_inputs = None
        with self.assertRaises(ModelError): sim.set_run_inputs(halt=1)

    def test_waits_preserve_pc_x_aliases_and_operand_wrap_on_every_page(self):
        for n in range(8):
            for pg in range(4):
                for base in (0x48, 0x68, 0x58, 0x70, 0x50, 0xF8, 0xB8, 0xB0):
                    with self.subTest(n=n, pg=pg, opcode=base|n):
                        baseline = machine(base|n)
                        baseline.state.n, baseline.state.pg = n, pg
                        baseline.state.registers[n] = 0xFF
                        baseline.memory.program = {(pg<<8)|0xFF: base|n,
                                                   pg<<8: 0x80, (pg<<8)|0x80: 0xA6}
                        baseline.memory.storage = {pg<<8: 0x69, (pg<<8)|0x80: 0x5A}
                        delayed = InstructionSimulator(
                            deepcopy(baseline.state), deepcopy(baseline.memory),
                            run_inputs=RunInputs(memr=0, halt=1, ss=1), test_inputs=(0, 1, 0, 1))
                        delayed.memory.program_delay = delayed.memory.storage_delay = 8
                        baseline.run_instruction()
                        run_with_one_wait_per_read(delayed)
                        self.assertEqual(architecture(delayed.state), architecture(baseline.state))
                        self.assertEqual(delayed.memory.program, baseline.memory.program)
                        self.assertEqual(delayed.memory.storage, baseline.memory.storage)

    def test_demo_combines_memory_halt_and_step_without_repeating_fetch(self):
        from cmc8.__main__ import execution_demo
        sim = execution_demo()
        self.assertEqual(len(sim.trace), 40)
        self.assertEqual((sim.state.registers[0], sim.state.registers[3], sim.state.sse),
                         (0x22, 0x69, 0))
        self.assertEqual(sum(48 in row.mops for row in sim.trace), 1)
        self.assertEqual(sum(12 in row.mops for row in sim.trace), 2)


if __name__ == '__main__':
    unittest.main()
