"""Datapath invariants; these are not yet book timing conformance tests."""
import itertools
import json
import unittest

from cmc8.versions.v001 import MOPS, UNRESOLVED, ModelError, Simulator, State, evaluate


class DatapathTests(unittest.TestCase):
    def test_catalogue_is_complete(self):
        self.assertEqual(set(MOPS), set(range(1, 51)))

    def test_increment_and_writeback_for_all_bytes(self):
        for value in range(256):
            state = State(n=3)
            state.registers[3] = value
            sim = Simulator(state)
            first = sim.capture([18, 21, 7, 10, 12])
            self.assertEqual(first.signals.di, value)
            self.assertEqual(sim.state.br, (value + 1) & 255)
            self.assertEqual(sim.state.registers[3], value)
            sim.capture([4, 18, 22])
            self.assertEqual(sim.state.registers[3], (value + 1) & 255)

    def test_mop_order_does_not_change_circuit(self):
        state = State(n=0)
        state.registers[0] = 19
        expected = evaluate(state, [18, 21, 7, 10, 12])
        for order in itertools.permutations([18, 21, 7, 10, 12]):
            self.assertEqual(evaluate(state, order), expected)

    def test_selectors_alias_and_x_is_register_seven(self):
        state = State(n=3, ir=0x53)
        state.registers[3] = 99
        state.registers[7] = 23
        self.assertEqual(evaluate(state, [18, 21]).di, 99)
        self.assertEqual(evaluate(state, [19, 21]).di, 99)
        self.assertEqual(evaluate(state, [20, 21]).di, 23)

    def test_complement_is_eight_bits(self):
        self.assertEqual(evaluate(State(br=0xA5), [5]).di, 0x5A)

    def test_simultaneous_capture_reads_old_storage(self):
        sim = Simulator(State(br=17))
        sim.capture([2, 6], external_db=99)
        self.assertEqual((sim.state.br, sim.state.ab), (99, 17))

    def test_unknown_propagates_without_initializing_to_zero(self):
        sim = Simulator()
        sim.capture([4, 14])
        self.assertIsNone(sim.state.ab)
        self.assertIsNone(sim.state.n)

    def test_di_is_not_retained_between_evaluations(self):
        self.assertEqual(evaluate(State(br=17), [4]).di, 17)
        self.assertIsNone(evaluate(State(br=17), []).di)

    def test_conflicts_are_atomic(self):
        for mops, db in [([4, 5], None), ([23], 0), ([18, 19], None),
                         ([2, 12], None), ([34, 35], None), ([44, 18, 22, 40], None)]:
            sim = Simulator(State(n=0, br=1))
            before = State(n=0, br=1)
            with self.assertRaises(ModelError):
                sim.capture(mops, external_db=db)
            self.assertEqual(sim.state, before)
            self.assertEqual(sim.trace, [])

    def test_every_unresolved_mop_is_explicit(self):
        for number in UNRESOLVED:
            with self.assertRaisesRegex(ModelError, f"MOP{number}"):
                Simulator().capture([number])

    def test_alu_logical_paths_and_provisional_addition(self):
        state = State(br=0x96, n=0)
        state.registers[0] = 0x35
        controls = [18, 21, 7, 3, 12]
        self.assertEqual(evaluate(state, controls + [8]).mux, 0xA3)
        self.assertEqual(evaluate(state, controls + [9]).mux, 0x14)
        self.assertEqual(evaluate(state, controls).mux, 0xCB)

    def test_shift_modes(self):
        state = State(br=0x81, link=1)
        controls = [4, 7, 10, 11, 12]  # ALU = 0x82
        self.assertEqual(evaluate(state, controls).mux, 0xC1)
        self.assertEqual(evaluate(state, controls + [43]).mux, 0x41)
        self.assertEqual(evaluate(state, controls + [13]).mux, 0x41)

    def test_control_writes_and_wraparound(self):
        sim = Simulator(State(n=7, ir=3))
        sim.capture([16, 15, 34, 36, 38, 49, 31])
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.link, sim.state.z,
                          sim.state.inte, sim.state.sse, sim.state.phase),
                         (0, 3, 1, 1, 1, 1, 2))
        sim.capture([17, 42, 35, 37, 39, 48, 30, 46])
        self.assertEqual((sim.state.n, sim.state.pg, sim.state.link, sim.state.z,
                          sim.state.inte, sim.state.sse, sim.state.phase, sim.state.intr),
                         (7, 0, 0, 0, 0, 0, 0, 0))

    def test_bus_capture_outputs_and_trace(self):
        sim = Simulator()
        record = sim.capture([1, 24, 25, 26, 27], external_db=0x53)
        self.assertEqual(sim.state.ir, 0x53)
        self.assertEqual(record.signals.outputs, ("PME", "SME", "EDE", "WRITE"))
        self.assertEqual(json.loads(json.dumps(record.to_dict()))["version"], "v001")
        sim.state.ir = 0
        self.assertEqual(record.after.ir, 0x53)

    def test_invalid_values_rejected(self):
        for state in [State(n=8), State(registers=[0]), State(br=256)]:
            with self.assertRaises(ModelError):
                Simulator(state)


if __name__ == "__main__":
    unittest.main()
