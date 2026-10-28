#!/usr/bin/env python3
"""Compare actual native T-slot execution with the Python v018 board oracle.

Needs the research repository; the console app does not. No expected register
transfers or light states are manufactured inside the native CPU under test.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cmc8.boards.traffic import make_board


def main():
    executable = sys.argv[1] if len(sys.argv)>1 else ROOT/'x7_traffic/build-host/traffic-host'
    count = 16000
    result = subprocess.run([str(executable), '--trace', str(count)],
                            check=True, capture_output=True, text=True)
    rows = result.stdout.splitlines()
    if len(rows) != count:
        raise SystemExit('Incomplete native trace')
    board = make_board()
    instructions = set()
    for index, line in enumerate(rows):
        if index == 200:
            board.cpu.test_inputs = (0,1,0,0)
        if index == 500:
            board.cpu.test_inputs = (0,0,0,0)
        row = board.step()
        state = board.cpu.state
        instructions.add(row.instruction)
        expected = [index, sum(1<<number for number in set(row.mops)),
                    row.phase, row.timing, state.ir, state.br, state.ab, state.pg,
                    state.n, state.z, state.h, state.t, state.phase, state.timing,
                    *state.registers]
        for point in (row.start, row.end):
            wires = point.signals
            expected += [wires.selected_register, wires.di, wires.db, wires.alu, wires.mux]
        expected += [board.cpu.memory.ports[4].value]
        expected = [-1 if value is None else value for value in expected]
        actual = list(map(int,line.split()))
        if actual != expected:
            raise SystemExit(f'MOP mismatch at subdivision {index}, F{row.phase}T{row.timing}\n'
                             f'Native: {actual}\nOracle: {expected}')
    if 'DCR' not in instructions:
        raise SystemExit('Trace did not cover the selected DCR zero detector')
    print(f'{count} consecutive v018 slots match: MOPs, state, leading/trailing wires, ED4')


if __name__ == '__main__':
    main()
