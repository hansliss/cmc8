"""EDE substitution, unpaged I/O and isolation from both memory spaces."""
from dataclasses import asdict
import json
import unittest

from cmc8.versions.v003 import InstructionSimulator as PreviousSimulator
from cmc8.versions.v003 import Memory as PreviousMemory
from cmc8.versions.v003 import State as PreviousState
from cmc8.versions.v004 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v004.sequences import decode


FAMILIES = {"LRM": 0x40, "LRS": 0x50, "SRM": 0x60, "SRS": 0x70,
            "LRD": 0x10, "SRD": 0x18}


def experiment(name, page=2, n=0, target=3, value=0xA6):
    state = State(n=n, pg=page, link=1, z=0)
    state.registers = [value] * 8
    state.registers[n] = 0x20
    base = page << 8
    memory = Memory(
        program={base | 0x20: FAMILIES[name] | target, base | 0x21: 0x80,
                 base | 0x80: value if name == "LRM" else 0x11},
        storage={base | 0x80: value if name == "LRS" else 0x22},
        devices={0x80: value if name == "LRD" else 0x33},
    )
    return InstructionSimulator(state, memory)


class DeviceInstructionTests(unittest.TestCase):
    def test_book_opcodes(self):
        # Printed p.126, lower table: octal 023/033 for LRD/SRD R3.
        self.assertEqual(decode(0o023), "LRD")
        self.assertEqual(decode(0o033), "SRD")
        for name, base in FAMILIES.items():
            for register in range(8):
                self.assertEqual(decode(base | register), name)

    def test_all_six_families_pages_and_register_pairs(self):
        for page in range(4):
            for n in range(8):
                for target in range(8):
                    for name in FAMILIES:
                        with self.subTest(page=page, n=n, target=target, name=name):
                            sim = experiment(name, page, n, target)
                            registers = list(sim.state.registers)
                            registers[n] = 0x22
                            snapshots = {space: dict(getattr(sim.memory, space))
                                         for space in ("program", "storage", "devices")}
                            sim.run_instruction()
                            if name.startswith("L"):
                                registers[target] = 0xA6
                            else:
                                space = {"SRM": "program", "SRS": "storage", "SRD": "devices"}[name]
                                address = 0x80 if space == "devices" else (page << 8) | 0x80
                                snapshots[space][address] = 0x22 if target == n else 0xA6
                            self.assertEqual(sim.state.registers, registers)
                            for space, cells in snapshots.items():
                                self.assertEqual(getattr(sim.memory, space), cells)
                            self.assertEqual((sim.state.pg, sim.state.link, sim.state.z), (page, 1, 0))
                            self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))

    def test_ede_substitution_preserves_every_other_control_and_transfer(self):
        for source, variant in [("LRS", "LRD"), ("SRS", "SRD")]:
            old = experiment(source).run_instruction()
            new = experiment(variant).run_instruction()
            for old_slot, new_slot in zip(old, new):
                self.assertEqual(new_slot.mops, tuple(26 if n == 25 else n for n in old_slot.mops))
                for field in ("registers", "br", "ab", "pg", "n", "link", "z"):
                    self.assertEqual(getattr(old_slot.end.after, field), getattr(new_slot.end.after, field))

    def test_lrd_enable_and_capture_windows(self):
        sim = experiment("LRD")
        trace = sim.run_instruction()
        self.assertEqual([(r.phase, r.timing) for r in trace if "EDE" in r.start.signals.outputs],
                         [(2, t) for t in (2, 3, 4, 5)])
        self.assertTrue(all("DBDIR" not in r.start.signals.outputs for r in trace))
        self.assertEqual(trace[21].start.after.br, 0xA6)
        self.assertEqual(trace[22].start.after.registers[3], 0xA6)
        self.assertEqual(trace[21].end.after.ir, 0x13)

    def test_srd_enable_direction_and_completion(self):
        sim = experiment("SRD")
        before = dict(sim.memory.devices)
        for _ in range(21):
            sim.step()
        self.assertEqual(sim.memory.devices, before)
        row = sim.step()
        self.assertEqual(sim.memory.devices[0x80], 0xA6)
        self.assertEqual((row.memory_write.space, row.memory_write.address, row.memory_write.value),
                         ("devices", 0x80, 0xA6))
        encoded = json.loads(json.dumps(row.to_dict()))
        self.assertEqual(encoded["version"], "v004")
        self.assertEqual(encoded["memory_write"]["space"], "devices")
        self.assertEqual([r.timing for r in sim.trace if r.phase == 2
                          and "EDE" in r.start.signals.outputs], list(range(6)))
        self.assertEqual([r.timing for r in sim.trace if r.phase == 2
                          and "WRITE" in r.start.signals.outputs], [1, 2, 3, 4])
        self.assertTrue(all(r.start.signals.db == 0xA6 for r in sim.trace[15:22]))

    def test_lrd_does_not_need_pg_during_device_access(self):
        sim = experiment("LRD", page=3)
        for _ in range(16):
            sim.step()
        sim.state.pg = None  # Fetch needed PG; the external port does not.
        for _ in range(8):
            sim.step()
        self.assertEqual(sim.state.registers[3], 0xA6)

    def test_page_changes_do_not_change_selected_output_port(self):
        sim = experiment("SRD")
        for _ in range(18):
            sim.step()
        sim.state.pg = 1
        for _ in range(6):
            sim.step()
        self.assertEqual(sim.memory.devices[0x80], 0xA6)

    def test_static_bidirectional_port_round_trip(self):
        sim = experiment("SRD")
        sim.memory.program.update({0x222: 0x14, 0x223: 0x80})  # LRD R4
        sim.run_instruction()
        sim.state.registers[4] = 0
        sim.run_instruction()
        self.assertEqual(sim.state.registers[4], 0xA6)
        self.assertEqual(len(sim.trace), 48)

    def test_late_device_data_is_rejected_at_br_capture(self):
        sim = experiment("LRD")
        sim.memory.device_delay = 4
        for _ in range(21):
            sim.step()
        with self.assertRaisesRegex(ModelError, "start of T5"):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 5))
        self.assertEqual(len(sim.cpu.trace), 42)
        sim.memory.device_delay = 3
        sim.step()
        self.assertEqual(sim.state.br, 0xA6)

    def test_missing_input_is_unknown_and_failed_slot_is_rolled_back(self):
        sim = experiment("LRD")
        sim.memory.devices.clear()
        for _ in range(21):
            sim.step()
        with self.assertRaisesRegex(ModelError, "DB is not valid"):
            sim.step()
        self.assertEqual(sim.memory.devices, {})
        self.assertEqual(len(sim.trace), 21)
        self.assertEqual(sim.state.br, 0x80)

    def test_invalid_ports_and_multiple_enables_rejected(self):
        for address in (-1, 256):
            with self.assertRaises(ModelError):
                Memory(devices={address: 0})
        with self.assertRaises(ModelError):
            Memory(device_delay=-1)
        sim = experiment("LRD")
        for enables in ((24, 26), (25, 26), (24, 25, 26)):
            with self.assertRaisesRegex(ModelError, "Multiple external"):
                sim._memory_space(enables)

    def test_memory_instruction_state_matches_preserved_v003(self):
        for name in ("LRM", "LRS", "SRM", "SRS"):
            sim = experiment(name)
            state = PreviousState(**asdict(sim.state))
            memory = PreviousMemory(program=dict(sim.memory.program), storage=dict(sim.memory.storage))
            previous = PreviousSimulator(state, memory)
            sim.run_instruction()
            previous.run_instruction()
            self.assertEqual(asdict(sim.state), asdict(previous.state))
            self.assertEqual(sim.memory.program, previous.memory.program)
            self.assertEqual(sim.memory.storage, previous.memory.storage)
            for actual, expected in zip(sim.trace, previous.trace):
                self.assertEqual(actual.mops, expected.mops)


if __name__ == "__main__":
    unittest.main()
