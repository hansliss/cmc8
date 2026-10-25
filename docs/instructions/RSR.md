# RSR

[All instructions](../instruction-set.md)

**Encoding:** `00001111`; **bytes:** 1; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Return by selecting the previous PC register.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [71: Figure 5.4: JSR and RSR](../../bookpages/Page_077.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. JSR increments caller PC again during F1, increments N at F2T2 and writes target to new PC at F2T6. RSR skips phase then decrements N. PDF page 78. |
| [64: Figure 4.19: EIN followed by RSR](../../bookpages/Page_070.jpg) | Interrupt return context; do not infer RSR alone enables INTE. Explicit delayed enable; RSR execute row is labeled F1, unlike the skipped-to-F2 presentation later. PDF page 71. |
| [63: Figure 4.18: interrupt state flow](../../bookpages/Page_069.jpg) | Interrupt return context; do not infer RSR alone enables INTE. N increments on interrupt entry and RSR decrements it; discusses MOP38/39 and INTR. PDF page 70. |
| [143: Figure 8.5: wait subroutine](../../bookpages/Page_149.jpg) | Return from actual wait subroutine; validates that the caller must resume after both JSR bytes. LRI, INR, BZ0, DCR, RSR with octal machine code and per-instruction cycles; INR explicitly three cycles. PDF page 150. |
| [147: Figure 8.6 part 2](../../bookpages/Page_153.jpg) | Return from actual wait subroutine; validates that the caller must resume after both JSR bytes. NOP padding; LRI/INR/BZ0/DCR/RSR delay routine. Printed octal172 is retained; its parenthetical decimal76 conflicts with decimal122 and the p.144 calculation (candidate E009). PDF page 154. |
| [153: Figure 8.10: keyboard subroutine](../../bookpages/Page_159.jpg) | Keyboard read/compare/copy example; inspect marked numeric discrepancies before execution. CPY R6→R7, XRI R7 with octal 377, zero branches and RSR. Several printed mnemonic/machine-code pairs disagree with figure 5.1. E004/E005 are accepted byte-field corrections: 052→057 at 012 and 340→343 at 014; preserve the printed fields. PDF page 160. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### EIN followed by RSR, figure 4.19

[64: Figure 4.19: EIN followed by RSR](../../bookpages/Page_070.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EIN F0 | R(N)→DI | DI→AB | PME rises | DI+1→BR | BR→R(N) | DB→IR | BR→AB; PME falls | 0→F |
| following RSR F0 | R(N)→DI | DI→AB | 1→INTE; PME rises | DI+1→BR | BR→R(N) | DB→IR | BR→AB; PME falls | — |
| following RSR F1 | — | — | N-1→N | — | — | — | — | 0→F |

- The INTE update is caused by preceding EIN, not evidence that RSR alone enables interrupts.
- The execute row is labeled F1 here; later figure 5.4 explicitly changes F1 to F2 at T1.

### RSR, figure 5.4

[71: Figure 5.4: JSR and RSR](../../bookpages/Page_077.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | — | 2→F | — | — | — | — | — | — |
| F2 | — | — | N-1→N | — | — | — | — | 0→F |

- Two cycles via phase switch at F1T1; no operand byte or unconditional INTE write is shown.

### Interrupt-entry cycle, figure4.20b (not an opcode)

[65: Figures 4.20/4.21](../../bookpages/Page_071.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 1→INTA; 0→INTE; 0→INTR | 02→DI | N+1→N | — | DI→R(N) | — | — | 0→F |

- Interrupt entry takes one eight-slot cycle and does not fetch a replacement opcode.
- INTA is clocked from pending INTR at F0T0; accepted entry clears INTE and INTR after sampling.
- No PG write or flag stack is shown. Complete held controls in v016 are derived from the functional row.

## Working findings and assumptions

- **documented; working:** Decrement N to resume the previous PC; no standalone INTE enable is shown by figure 5.4. Sources: pp. 71, 64.
- **interrupt integration of documented circuit and sequence; selected in v016; sampled endpoint realization:** With explicit InterruptInput, enabled active-low INT asynchronously sets INTR; MOP28 samples pending INTR at F0T0. An accepted request selects the eight-slot figure4.20 entry cycle: clear INTE/INTR at T0, increment N T2, write002 to new PC T4. Return PC is the previous instruction’s completed PC; PG and L/Z are unchanged by entry. Sources: pp. 62, 63, 65.
- **consistency-supported integration; tested in v016:** RSR restores N and the saved PC after interrupt entry without automatically enabling INTE or restoring PG/L/Z. Handler EIN supplies the reenable effect during RSR fetch; held requests cannot be accepted until the following F0T0. Sources: pp. 63, 64, 65.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

- Global PG is not a per-register stack. Cross-page subroutines need an explicit page convention; do not silently invent PG save/restore.
- Figure 4.19 labels the execute cycle F1; figure 5.4/p.71 explicitly switch to F2. Use the explicit phase-skip account while preserving the discrepancy.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | — | 31 | — | — | — | — | — | — |
| F2 | — | — | 17 | — | — | — | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

[v016 interrupt integration](../model-v016.md) tests this instruction with request latching and F0T0 acceptance. The separate entry cycle has no opcode and is not included in this instruction’s own cycle count. Retained-IR/interrupt decoder edge cases remain explicit.

## OCR cross-references

16 candidate line matches on proposed printed pages: 62, 63, 64, 67, 70, 71, 143, 147, 153.

[All snippets and scan links](../instruction-mentions.md#rsr). These are unreviewed leads and may include other-architecture examples.
