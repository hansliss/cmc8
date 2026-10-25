# SRS

[All instructions](../instruction-set.md)

**Encoding:** `01110RRR`; **bytes:** 2; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Store R(A) into storage memory at the address byte.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [43: Figure 4.3: page addressing](../../bookpages/Page_049.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Four pages each for program/storage, AB-only I/O; LSX retains three cycles to simplify control. PDF page 50. |
| [38: Figure 4.2: MOP list](../../bookpages/Page_044.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Numbered functional controls; not necessarily independent physical silicon wires. PDF page 45. |
| [39: Figure 4.1: processor principle diagram](../../bookpages/Page_045.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Register selectors, buses, ALU, latch paths and interrupt controls; explicitly simplified. PDF page 46. |
| [52: Figure 4.10: fetch controls](../../bookpages/Page_058.jpg) | Store-specific signaling and example; numbered held controls remain derived. Numbered fetch table and alternatives; MOP6 needed by stores at F1T6. PDF page 59. |
| [54: Figure 4.12 and SRS differences](../../bookpages/Page_060.jpg) | Store-specific signaling and example; numbered held controls remain derived. Full LRS MOP table with recorded MOP1/2 errors; section 3.4 explains store signaling changes. PDF page 61. |
| [55: Figure 4.13: SRS timing](../../bookpages/Page_061.jpg) | Store-specific signaling and example; numbered held controls remain derived. Store output direction, early SME and WRITE pulse; contains no full numbered SRS table. PDF page 62. |
| [126: MIDAHS memory and port tests](../../bookpages/Page_132.jpg) | Store-specific signaling and example; numbered held controls remain derived. Parallel SRM/LRM and SRS/LRS programs; LRM data window F2T2–T5; LRD/SRD opcodes in lower table. PDF page 133. |

## Working findings and assumptions

- **derived; working:** Held internal store controls reproduce figure 4.13; no complete printed SRS MOP table has been found. Sources: pp. 55.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | 6,19,21 | 19,21,23 |
| F2 | 19,21,23,25 | 19,21,23,25,27 | 19,21,23,25,27 | 19,21,23,25,27 | 19,21,23,25,27 | 19,21,23,25 | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

9 candidate line matches on proposed printed pages: 54, 55, 67, 125, 126, 139, 218.

[All snippets and scan links](../instruction-mentions.md#srs). These are unreviewed leads and may include other-architecture examples.
