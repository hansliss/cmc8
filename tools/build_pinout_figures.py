"""Render the tentative pinout as an SVG and CSV; source photos stay unchanged."""
import csv
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    data = json.loads((ROOT / 'specification/pinout-hypothesis.json').read_text())
    pads = sorted(data['pads'], key=lambda p: p['candidate_package_pin'])
    with (ROOT / 'specification/pinout-hypothesis.csv').open('w', newline='') as output:
        fields = ['candidate_package_pin', 'candidate_signal', 'id', 'die_label',
                  'evidence_basis', 'connector_reference', 'package_assignment_status']
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(pads)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1340" height="680" viewBox="0 0 1340 680">',
           '<rect width="1340" height="680" fill="white"/>',
           '<style>text{font-family:Arial,sans-serif;fill:#172b40}.pin{font-size:15px}.note{font-size:17px}</style>',
           '<text x="40" y="40" font-size="26">CMC8 — tentative package pinout, hypothesis PIN001</text>',
           '<text x="40" y="72" class="note">Top view; notch left. Every external pin assignment remains conditional.</text>',
           '<rect x="72" y="230" width="1188" height="155" rx="12" fill="#eef3f7" stroke="#43576b" stroke-width="2"/>',
           '<path d="M72 277 A30 30 0 0 1 72 337" fill="white" stroke="#43576b" stroke-width="2"/>',
           '<circle cx="98" cy="367" r="5" fill="#43576b"/>',
           '<text x="520" y="300" font-size="24">ASEA-HAFO CMC8</text>',
           '<text x="435" y="335" class="note">40-pad order + figure 7.6 connector hypothesis</text>']
    for p in pads:
        pin = p['candidate_package_pin']
        lower = pin <= 20
        column = pin-1 if lower else 40-pin
        x = 115+58*column
        edge, tip = (385, 414) if lower else (230, 201)
        color = '#196d55' if p['die_label'] is not None else '#aa6300'
        svg.append(f'<path d="M{x} {edge} V{tip}" stroke="{color}" stroke-width="8"/>')
        y = 442 if lower else 177
        rotation = 55 if lower else -55
        label = escape(f"{pin}: {p['candidate_signal']}")
        svg.append(f'<text class="pin" transform="translate({x},{y}) rotate({rotation})">{label}</text>')
    svg += [
        '<text x="40" y="577" class="note" style="fill:#196d55">Green terminal: signal explicitly labeled on the die overview.</text>',
        '<text x="40" y="607" class="note" style="fill:#aa6300">Amber terminal: signal inferred from pad pattern and/or connector ordering.</text>',
        '<text x="40" y="637" class="note">Colors describe die-signal evidence, not confidence in an external pin number. Pin numbers are proposed.</text>',
        '</svg>']
    (ROOT / 'docs/figures/pinout-hypothesis.svg').write_text('\n'.join(svg)+'\n')
    print('Built tentative package SVG and CSV from the authored pad inventory.')


if __name__ == '__main__':
    build()
