# BZ1

[All instructions](../instruction-set.md)

**Encoding:** `111010PP`; **bytes:** 2; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Branch to the address byte on page PP if Z is one.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [72: Figure 5.5: conditional branch circuits](../../bookpages/Page_078.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. MOP51–54 select Z/L/T/DI bit0; MOP55 clocks H at T2. XOR uses IR bit3; inverted H output gates MOP22 at T6. Separate T capture edge and complete branch/page decoding are not drawn. PDF page 79. |
| [73: Figure 5.6: BB0 functional/MOP sequence](../../bookpages/Page_079.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. Operand fetch increments PC; conditional MOP22 at F2T6 selects branch or fall-through. PDF page 80. |
| [153: Figure 8.10: keyboard subroutine](../../bookpages/Page_159.jpg) | Keyboard read/compare/copy example; inspect marked numeric discrepancies before execution. CPY R6→R7, XRI R7 with octal 377, zero branches and RSR. Several printed mnemonic/machine-code pairs disagree with figure 5.1. E004/E005 are accepted byte-field corrections: 052→057 at 012 and 340→343 at 014; preserve the printed fields. PDF page 160. |

## Working findings and assumptions

- **derived from documented circuit; selected in v009:** Store physical H.Q = selected condition XOR IR bit3 at F2T2. H.Q-bar controls MOP22 at F2T6; the functional table’s H=1 taken notation refers to the logical predicate, not physical Q. Restrict the conditional write overlay to branch execute; complete decoding is not drawn. Sources: pp. 72, 73.
- **consistency-supported extrapolation; H008 selected in v009; likely:** Use MOP31 at F1T1; sample condition at F2T2; increment PC through BR at T3/T4 while fetching the operand; capture target at T5; conditionally write PC at T6. This fits the documented two-cycle duration and reuses operand-fetch controls. No dedicated complete MOP table was found. Sources: pp. 67, 72, 73, 70.
- **consistency-supported extrapolation; selected in v009; likely:** Load PP→PG with MOP15 at T6 only when taken, alongside the conditional PC write. Fetch the address using the original page. The PG condition gate is not drawn in figure 5.5. Sources: pp. 67, 72, 70.
- **consistency-supported extrapolation; H022 selected in v018 when execution control enabled:** Add a T4 MEMR checkpoint to the external operand/control-byte read where the sparse selected table omits MOP29. Preserve the active access during complete eight-slot waits and resume original T4 actions once. Do not extend this to CPU loopback, write strobes or SCW’s already-fetched control byte in F2. Sources: pp. 56, 58, 59.

## Open questions

- Exact historical placement and circuitry for the conditional PG update remain unverified.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21,31 | — | — | — | — | — | — |
| F2 | — | — | 18,21,24,51,55 | 18,21,7,10,24,12 | 4,18,22,24 | 2,24 | 4,18 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

The table shows static controls. At **F2T6**, the branch circuit adds MOP22 only when sampled physical H.Q=0 (Q-bar=1). For this page branch it also adds MOP15 only when taken. The actual overlay appears in trace `mops` and `branch_taken`. H samples at F2T2; static MOP22 at F1/F2T4 advances the operand PC regardless of outcome. See [v009 interpretation](../model-v009.md).

## OCR cross-references

2 candidate line matches on proposed printed pages: 67, 70.

[All snippets and scan links](../instruction-mentions.md#bz1). These are unreviewed leads and may include other-architecture examples.
