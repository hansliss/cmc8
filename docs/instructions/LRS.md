# LRS

[All instructions](../instruction-set.md)

**Encoding:** `01010RRR`; **bytes:** 2; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Load R(A) from storage memory at the address byte.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [43: Figure 4.3: page addressing](../../bookpages/Page_049.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Four pages each for program/storage, AB-only I/O; LSX retains three cycles to simplify control. PDF page 50. |
| [38: Figure 4.2: MOP list](../../bookpages/Page_044.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Numbered functional controls; not necessarily independent physical silicon wires. PDF page 45. |
| [39: Figure 4.1: processor principle diagram](../../bookpages/Page_045.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Register selectors, buses, ALU, latch paths and interrupt controls; explicitly simplified. PDF page 46. |
| [30: Figure 3.2: meaning of LRS](../../bookpages/Page_036.jpg) | Detailed load model; compare functional sequence with literal numbered table. Introduces the CMC8 load operation; surrounding LDA/MOV examples belong to other architectures. PDF page 37. |
| [31: LRS format and three phases](../../bookpages/Page_037.jpg) | Detailed load model; compare functional sequence with literal numbered table. Fetch, operand-address fetch, final read; PC advances for both bytes. Also identifies REL as one cycle and JMP as two. PDF page 38. |
| [49: Figure 4.9: LRS bus timing](../../bookpages/Page_055.jpg) | Detailed load model; compare functional sequence with literal numbered table. Memory enables, address changes and data-valid deadlines. PDF page 56. |
| [50: LRS encoding and read deadlines](../../bookpages/Page_056.jpg) | Detailed load model; compare functional sequence with literal numbered table. 01010RRR plus address byte; F1/F2 read timing and 375 ns example. PDF page 57. |
| [51: Common fetch description](../../bookpages/Page_057.jpg) | Detailed load model; compare functional sequence with literal numbered table. Common through T5; one-cycle instructions use T6/T7. IR open during T5. PDF page 58. |
| [52: Figure 4.10: fetch controls](../../bookpages/Page_058.jpg) | Detailed load model; compare functional sequence with literal numbered table. Numbered fetch table and alternatives; MOP6 needed by stores at F1T6. PDF page 59. |
| [53: Figure 4.11: LRS functional microprogram](../../bookpages/Page_059.jpg) | Detailed load model; compare functional sequence with literal numbered table. All three phases; IR final capture at end T5, BR capture at start T5. PDF page 60. |
| [54: Figure 4.12 and SRS differences](../../bookpages/Page_060.jpg) | Detailed load model; compare functional sequence with literal numbered table. Full LRS MOP table with recorded MOP1/2 errors; section 3.4 explains store signaling changes. PDF page 61. |
| [126: MIDAHS memory and port tests](../../bookpages/Page_132.jpg) | Detailed load model; compare functional sequence with literal numbered table. Parallel SRM/LRM and SRS/LRS programs; LRM data window F2T2–T5; LRD/SRD opcodes in lower table. PDF page 133. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### LRS, figure 4.11

[53: Figure 4.11: LRS functional microprogram](../../bookpages/Page_059.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | R(N)→DI | DI→AB | PME rises | DI+1→BR | BR→R(N) | DB→IR | BR→AB; PME falls | — |
| F1 | R(N)→DI | — | PME rises | DI+1→BR | BR→R(N) | DB→BR | BR→AB; PME falls | — |
| F2 | — | — | SME rises | — | — | DB→BR | BR→R(A); SME falls | 0→F |

- IR is transparent during T5; BR captures at the T4→T5 boundary. See p.53 prose.
- Figure 4.12 supplies a numbered table but prints MOP1 at the two execution reads; the established project correction is MOP2.

## Working findings and assumptions

- **documented; established project correction:** Use MOP2 at F1T5/F2T5; printed figure 4.12 MOP1 conflicts with its transfer description and figure 4.2. Sources: pp. 53, 54, 38.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | 6 | — |
| F2 | — | — | 25 | 25 | 29,25 | 2,25 | 4,22,19 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

60 candidate line matches on proposed printed pages: 30, 31, 32, 35, 37, 40, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 56, 58, 60, 67, 68, 69, 72, 119, 121, 122, 124, 125, 126, 217.

[All snippets and scan links](../instruction-mentions.md#lrs). These are unreviewed leads and may include other-architecture examples.
