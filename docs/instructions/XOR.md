# XOR

[All instructions](../instruction-set.md)

**Encoding:** `10101RRR`; **bytes:** 1; **cycles:** 3; **flag column:** Z.

**Book summary (documented summary):** Exclusive-OR R(A) and X; result to X.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | Detailed AND example; XOR shares operand/result roles in figure 5.1, not a separate detailed table. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |

## Working findings and assumptions

- **consistency-supported extrapolation; H015 selected in v012; likely:** Use the AND schedule unchanged except substitute XOR MOP8 for AND MOP9. Same X buffer preparation, R(A) operand, ALU/Z capture F2T3 and result→X F2T4. Figure 5.1 documents the matching operands, result destination, three cycles and Z effect. Sources: pp. 67, 75, 38.

## Open questions

- No dedicated XOR MOP table found; operation substitution follows the consistency principle.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 20,21 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23,2 | — | — |
| F2 | 19,21 | 19,21 | 19,21 | 19,21,3,7,8,32,12 | 4,22,20 | — | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

12 candidate line matches on proposed printed pages: 17, 18, 19, 27, 67, 72, 74.

[All snippets and scan links](../instruction-mentions.md#xor). These are unreviewed leads and may include other-architecture examples.
