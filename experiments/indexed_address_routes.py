"""Compare two indexed-address hypotheses using the preserved v006 datapath.

Run from the repository root: python3 -m experiments.indexed_address_routes
These are manual captures with ideal memory, not implemented CPU opcodes or
book timing conformance tests. See docs/indexed-addressing.md for evidence.
"""
from itertools import product

from cmc8.versions.v006 import Simulator, State, evaluate
from cmc8.versions.v006.sequences import LRM, LRS, SRM, SRS


INSTRUCTIONS = {
    "LRX": (0x48, LRM, False, "program"),
    "LSX": (0x58, LRS, False, "storage"),
    "SRX": (0x68, SRM, True, "program"),
    "SSX": (0x78, SRS, True, "storage"),
}


def address_phase(route, store):
    if route == "loopback":
        slots = (
            (20, 21),              # T0: X -> DI
            (20, 21, 23),          # T1: DI -> DB; keep X driving
            (20, 21, 23),          # T2
            (20, 21, 23),          # T3
            (20, 21, 23),          # T4
            (20, 21, 23, 2),       # T5: capture CPU-driven DB into BR
        )
        return slots + (((6, 19, 21), (19, 21, 23)) if store else ((6,), ()))
    if route == "direct":
        slots = ((20, 21), (20, 21, 14), (), (), (), ())
        return slots + (((19, 21), (19, 21, 23)) if store else ((), ()))
    raise ValueError(f"Unknown candidate route: {route}")


def run_case(name, route, page, n, a):
    opcode, direct_sequence, store, space = INSTRUCTIONS[name]
    state = State(n=n, pg=page)
    state.registers = [0xA6] * 8
    state.registers[7] = 0x80
    state.registers[n] = 0x20
    # X can itself be PC. F0 has already incremented it when F1 reads X.
    address = 0x21 if n == 7 else 0x80
    source = 0x21 if a == n else address if a == 7 else 0xA6
    memory = {"program": {(page << 8) | 0x20: opcode | a}, "storage": {}}
    target = (page << 8) | address
    memory[space][target] = 0x11 if store else 0x69
    sequence = (direct_sequence[0], address_phase(route, store), direct_sequence[2])
    cpu = Simulator(state)
    access_phases = []

    for phase, slots in enumerate(sequence):
        for timing, mops in enumerate(slots):
            cpu.state.phase, cpu.state.timing = phase, timing
            external = None
            if 23 not in mops and (24 in mops or 25 in mops):
                selected_space = "program" if 24 in mops else "storage"
                full_address = (page << 8) | cpu.state.ab
                external = memory[selected_space].get(full_address)
                access_phases.append(phase)
            cpu.capture(mops, external_db=external, memory_ready=True)
            if store and phase == 2 and timing == 5:
                signals = evaluate(cpu.state, mops, memory_ready=True)
                memory[space][(page << 8) | cpu.state.ab] = signals.db

    assert 1 not in access_phases, "Unexpected operand-memory access"
    assert cpu.state.ab == address
    assert memory[space][target] == (source if store else 0x69)
    if not store:
        assert cpu.state.registers[a] == 0x69
    if store or a != n:
        assert cpu.state.registers[n] == 0x21


def main():
    count = 0
    for route, name, page, n, a in product(
            ("loopback", "direct"), INSTRUCTIONS, range(4), range(8), range(8)):
        run_case(name, route, page, n, a)
        count += 1
    print(f"{count} manual v006 datapath experiments passed for both address routes.")
    print("Schedules remain hypotheses; indexed opcode decoding is not yet implemented.")


if __name__ == "__main__":
    main()
