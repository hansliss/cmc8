# LRX

[All instructions](../instruction-set.md)

**Encoding:** `01001RRR`; **bytes:** 1; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Load R(A) from program memory addressed by X.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [43: Figure 4.3: page addressing](../../bookpages/Page_049.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Four pages each for program/storage, AB-only I/O; LSX retains three cycles to simplify control. PDF page 50. |
| [38: Figure 4.2: MOP list](../../bookpages/Page_044.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Numbered functional controls; not necessarily independent physical silicon wires. PDF page 45. |
| [39: Figure 4.1: processor principle diagram](../../bookpages/Page_045.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Register selectors, buses, ALU, latch paths and interrupt controls; explicitly simplified. PDF page 46. |
| [43: Figure 4.3: page addressing](../../bookpages/Page_049.jpg) | Indexed operation and three-cycle simplification; AND supplies a reusable X→BR path, not a literal indexed microprogram. Four pages each for program/storage, AB-only I/O; LSX retains three cycles to simplify control. PDF page 50. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | Indexed operation and three-cycle simplification; AND supplies a reusable X→BR path, not a literal indexed microprogram. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Indexed operation and three-cycle simplification; AND supplies a reusable X→BR path, not a literal indexed microprogram. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [155: Figure 8.12: increment-address command](../../bookpages/Page_161.jpg) | Indexed read and branch-back in a concrete application sequence. LRD R7, INR R7, SRD R7, LRX R5, SRD R5, JMP page3; SRD R7 machine-code field prints 032 instead of expected 037. Accepted project correction E006: R7 is intended by the read/increment/write sequence. PDF page 162. |

## Working findings and assumptions

- **consistency-supported extrapolation; working:** Selected H006-A: X→DI→DB→BR at F1T5, then BR→AB at F1T6; F2 reuses direct memory transfer. H006-B direct X→DI→AB remains backup. Sources: pp. 43, 75.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 20,21 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23,2 | 6 | — |
| F2 | — | — | 24 | 24 | 29,24 | 2,24 | 4,22,19 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

2 candidate line matches on proposed printed pages: 67, 155.

[All snippets and scan links](../instruction-mentions.md#lrx). These are unreviewed leads and may include other-architecture examples.
