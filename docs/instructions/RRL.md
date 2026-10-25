# RRL

[All instructions](../instruction-set.md)

**Encoding:** `10011RRR`; **bytes:** 1; **cycles:** 2; **flag column:** L.

**Book summary (documented summary):** Rotate R(A) right through Link.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [77: Figure 5.9 and omitted DCR flag circuitry](../../bookpages/Page_083.jpg) | Right-shift/rotation semantics and dedicated mux/link circuits. Only RRL has a full illustrated functional example here. SHR/ROR/RRL semantics; explicitly says DCR zero-detection controls omitted from figure 5.8. PDF page 84. |
| [78: Figure 5.10: shift multiplexer](../../bookpages/Page_084.jpg) | Right-shift/rotation semantics and dedicated mux/link circuits. Only RRL has a full illustrated functional example here. MOP11 shifts ALU→BR. ROR wraps bit0; SHR grounds bit7; RRL uses a master/slave Link. Explicitly says figure-5.11 gates are only a principle and physical controls are partly coded. PDF page 85. |
| [79: Figures 5.11/5.12: RRL circuits and microprogram](../../bookpages/Page_085.jpg) | Right-shift/rotation semantics and dedicated mux/link circuits. Only RRL has a full illustrated functional example here. Link path and shift timing. Printed 30 at F1T1 conflicts with functional 2→F; figure 5.11 uses 57 for zero insertion. PDF page 86. |
| [107: CMC8 Link and serial transfer](../../bookpages/Page_113.jpg) | Eight rotations emit source bits LSB first; a full nine-bit register-plus-Link cycle takes nine rotations. CMC8 has direct LOUT from Link. Eight RRLs emit a register LSB first; setting Link from a test input before each RRL permits serial reception. Earlier UART/SCMP comparisons do not define CMC8 circuitry. PDF page 114. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### RRL, figure 5.12

[79: Figures 5.11/5.12: RRL circuits and microprogram](../../bookpages/Page_085.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | R(A)→DI | 2→F; DI→DB | — | — | — | — | — | — |
| F2 | — | — | rotate DI through L into BR | — | — | BR→DI | DI→R(A) | 0→F |

- The F1T1 numbered row prints 30, but its 2→F function corresponds to MOP31 in figure 4.2.
- Figure 5.11 adds a zero-insertion control numbered 57; correspondence to MOP43 needs review.

Literal numbered row (conditional overlays may be described in the notes):

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 19,21 | 19,21,23,30 | — | — | — | — | — | — |
| F2 | — | — | 19,21,7,11,12,33 | — | — | 4 | 19,22,4 | 30 |

## Working findings and assumptions

- **derived datapath realization from documented sequence; H017 selected in v013:** Figure 5.12 uses MOP7 without B enable or arithmetic operation: model DI passthrough through ALU. MOP11 shifts; MOP13 wraps ALU bit0, MOP43/57 insert zero, MOP33 uses old Link for bit7 while sampling ALU bit0 into new Link. These are functional control abstractions, not recovered physical wire coding. Sources: pp. 79, 78, 38, 77.
- **established project correction; derived held controls; E003; selected in v013 and subsequently accepted by project owner:** Replace printed F1T1 MOP30 with MOP31, matching its functional 2→F and the two-cycle phase-skip mechanism. Follow the table: shift/Link capture F2T2, BR→DI T5, register write T6, phase reset T7. Preserve literal numbered row and endpoint timing limitations. Sources: pp. 79, 38, 70.
- **cross-instruction consistency finding; tested in v013; timing confidence unchanged:** Eight RRLs reproduce the serial-output behavior described on p.107. BT/SEL/REL/RRL programs receive serial bytes through the selected deferred flag timing; RRL/BL programs consume shifted-out Link. These tests check model consistency rather than physical timing. Sources: pp. 107, 79.

## Open questions

- Figure 5.11 labels zero insertion 57 while figure 4.2 uses 43. v013 models their stated function as equivalent, without asserting the physical encodings are identical; selected SHR tables use 43.
- E003 is now an accepted project correction; physical Link master/slave edges inside T2 remain unspecified by the endpoint model.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 19,21 | 19,21,23,31 | — | — | — | — | — | — |
| F2 | — | — | 19,21,7,11,12,33 | — | — | 4 | 19,22,4 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

7 candidate line matches on proposed printed pages: 67, 77, 78, 79, 107.

[All snippets and scan links](../instruction-mentions.md#rrl). These are unreviewed leads and may include other-architecture examples.
