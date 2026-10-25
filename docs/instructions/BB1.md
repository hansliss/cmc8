# BB1

[All instructions](../instruction-set.md)

**Encoding:** `11011RRR`; **bytes:** 2; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Branch to the address byte if bit 0 of R(A) is one.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [72: Figure 5.5: conditional branch circuits](../../bookpages/Page_078.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. MOP51–54 select Z/L/T/DI bit0; MOP55 clocks H at T2. XOR uses IR bit3; inverted H output gates MOP22 at T6. Separate T capture edge and complete branch/page decoding are not drawn. PDF page 79. |
| [73: Figure 5.6: BB0 functional/MOP sequence](../../bookpages/Page_079.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. Operand fetch increments PC; conditional MOP22 at F2T6 selects branch or fall-through. PDF page 80. |

## Working findings and assumptions

- **derived from documented circuit; selected in v009:** Store physical H.Q = selected condition XOR IR bit3 at F2T2. H.Q-bar controls MOP22 at F2T6; the functional table’s H=1 taken notation refers to the logical predicate, not physical Q. Restrict the conditional write overlay to branch execute; complete decoding is not drawn. Sources: pp. 72, 73.
- **established project correction; E002; selected in v009 and subsequently accepted by project owner:** Use MOP4 instead of the printed F1T4 MOP6, matching the functional BR→R(N) row and p.73 increment explanation. Keep the literal source row unchanged. F2 samples R(A), so A=N observes the PC after both bytes. Held source controls are derived. Sources: pp. 73, 38.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | — | — |
| F2 | 19,21 | 19,21,54 | 19,21,54,55 | — | — | — | 4,18 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

The table shows static controls. At **F2T6**, the branch circuit adds MOP22 only when sampled physical H.Q=0 (Q-bar=1). N and PG remain unchanged. The actual overlay appears in trace `mops` and `branch_taken`. H samples at F2T2; static MOP22 at F1/F2T4 advances the operand PC regardless of outcome. See [v009 interpretation](../model-v009.md).

## OCR cross-references

3 candidate line matches on proposed printed pages: 67, 70, 128.

[All snippets and scan links](../instruction-mentions.md#bb1). These are unreviewed leads and may include other-architecture examples.
