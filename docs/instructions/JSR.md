# JSR

[All instructions](../instruction-set.md)

**Encoding:** `00001100`; **bytes:** 2; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Jump to a subroutine using the next register as PC.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [71: Figure 5.4: JSR and RSR](../../bookpages/Page_077.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. JSR increments caller PC again during F1, increments N at F2T2 and writes target to new PC at F2T6. RSR skips phase then decrements N. PDF page 78. |
| [64: Figure 4.19: EIN followed by RSR](../../bookpages/Page_070.jpg) | Interrupt return context; do not infer RSR alone enables INTE. Explicit delayed enable; RSR execute row is labeled F1, unlike the skipped-to-F2 presentation later. PDF page 71. |
| [63: Figure 4.18: interrupt state flow](../../bookpages/Page_069.jpg) | Interrupt return context; do not infer RSR alone enables INTE. N increments on interrupt entry and RSR decrements it; discusses MOP38/39 and INTR. PDF page 70. |
| [105: Figure 6.22: test inputs](../../bookpages/Page_111.jpg) | Software call versus interrupt; application call/return examples. Four direct test lines and BT0/BT1; compares software subroutine, interrupt and test-input polling. PDF page 112. |
| [144: Wait-subroutine timing](../../bookpages/Page_150.jpg) | Software call versus interrupt; application call/return examples. JSR call example; computed timing uses (3+2) cycles for INR+branch. SCW used as halt in this system setup. PDF page 151. |
| [146: Figure 8.6 part 1](../../bookpages/Page_152.jpg) | Software call versus interrupt; application call/return examples. LRM/SRD, BT1, JMP and repeated JSR calls with octal encodings. Complete 75-byte figure8.6 image is transcribed in traffic-program.json and exercised by the board harness. E010 retains the inconsistent T1/T2 prose comment beside actual T1/T3 instructions. PDF page 153. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### JSR, figure 5.4

[71: Figure 5.4: JSR and RSR](../../bookpages/Page_077.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | R(N)→DI | — | PME rises | DI+1→BR | BR→R(N) | DB→BR | PME falls | — |
| F2 | — | — | N+1→N | — | — | — | BR→R(N) | 0→F |

- F0 is common fetch; F1 advances the saved caller PC past the operand byte.
- No PG save/restore or change is shown; no BR→AB at F1T6 is shown.

## Working findings and assumptions

- **derived; working:** Caller PC must advance past both bytes before N increments. PG is not stacked by the shown mechanism. Sources: pp. 71.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

- Global PG is not a per-register stack. Cross-page subroutines need an explicit page convention; do not silently invent PG save/restore.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | — | — |
| F2 | — | — | 16 | — | — | — | 4,18,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

26 candidate line matches on proposed printed pages: 51, 67, 69, 70, 71, 105, 144, 146, 148.

[All snippets and scan links](../instruction-mentions.md#jsr). These are unreviewed leads and may include other-architecture examples.
