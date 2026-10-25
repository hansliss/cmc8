# INR

[All instructions](../instruction-set.md)

**Encoding:** `10000RRR`; **bytes:** 1; **cycles:** 3; **flag column:** Z.

**Book summary (documented summary):** Increment R(A).

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [76: Figure 5.8: INR/DCR microprograms](../../bookpages/Page_082.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. Increment and complemented increment/decrement; captures and final register writes. Held gates across phases are implicit; the three-cycle model uses both F1 and F2 without a phase skip. PDF page 83. |
| [77: Figure 5.9 and omitted DCR flag circuitry](../../bookpages/Page_083.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. SHR/ROR/RRL semantics; explicitly says DCR zero-detection controls omitted from figure 5.8. PDF page 84. |
| [143: Figure 8.5: wait subroutine](../../bookpages/Page_149.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. LRI, INR, BZ0, DCR, RSR with octal machine code and per-instruction cycles; INR explicitly three cycles. PDF page 150. |
| [147: Figure 8.6 part 2](../../bookpages/Page_153.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. NOP padding; LRI/INR/BZ0/DCR/RSR delay routine. Printed octal172 is retained; its parenthetical decimal76 conflicts with decimal122 and the p.144 calculation (candidate E009). PDF page 154. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | Z detects wrap to zero; timing calculation corroborates three cycles. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |
| [144: Wait-subroutine timing](../../bookpages/Page_150.jpg) | Z detects wrap to zero; timing calculation corroborates three cycles. JSR call example; computed timing uses (3+2) cycles for INR+branch. SCW used as halt in this system setup. PDF page 151. |
| [155: Figure 8.12: increment-address command](../../bookpages/Page_161.jpg) | Indexed read and branch-back in a concrete application sequence. LRD R7, INR R7, SRD R7, LRX R5, SRD R5, JMP page3; SRD R7 machine-code field prints 032 instead of expected 037. Accepted project correction E006: R7 is intended by the read/increment/write sequence. PDF page 162. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### INR, figure 5.8

[76: Figure 5.8: INR/DCR microprograms](../../bookpages/Page_082.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | R(A)→DI | DI→DB | — | — | — | — | — | — |
| F2 | — | — | — | DI+1→BR; update Z | — | — | BR→R(A) | 0→F |

- Figure 5.1 and application cycle counts establish three cycles.
- The preceding p.75 prose refers to F2T2 for the flag update; the table places the operation at T3.

Literal numbered row (conditional overlays may be described in the notes):

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 21,19 | 23 | — | — | — | — | — | — |
| F2 | — | — | — | 10,7,12,32 | — | — | 4,19,22 | 30 |

## Working findings and assumptions

- **documented functional sequence; source-conflict interpretation; H013 selected in v011; T3 selected over prose T2:** Hold R(A) on DI across full F1 and through F2T3; do not invent a missing F1 DB→BR capture. Follow figure 5.8: DI+1→BR with MOP32 testing ALU zero at T3, then BR→R(A) at T6. Preserve three cycles and the prose T2 alternative. Sources: pp. 76, 75, 143, 144.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

- Figure 5.8 leaves held register gates and the relation of its F1 preparation to F2 implicit. v011 holds the source across both full phases. Keep figure 5.1/8.5 three-cycle count; no phase skip is selected.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 19,21 | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23 |
| F2 | 19,21 | 19,21 | 19,21 | 19,21,10,7,12,32 | — | — | 4,19,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

13 candidate line matches on proposed printed pages: 17, 19, 45, 46, 67, 75, 76, 143, 147, 155.

[All snippets and scan links](../instruction-mentions.md#inr). These are unreviewed leads and may include other-architecture examples.
