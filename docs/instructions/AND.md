# AND

[All instructions](../instruction-set.md)

**Encoding:** `10110RRR`; **bytes:** 1; **cycles:** 3; **flag column:** Z.

**Book summary (documented summary):** AND R(A) and X; result to X.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | Detailed AND example; XOR shares operand/result roles in figure 5.1, not a separate detailed table. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### AND, figure 5.7

[75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | X→DI | DI→DB | — | — | — | DB→BR | — | — |
| F2 | R(A)→DI | — | — | DI·BR→BR; update Z | BR→X | — | — | 0→F |

- Printed MOP23 appears at T0 and T1, while the functional DI→DB is placed at T1.
- Sparse numbered entries do not specify every held gate level.

Literal numbered row (conditional overlays may be described in the notes):

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 20,21,23 | 23 | — | — | — | 2 | — | — |
| F2 | 19,21 | — | — | 3,7,9,32,12 | 4,22,20 | — | — | 30 |

## Working findings and assumptions

- **documented functional sequence; derived held controls; H012 selected in v011:** Use the established X→DI→DB→BR preparation with DB drive starting F1T1 (functional placement), retaining the sparse numbered-row T0 discrepancy. Hold R(A) on DI through F2T3; MOP3+7+9+12+32 capture AND result and ALU-zero Z together at T3, then BR→X at T4. No execute memory access or extra PC increment. Sources: pp. 75, 38.

## Open questions

- Figure 5.7 functional DI→DB at T1 and numbered row MOP23 at T0 differ; held-level controls are incomplete.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 20,21 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23,2 | — | — |
| F2 | 19,21 | 19,21 | 19,21 | 19,21,3,7,9,32,12 | 4,22,20 | — | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

51 candidate line matches on proposed printed pages: 7, 11, 12, 16, 17, 18, 19, 27, 46, 67, 75, 86, 87, 94, 95, 97, 131, 135, 158, 159, 186, 190, 215, 216, 217, 218.

[All snippets and scan links](../instruction-mentions.md#and). These are unreviewed leads and may include other-architecture examples.
