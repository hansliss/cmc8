"""Check the pin-order hypothesis against authored observations; not hardware validation.

Run with python3 -m tools.check_pinout_hypothesis. This uses the explicit
figure3.5 pad inventory and figure7.6 connector transcription, not simulator
state or an assumed pinout imported from another processor.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((ROOT / 'specification/pinout-hypothesis.json').read_text())
    pads = data['pads']
    assert len(pads) == 40
    assert {p['candidate_package_pin'] for p in pads} == set(range(1, 41))
    assert len({p['candidate_signal'] for p in pads}) == 40
    for source in data['sources'].values():
        assert (ROOT / source).exists(), source
    # This tests only the proposed correspondence between connector row
    # numbers and chip pins. Rows without die labels cannot score a match.
    connector = {r['row']: r['a'] for r in data['connector_rows'] if r['row'] <= 31}
    observed = [p for p in pads if p['die_label'] is not None]
    scores = []
    for direction in (-1, 1):
        for offset in range(40):
            matches = sum(connector.get(1+(offset+direction*p['clockwise_index']) % 40)
                          == p['die_label'] for p in observed)
            scores.append((matches, direction, offset))
    scores.sort(reverse=True)
    best = scores[0]
    assert best == (15, -1, 33), best
    assert scores[1][0] < best[0]
    for p in pads:
        assert p['candidate_package_pin'] == 1+(33-p['clockwise_index']) % 40
        if p['die_label'] is not None:
            assert p['candidate_signal'] == p['die_label']
    by_signal = {p['candidate_signal']: p for p in pads}
    vdd = by_signal['VDD']['clockwise_index']
    db0 = by_signal['DB0']['clockwise_index']
    vss = by_signal['VSS']['clockwise_index']
    assert (vdd-db0) % 40-1 == 11
    assert (vdd-vss) % 40 == 20
    print('40 pads and 40 distinct proposed pins/signals; all source files present.')
    print(f'Conditional connector-order fit: {best[0]}/15 die labels; '
          f'next-best cyclic fit {scores[1][0]}/15.')
    print('This is a consistency check under the stated ordering assumptions, not pinout proof.')


if __name__ == '__main__':
    main()
