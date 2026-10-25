"""Paged load/store tests, including cross-family timing and code writes."""
import json
import unittest

from cmc8.versions.v002 import Memory as PreviousMemory
from cmc8.versions.v003 import InstructionSimulator, Memory, ModelError, State
from cmc8.versions.v003.sequences import decode


FAMILIES = {"LRM": 0x40, "LRS": 0x50, "SRM": 0x60, "SRS": 0x70}


def experiment(name, *, page=2, n=0, target=3, pc=0x20, value=0xA6):
    state = State(n=n, pg=page, link=1, z=0)
    state.registers = [value] * 8
    state.registers[n] = pc
    base = page << 8
    memory = Memory(
        program={base | pc: FAMILIES[name] | target,
                 base | ((pc + 1) & 255): 0x80,
                 base | 0x80: value if name == "LRM" else 0x11},
        storage={base | 0x80: value if name == "LRS" else 0x22},
    )
    return InstructionSimulator(state, memory)


class PagedMemoryTests(unittest.TestCase):
    def test_book_program_memory_opcodes(self):
        # p.126 gives octal 103 and 143 for LRM R3 and SRM R3.
        self.assertEqual(decode(0o103), "LRM")
        self.assertEqual(decode(0o143), "SRM")
        for name, base in FAMILIES.items():
            for register in range(8):
                self.assertEqual(decode(base | register), name)

    def test_all_four_families_on_every_page_and_register_pair(self):
        for page in range(4):
            for n in range(8):
                for target in range(8):
                    for name in FAMILIES:
                        with self.subTest(page=page, n=n, target=target, name=name):
                            sim = experiment(name, page=page, n=n, target=target)
                            before = list(sim.state.registers)
                            address = (page << 8) | 0x80
                            program_before = dict(sim.memory.program)
                            storage_before = dict(sim.memory.storage)
                            trace = sim.run_instruction()
                            expected_registers = list(before)
                            expected_registers[n] = 0x22
                            if name.startswith("L"):
                                expected_registers[target] = 0xA6
                                self.assertEqual(sim.memory.program, program_before)
                                self.assertEqual(sim.memory.storage, storage_before)
                            else:
                                expected = 0x22 if target == n else 0xA6
                                if name == "SRM":
                                    program_before[address] = expected
                                else:
                                    storage_before[address] = expected
                                self.assertEqual(sim.memory.program, program_before)
                                self.assertEqual(sim.memory.storage, storage_before)
                            self.assertEqual(sim.state.registers, expected_registers)
                            self.assertEqual((sim.state.pg, sim.state.link, sim.state.z), (page, 1, 0))
                            self.assertEqual((sim.state.phase, sim.state.timing), (0, 0))
                            self.assertEqual(len(trace), 24)

    def test_only_current_storage_page_is_read(self):
        for page in range(4):
            sim = experiment("LRS", page=page)
            sim.memory.storage = {(p << 8) | 0x80: 0x30 + p for p in range(4)}
            sim.run_instruction()
            self.assertEqual(sim.state.registers[3], 0x30 + page)

    def test_only_current_storage_page_is_written(self):
        for page in range(4):
            sim = experiment("SRS", page=page)
            sim.memory.storage = {(p << 8) | 0x80: 0x30 + p for p in range(4)}
            sim.run_instruction()
            for other in range(4):
                self.assertEqual(sim.memory.storage[(other << 8) | 0x80],
                                 0xA6 if other == page else 0x30 + other)

    def test_program_variants_preserve_datapath_and_substitute_enable(self):
        for load, store in [("LRS", "LRM"), ("SRS", "SRM")]:
            storage_sim = experiment(load)
            program_sim = experiment(store)
            storage_trace = storage_sim.run_instruction()
            program_trace = program_sim.run_instruction()
            for old, new in zip(storage_trace, program_trace):
                with self.subTest(pair=(load, store), phase=old.phase, timing=old.timing):
                    self.assertEqual(new.mops, tuple(24 if n == 25 else n for n in old.mops))
                    for field in ("registers", "br", "ab", "pg", "n", "link", "z"):
                        self.assertEqual(getattr(old.end.after, field), getattr(new.end.after, field))
                    if old.phase > 0:
                        self.assertEqual(old.start.signals.db, new.start.signals.db)

    def test_lrm_matches_documented_data_window_and_transfer_points(self):
        sim = experiment("LRM")
        trace = sim.run_instruction()
        self.assertEqual([row.timing for row in trace[16:]
                          if row.start.signals.db is not None], [2, 3, 4, 5])
        self.assertEqual(trace[13].start.after.br, 0x80)
        self.assertEqual(trace[14].start.after.ab, 0x80)
        self.assertEqual(trace[21].start.after.br, 0xA6)
        self.assertEqual(trace[22].start.after.registers[3], 0xA6)
        self.assertTrue(all("SME" not in row.start.signals.outputs for row in trace))

    def test_srm_write_window_commit_and_trace_identity(self):
        sim = experiment("SRM")
        before = dict(sim.memory.program)
        for _ in range(21):
            sim.step()
        self.assertEqual(sim.memory.program, before)
        row = sim.step()
        self.assertEqual((row.phase, row.timing), (2, 5))
        self.assertEqual((row.memory_write.space, row.memory_write.address, row.memory_write.value),
                         ("program", 0x280, 0xA6))
        self.assertEqual(sim.memory.program[0x280], 0xA6)
        encoded = json.loads(json.dumps(row.to_dict()))
        self.assertEqual(encoded["version"], "v003")
        self.assertEqual(encoded["start"]["version"], "v003")
        self.assertEqual(encoded["memory_write"],
                         {"space": "program", "address": 0x280, "value": 0xA6})
        self.assertEqual([r.timing for r in sim.trace if r.phase == 2
                          and "WRITE" in r.start.signals.outputs], [1, 2, 3, 4])

    def test_program_store_changes_a_subsequently_fetched_opcode(self):
        sim = experiment("SRM", value=0x44)  # LRM R4 opcode
        sim.memory.program.update({0x221: 0x22, 0x222: 0, 0x223: 0x80, 0x280: 0x69})
        sim.run_instruction()
        self.assertEqual(sim.memory.program[0x222], 0x44)
        trace = sim.run_instruction()
        self.assertEqual(trace[6].instruction, "LRM")
        self.assertEqual(sim.state.registers[4], 0x69)
        self.assertEqual(sim.state.registers[0], 0x24)

    def test_same_space_round_trip(self):
        for load, store in [(0x43, 0x63), (0x53, 0x73)]:
            sim = experiment("SRM" if store == 0x63 else "SRS")
            sim.memory.program.update({0x220: store, 0x222: load, 0x223: 0x80})
            sim.run_instruction()
            sim.state.registers[3] = 0
            sim.run_instruction()
            self.assertEqual(sim.state.registers[3], 0xA6)

    def test_pc_wrap_does_not_change_page(self):
        for name in FAMILIES:
            sim = experiment(name, page=3, pc=0xFF)
            sim.run_instruction()
            self.assertEqual(sim.state.registers[0], 1)
            self.assertEqual(sim.state.pg, 3)

    def test_late_program_data_misses_br_but_can_reach_ir(self):
        sim = experiment("LRM")
        sim.memory.program_delay = 4
        for _ in range(6):
            row = sim.step()
        self.assertIsNone(row.start.after.ir)
        self.assertEqual(row.end.after.ir, 0x43)
        # Reach F2 with fast operand memory, then delay the LRM data access.
        sim.memory.program_delay = 0
        for _ in range(10):
            sim.step()
        sim.memory.program_delay = 4
        for _ in range(5):
            sim.step()
        with self.assertRaisesRegex(ModelError, "start of T5"):
            sim.step()
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 5))
        sim.memory.program_delay = 3
        sim.step()
        self.assertEqual(sim.state.br, 0xA6)

    def test_read_only_program_page_rejects_write_and_preserves_slot(self):
        sim = experiment("SRM", page=3)
        sim.memory.program_readonly_pages = frozenset({3})
        before = dict(sim.memory.program)
        for _ in range(21):
            sim.step()
        with self.assertRaisesRegex(ModelError, "read-only"):
            sim.step()
        self.assertEqual(sim.memory.program, before)
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 5))
        self.assertEqual(len(sim.trace), 21)
        self.assertEqual(len(sim.cpu.trace), 42)
        sim.memory.program_readonly_pages = frozenset()
        sim.step()
        self.assertEqual(sim.memory.program[0x380], 0xA6)

    def test_read_only_program_page_can_still_be_read(self):
        sim = experiment("LRM", page=3)
        sim.memory.program_readonly_pages = frozenset({3})
        sim.run_instruction()
        self.assertEqual(sim.state.registers[3], 0xA6)

    def test_write_stability_includes_page_and_memory_selection(self):
        sim = experiment("SRM")
        for _ in range(18):
            sim.step()
        before = dict(sim.memory.program)
        sim.state.pg = 1
        with self.assertRaisesRegex(ModelError, "changed during WRITE"):
            sim.step()
        self.assertEqual(sim.memory.program, before)
        self.assertEqual((sim.state.phase, sim.state.timing), (2, 2))

    def test_address_space_sizes_and_predecessor_are_explicit(self):
        memory = Memory(program={1023: 1}, storage={1023: 2})
        self.assertEqual(memory.storage[1023], 2)
        with self.assertRaises(Exception):
            PreviousMemory(storage={1023: 2})
        for space in ("program", "storage"):
            for address in (-1, 1024):
                with self.assertRaises(ModelError):
                    Memory(**{space: {address: 0}})
        with self.assertRaises(ModelError):
            Memory(program_readonly_pages=frozenset({4}))


if __name__ == "__main__":
    unittest.main()
