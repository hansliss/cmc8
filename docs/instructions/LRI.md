# LRI

[All instructions](../instruction-set.md)

**Encoding:** `00100RRR`; **bytes:** 2; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Load the immediate second byte into R(A).

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Immediate byte format and initialization examples. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [126: MIDAHS memory and port tests](../../bookpages/Page_132.jpg) | Immediate byte format and initialization examples. Parallel SRM/LRM and SRS/LRS programs; LRM data window F2T2–T5; LRD/SRD opcodes in lower table. PDF page 133. |
| [143: Figure 8.5: wait subroutine](../../bookpages/Page_149.jpg) | Immediate byte format and initialization examples. LRI, INR, BZ0, DCR, RSR with octal machine code and per-instruction cycles; INR explicitly three cycles. PDF page 150. |
| [147: Figure 8.6 part 2](../../bookpages/Page_153.jpg) | Immediate byte format and initialization examples. NOP padding; LRI/INR/BZ0/DCR/RSR delay routine. Printed octal172 is retained; its parenthetical decimal76 conflicts with decimal122 and the p.144 calculation (candidate E009). PDF page 154. |
| [93: Figure 6.9: lamp polling example](../../bookpages/Page_099.jpg) | Worked polling loop using the named instruction. LRI/SRD/LRD/ANI/BZ0 polling sequence; generic OUT/STORE references in surrounding prose are not CMC8 mnemonics. PDF page 100. |
| [94: Lamp polling interpretation](../../bookpages/Page_100.jpg) | Explanation of accumulator effects and immediate masking. Explains immediate data load, port transfer and ANI mask replacing accumulator contents; octal numeric notation. PDF page 101. |
| [154: Figure 8.11: key identification](../../bookpages/Page_160.jpg) | Bit-by-bit command classification. LRI R4, SHR R6 and BB0 R6 distinguish command bits; example octal encodings. PDF page 161. |

## Working findings and assumptions

- **consistency-supported extrapolation; H010 selected in v010; likely:** Use common F0 fetch, phase skip at F1T1, established operand-fetch controls at F2T2–T5, then MOP4+19+22 at T6 and phase reset at T7. PC advances past both bytes before R(A) receives the immediate. When A=N the T6 write replaces PC. No third-cycle memory dereference or flag update. Sources: pp. 67, 68, 53, 70.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

- No complete LRI MOP table located. A full F1 operand-fetch/write cycle without a phase skip is an unselected timing alternative; selected F2 labels follow the existing two-cycle control convention.
- The inherited always-ready MOP29 check at F2T4 is extrapolated, not a documented LRI-specific slot.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21,31 | — | — | — | — | — | — |
| F2 | — | — | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | 4,19,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

13 candidate line matches on proposed printed pages: 67, 68, 93, 94, 125, 126, 131, 143, 147, 148, 150, 154, 214.

[All snippets and scan links](../instruction-mentions.md#lri). These are unreviewed leads and may include other-architecture examples.
