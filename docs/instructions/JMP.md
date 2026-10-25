# JMP

[All instructions](../instruction-set.md)

**Encoding:** `111100PP`; **bytes:** 2; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Jump to the address byte on page PP.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [71: Figure 5.4: JSR and RSR](../../bookpages/Page_077.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. JSR increments caller PC again during F1, increments N at F2T2 and writes target to new PC at F2T6. RSR skips phase then decrements N. PDF page 78. |
| [31: LRS format and three phases](../../bookpages/Page_037.jpg) | Two-cycle classification and program examples using octal 360. Fetch, operand-address fetch, final read; PC advances for both bytes. Also identifies REL as one cycle and JMP as two. PDF page 38. |
| [146: Figure 8.6 part 1](../../bookpages/Page_152.jpg) | Two-cycle classification and program examples using octal 360. LRM/SRD, BT1, JMP and repeated JSR calls with octal encodings. Complete 75-byte figure8.6 image is transcribed in traffic-program.json and exercised by the board harness. E010 retains the inconsistent T1/T2 prose comment beside actual T1/T3 instructions. PDF page 153. |
| [147: Figure 8.6 part 2](../../bookpages/Page_153.jpg) | Two-cycle classification and program examples using octal 360. NOP padding; LRI/INR/BZ0/DCR/RSR delay routine. Printed octal172 is retained; its parenthetical decimal76 conflicts with decimal122 and the p.144 calculation (candidate E009). PDF page 154. |
| [155: Figure 8.12: increment-address command](../../bookpages/Page_161.jpg) | Indexed read and branch-back in a concrete application sequence. LRD R7, INR R7, SRD R7, LRX R5, SRD R5, JMP page3; SRD R7 machine-code field prints 032 instead of expected 037. Accepted project correction E006: R7 is intended by the read/increment/write sequence. PDF page 162. |
| [90: Figure 6.7: JMP bus timing](../../bookpages/Page_096.jpg) | Target is written to PC at the beginning of F2T6; AB receives it at T1 of the following fetch. Confirms operand address remains in AB across the jump completion. Target is written to PC at the beginning of F2T6; AB receives it at T1 of the following fetch. Confirms operand address remains in AB across the jump completion. PDF page 97. |
| [89: JMP combined execute cycle discussion](../../bookpages/Page_095.jpg) | Explains the F1–2 execute cycle used in the following JMP timing diagram. Explains the F1–2 execute cycle used in the following JMP timing diagram. PDF page 96. |
| [91: Figure 6.8: single-step JMP](../../bookpages/Page_097.jpg) | Single-step/wait circuit context; not evidence that the always-ready simulator implements single stepping. Shows memory/address retention through single-step waits and the T4 WAIT-output mask. Implemented in v018 with explicit H023 SSE timing/interaction assumptions; the omitted complete SSE circuit is not claimed recovered. PDF page 98. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### JMP, figure 5.3

[70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | — | 2→F | — | — | — | — | — | — |
| F2 | — | — | PME rises | — | — | DB→BR | BR→R(N); PP→PG; PME falls | 0→F |

- F0 is the common fetch (figure 4.10).
- At F1T1, phase changes to F2 while the timing counter continues; the next slot is F2T2.

Literal numbered row (conditional overlays may be described in the notes):

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | — | 31 | — | — | — | — | — | — |
| F2 | — | — | 24 | 24 | 24 | 2,24 | 4,18,15,22 | 30 |

## Working findings and assumptions

- **documented; working:** F1T1 switches to F2; next executed slot is F2T2, not F2T0. This explains the two-cycle duration. Sources: pp. 70, 71.
- **consistency-supported extrapolation; H022 selected in v018 when execution control enabled:** Add a T4 MEMR checkpoint to the external operand/control-byte read where the sparse selected table omits MOP29. Preserve the active access during complete eight-slot waits and resume original T4 actions once. Do not extend this to CPU loopback, write strobes or SCW’s already-fetched control byte in F2. Sources: pp. 56, 58, 59.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | — | 31 | — | — | — | — | — | — |
| F2 | — | — | 24 | 24 | 24 | 2,24 | 4,18,15,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

39 candidate line matches on proposed printed pages: 31, 42, 67, 69, 70, 71, 89, 90, 91, 119, 121, 124, 125, 126, 127, 128, 129, 135, 145, 146, 147, 148, 150, 152, 155.

[All snippets and scan links](../instruction-mentions.md#jmp). These are unreviewed leads and may include other-architecture examples.
