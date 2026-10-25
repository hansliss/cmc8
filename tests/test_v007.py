"""Integrated indexed instruction tests for the selected buffer-route model."""
from dataclasses import asdict
import json
import unittest

from cmc8.versions.v006 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v006 import Memory as PreviousMemory
from cmc8.versions.v006 import State as PreviousState
from cmc8.versions.v007 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v007.sequences import decode


INDEXED = {"LRX": (0x48, "program", False), "LSX": (0x58, "storage", False),
           "SRX": (0x68, "program", True), "SSX": (0x78, "storage", True)}


def experiment(name, *, page=2, n=0, a=3, value=0xA6, pc=0x20):
    opcode, space, store = INDEXED[name]
    state = State(n=n, pg=page, link=1, z=0, inte=1)
    state.registers = [value] * 8
    state.registers[7] = 0x80
    state.registers[n] = pc
    address = ((pc + 1) & 255) if n == 7 else 0x80
    target = (page << 8) | address
    memory = Memory(program={(page << 8) | pc: opcode | a}, storage={}, devices={0: 0x69})
    getattr(memory, space)[target] = 0x11 if store else value
    return InstructionSimulator(state, memory), target


class IndexedInstructionTests(unittest.TestCase):
    def test_documented_encodings(self):
        for name, (opcode, _, _) in INDEXED.items():
            for a in range(8):
                self.assertEqual(decode(opcode | a), name)

    def test_all_pages_selectors_aliases_and_boundary_values(self):
        for name, (_, space, store) in INDEXED.items():
            for page in range(4):
                for n in range(8):
                    for a in range(8):
                        for value in (0, 0xA6, 0xFF):
                            with self.subTest(name=name, page=page, n=n, a=a, value=value):
                                sim, target = experiment(name, page=page, n=n, a=a, value=value)
                                registers = list(sim.state.registers)
                                registers[n] = 0x21
                                source = registers[a]
                                expected_memory = asdict(sim.memory)
                                if store:
                                    expected_memory[space][target] = source
                                else:
                                    registers[a] = value
                                trace = sim.run_instruction()
                                self.assertEqual(len(trace), 24)
                                self.assertEqual(sim.state.registers, registers)
                                self.assertEqual(asdict(sim.memory), expected_memory)
                                self.assertEqual(sim.state.ab, target & 255)
                                self.assertEqual((sim.state.pg, sim.state.link, sim.state.z, sim.state.inte),
                                                 (page, 1, 0, 1))
                                self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))

    def test_f1_loopback_landmarks_and_no_external_enable(self):
        for name in INDEXED:
            sim, _ = experiment(name)
            trace = sim.run_instruction()
            f1 = trace[8:16]
            self.assertEqual(f1[0].start.signals.di, 0x80)
            self.assertTrue(all(r.start.signals.db == 0x80 for r in f1[1:6]))
            self.assertEqual(f1[5].start.before.br, 0x21)
            self.assertEqual(f1[5].start.after.br, 0x80)
            self.assertEqual(f1[5].start.after.ab, 0x21)
            self.assertEqual(f1[6].start.after.ab, 0x80)
            self.assertTrue(all(not ({24, 25, 26, 29} & set(r.mops)) for r in f1))
            self.assertEqual([r.start.after.registers[0] for r in f1], [0x21] * 8)

    def test_external_adapter_reads_only_fetch_and_final_memory(self):
        class RecordingMemory(Memory):
            def read(self, space, address, elapsed):
                self.reads.append((space, address))
                return super().read(space, address, elapsed)

        for name, (_, space, store) in INDEXED.items():
            sim, target = experiment(name)
            recording = RecordingMemory(**asdict(sim.memory))
            recording.reads = []
            sim.memory = recording
            sim.run_instruction()
            expected = {("program", 0x220)}
            if not store:
                expected.add((space, target))
            self.assertEqual(set(recording.reads), expected)

    def test_final_memory_control_windows_are_preserved(self):
        for name, (_, space, store) in INDEXED.items():
            sim, target = experiment(name)
            trace = sim.run_instruction()
            enable = "PME" if space == "program" else "SME"
            self.assertEqual([r.timing for r in trace[16:] if enable in r.start.signals.outputs],
                             list(range(6)) if store else [2, 3, 4, 5])
            writes = [r for r in trace if r.memory_write]
            if store:
                self.assertEqual(len(writes), 1)
                self.assertEqual((writes[0].phase, writes[0].timing), (2, 5))
                self.assertEqual((writes[0].memory_write.space, writes[0].memory_write.address),
                                 (space, target))
            else:
                self.assertEqual(writes, [])

    def test_single_byte_instructions_can_be_run_consecutively(self):
        state = State(n=0, pg=2)
        state.registers[0], state.registers[7] = 0x20, 0x80
        memory = Memory(program={0x220: 0x4B, 0x221: 0x6B, 0x222: 0x7B,
                                 0x223: 0x5C, 0x280: 0xA6})
        sim = InstructionSimulator(state, memory)
        for name in ("LRX", "SRX", "SSX", "LSX"):
            trace = sim.run_instruction()
            self.assertEqual(trace[6].instruction, name)
            self.assertEqual(len(trace), 24)
        self.assertEqual(sim.state.registers[0], 0x24)
        self.assertEqual(sim.state.registers[4], 0xA6)
        self.assertEqual(memory.storage[0x280], 0xA6)
        self.assertEqual(len(sim.trace), 96)
        self.assertEqual(json.loads(json.dumps(sim.trace[-1].to_dict()))["version"], "v007")

    def test_pc_wrap_preserves_page_and_reads_updated_x_when_it_is_pc(self):
        for name, (_, space, store) in INDEXED.items():
            sim, target = experiment(name, page=3, n=7, a=3, pc=0xFF)
            self.assertEqual(target, 0x300)
            sim.run_instruction()
            self.assertEqual(sim.state.registers[7], 0)
            self.assertEqual(sim.state.ab, 0)
            self.assertEqual(sim.state.pg, 3)

    def test_unknown_x_rejects_undriven_loopback_and_can_be_retried(self):
        sim, _ = experiment("LSX")
        sim.state.registers[7] = None
        for _ in range(13):
            sim.step()
        with self.assertRaisesRegex(ModelError, "DB is not valid"):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (1, 5))
        self.assertEqual(len(sim.trace), 13)
        self.assertEqual(len(sim.cpu.trace), 26)
        sim.state.registers[7] = 0x80
        sim.step()
        self.assertEqual(sim.state.br, 0x80)

    def test_internal_loopback_ignores_external_memory_delay(self):
        sim, _ = experiment("LSX")
        sim.memory.storage_delay = 4
        for _ in range(14):
            sim.step()
        self.assertEqual(sim.state.br, 0x80)  # F1 capture succeeded without external data.
        for _ in range(7):
            sim.step()
        with self.assertRaisesRegex(ModelError, "DB is not valid"):
            sim.step()  # Actual F2 read still requires timely storage data.

    def test_ein_effect_occurs_once_before_indexed_execution(self):
        sim, _ = experiment("LSX")
        sim.state.ir, sim.state.inte = 3, 0
        trace = sim.run_instruction()
        self.assertEqual([r.flag_effect.name for r in trace if r.flag_effect], ["EIN"])
        self.assertEqual(trace[2].start.after.inte, 1)
        self.assertEqual(sim.state.registers[3], 0xA6)

    def test_prior_instructions_match_preserved_v006(self):
        for opcode in (0, 2, 3, 4, 5, 6, 7, 0x43, 0x53, 0x63, 0x73, 0x13, 0x1B):
            sim, _ = experiment("LSX")
            sim.memory.program[0x220] = opcode
            sim.memory.program[0x221] = 0x80
            sim.memory.program[0x280] = 0x69
            sim.memory.devices[0x80] = 0x45
            old = PreviousSimulator(PreviousState(**asdict(sim.state)), PreviousMemory(**asdict(sim.memory)))
            trace = sim.run_instruction()
            old_trace = old.run_instruction()
            self.assertEqual(asdict(sim.state), asdict(old.state))
            self.assertEqual(asdict(sim.memory), asdict(old.memory))
            for actual, previous in zip(trace, old_trace):
                actual_record, previous_record = actual.to_dict(), previous.to_dict()
                # Versions intentionally differ; all other trace content should agree.
                for record in (actual_record, previous_record):
                    record['version'] = ''
                    for point in ('start', 'end'):
                        record[point]['version'] = ''
                        record[point]['signals']['version'] = ''
                self.assertEqual(actual_record, previous_record)


if __name__ == "__main__":
    unittest.main()
