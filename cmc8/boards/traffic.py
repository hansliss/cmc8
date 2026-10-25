"""Run the book's traffic program on the unchanged v018 MOP simulator.

python3 -m cmc8.boards.traffic --delay-count 1  # Explicit shortened fixture.
python3 -m cmc8.boards.traffic                 # Literal book delay count122.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

from cmc8.versions.v018 import InstructionSimulator, InterruptInput, ResetInput, RunInputs, State
from .harness import BoardHarness, BytePort, PortMemory

ROOT = Path(__file__).resolve().parents[2]


def source_program():
    return json.loads((ROOT/'specification/traffic-program.json').read_text())


def make_board(*, delay_count=None, trace_limit=64):
    source = source_program()
    program = {int(c['address'], 8): int(c['byte'], 8) for c in source['cells']}
    if delay_count is not None:
        if type(delay_count) is not int or not 1 <= delay_count <= 255:
            raise ValueError('delay_count must be 1..255; None preserves the source byte')
        program[0o103] = delay_count
    lamps = BytePort('traffic lamps ED4', readable=False)
    memory = PortMemory(program=program, program_readonly_pages={0}, ports={4: lamps})
    # The fixture explicitly disables/clears IRQ state; the reset table does
    # not promise those values. Reset is observed after a stated T7 sample.
    state = State(inte=0, intr=0)
    cpu = InstructionSimulator(state, memory, reset=ResetInput(1), reset_sampled=True,
                               interrupts=InterruptInput(1), run_inputs=RunInputs(memr=0, halt=1, ss=1),
                               test_inputs=(0, 0, 0, 0))
    return BoardHarness(cpu, subdivision_ns=source['subdivision_nanoseconds'], trace_limit=trace_limit)


def lamp_state(value):
    """Figure8.3: main bits0..2, side bits5..7; 1 means the lamp is on."""
    return {road: [name for bit, name in enumerate(('red', 'yellow', 'green'), start)
                   if value & (1 << bit)] for road, start in [('main', 0), ('side', 5)]}


def delay_cycles(count):
    """Independent arithmetic for the literal INR/BZ0, DCR/BZ0 loop."""
    return 4 + count*(256*5+5) + 2


def run_cycle(*, delay_count=None, sensor=1, idle_polls=3, trace_limit=64, progress=None):
    if sensor not in (1, 3):
        raise ValueError('The example uses side-road sensors T1 and T3')
    board = make_board(delay_count=delay_count, trace_limit=trace_limit)
    board.run_until(lambda b: len(b.writes) == 1, max_slots=256)
    # Complete startup, then check several complete no-demand polling loops.
    board.run_until(lambda b: b.boundary and b.cpu.state.registers[0] == 0o004, max_slots=64)
    for _ in range(idle_polls*3):
        board.run_event()
    assert len(board.writes) == 1, 'Idle polling unexpectedly changed the lamps'
    levels = [0, 0, 0, 0]
    levels[sensor] = 1
    board.cpu.test_inputs = tuple(levels)
    # The first branch into the service sequence establishes that the
    # demand was sampled. Deassert before another cycle can be requested.
    board.run_until(lambda b: b.boundary and b.cpu.state.registers[0] == 0o012, max_slots=64)
    board.cpu.test_inputs = (0, 0, 0, 0)
    last_count = len(board.writes)
    budget = 16_000_000
    for _ in range(budget):
        if len(board.writes) == 7 and board.boundary and board.cpu.state.registers[0] == 0o004:
            break
        board.step()
        if len(board.writes) != last_count:
            last_count = len(board.writes)
            if progress is not None:
                progress(board.writes[-1])
    else:
        raise RuntimeError('Traffic cycle exceeded the research run budget')
    # Leave the sensors low and verify that normal polling resumes.
    for _ in range(9):
        board.run_event()
    return board


def cycle_report(board, *, delay_count=None, sensor=1):
    """Serialize the observed result; this function does not execute the CPU."""
    count = 0o172 if delay_count is None else delay_count
    return {'model':'v018', 'program':'figure8.6', 'literal_book_bytes':delay_count is None,
            'sensor':sensor, 'delay_count_decimal':count, 'delay_routine_cycles':delay_cycles(count),
            'subdivisions':board.subdivisions, 'elapsed_ns':board.time_ns,
            'events':board.completed_events, 'port_writes':[asdict(w) for w in board.writes],
            'final_n':board.cpu.state.n, 'final_pc_octal':f'{board.cpu.state.registers[0]:03o}',
            'final_ed4_octal':f'{board.cpu.memory.ports[4].value:03o}',
            'trace_tail_slots':len(board.cpu.trace)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--delay-count', type=int, help='Explicitly replace octal103 for a shortened run')
    parser.add_argument('--sensor', type=int, choices=(1, 3), default=1)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--output', type=Path, help='Write the same result JSON to a file')
    args = parser.parse_args()
    def progress(event):
        if not args.json:
            print(f'{event.time_ns/1e9:10.6f}s ED4={event.value:03o} '
                  f'{lamp_state(event.value)}', flush=True)
    board = run_cycle(delay_count=args.delay_count, sensor=args.sensor, progress=progress)
    report = cycle_report(board, delay_count=args.delay_count, sensor=args.sensor)
    if args.output:
        args.output.write_text(json.dumps(report,indent=2)+'\n')
    if args.json:
        print(json.dumps(report,indent=2))
    else:
        print(f"Completed: {board.subdivisions} subdivisions; "
              f"{board.completed_events} CPU events; source bytes {'preserved' if args.delay_count is None else 'explicitly patched'}.")


if __name__ == '__main__':
    main()
