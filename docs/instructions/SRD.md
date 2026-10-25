# SRD

[All instructions](../instruction-set.md)

**Encoding:** `00011RRR`; **bytes:** 2; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Store R(A) into an external device selected by the address byte.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [43: Figure 4.3: page addressing](../../bookpages/Page_049.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Four pages each for program/storage, AB-only I/O; LSX retains three cycles to simplify control. PDF page 50. |
| [38: Figure 4.2: MOP list](../../bookpages/Page_044.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Numbered functional controls; not necessarily independent physical silicon wires. PDF page 45. |
| [39: Figure 4.1: processor principle diagram](../../bookpages/Page_045.jpg) | Address/register selection and transfer vocabulary; shared framework rather than a dedicated table for every instruction. Register selectors, buses, ALU, latch paths and interrupt controls; explicitly simplified. PDF page 46. |
| [95: Figure 6.11: output port](../../bookpages/Page_101.jpg) | External registers behave like memory words enabled with EDE; device latch behavior is external to CPU. Address decode + EDE + WRITE loads port latch. Prose prints output address 001; figures 6.10/6.11 show 00. Accepted project correction E007 changes the output address to 00; input address 001 remains correct. PDF page 102. |
| [96: Figures 6.12/6.13: input port](../../bookpages/Page_102.jpg) | External registers behave like memory words enabled with EDE; device latch behavior is external to CPU. EDE and physical DBDIR high admit read data; tristate otherwise. PDF page 103. |
| [113: Figure 7.5: bidirectional port](../../bookpages/Page_119.jpg) | External registers behave like memory words enabled with EDE; device latch behavior is external to CPU. A register behaves like a memory word activated by EDE rather than PME/SME. PDF page 120. |
| [126: MIDAHS memory and port tests](../../bookpages/Page_132.jpg) | External registers behave like memory words enabled with EDE; device latch behavior is external to CPU. Parallel SRM/LRM and SRS/LRS programs; LRM data window F2T2–T5; LRD/SRD opcodes in lower table. PDF page 133. |
| [93: Figure 6.9: lamp polling example](../../bookpages/Page_099.jpg) | Worked polling loop using the named instruction. LRI/SRD/LRD/ANI/BZ0 polling sequence; generic OUT/STORE references in surrounding prose are not CMC8 mnemonics. PDF page 100. |
| [94: Lamp polling interpretation](../../bookpages/Page_100.jpg) | Explanation of accumulator effects and immediate masking. Explains immediate data load, port transfer and ANI mask replacing accumulator contents; octal numeric notation. PDF page 101. |
| [155: Figure 8.12: increment-address command](../../bookpages/Page_161.jpg) | Indexed read and branch-back in a concrete application sequence. LRD R7, INR R7, SRD R7, LRX R5, SRD R5, JMP page3; SRD R7 machine-code field prints 032 instead of expected 037. Accepted project correction E006: R7 is intended by the read/increment/write sequence. PDF page 162. |

## Working findings and assumptions

- **consistency-supported extrapolation; working:** Reuse load/store sequence with EDE; I/O addresses use AB alone. Device register capture at WRITE falling is a harness assumption. Sources: pp. 43, 95, 96, 113.
- **established project correction; E006; accepted by project owner:** Figure 8.12 at octal 052 intends SRD R7 after reading and incrementing R7. Correct printed opcode 032 (R2) to 037 (R7), preserving the literal field. Sources: pp. 155, 67.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | 6,19,21 | 19,21,23 |
| F2 | 19,21,23,26 | 19,21,23,26,27 | 19,21,23,26,27 | 19,21,23,26,27 | 19,21,23,26,27 | 19,21,23,26 | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

18 candidate line matches on proposed printed pages: 67, 93, 94, 126, 127, 128, 129, 146, 147, 150, 155.

[All snippets and scan links](../instruction-mentions.md#srd). These are unreviewed leads and may include other-architecture examples.
