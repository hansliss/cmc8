#!/usr/bin/env python3
"""Preserve the web demo's assembled monitor and SWITCHES images for the C app."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]


def cells(path):
    result = {}
    ended = False
    for line in path.read_text().splitlines():
        if ended or not line.startswith(':'):
            raise ValueError('Invalid HEX record')
        record = bytes.fromhex(line[1:])
        count, high, low, kind = record[:4]
        if len(record) != count+5 or sum(record)&255:
            raise ValueError('Invalid HEX length/checksum')
        address = high*256+low
        if kind == 1 and count == 0 and address == 0:
            ended = True
        elif kind == 0 and address+count <= 1024:
            for offset, value in enumerate(record[4:-1]):
                if address+offset in result:
                    raise ValueError('Overlapping HEX data')
                result[address+offset] = value
        else:
            raise ValueError('Unsupported HEX record')
    if not ended:
        raise ValueError('Missing EOF')
    return result


def main():
    lines = ['/* Generated from the web demo HEX; reconstructed monitor, not original ROM. */',
             '#ifndef X7_MIDAHS_PROGRAMS_H', '#define X7_MIDAHS_PROGRAMS_H',
             'static const struct { unsigned short address; unsigned char value; } initial_cells[] = {']
    for name in ('switches', 'monitor'):
        lines.append('    /* ' + name + ' */')
        lines.extend(f'    {{{address}, {value}}},' for address, value in cells(ROOT/f'demos/midahs/{name}.hex').items())
    lines += ['};', '#endif', '']
    output = ROOT/'x7_midahs/generated/programs.h'
    text = '\n'.join(lines)
    if '--check' in sys.argv:
        if output.read_text() != text:
            raise SystemExit('Stale generated/programs.h')
        print('Native images match web monitor/SWITCHES HEX')
    else:
        output.write_text(text)


if __name__ == '__main__':
    main()
