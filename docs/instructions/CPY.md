# CPY

[All instructions](../instruction-set.md)

**Encoding:** `00111RRR`; **bytes:** 1; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Copy R(A) into X.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [153: Figure 8.10: keyboard subroutine](../../bookpages/Page_159.jpg) | Keyboard read/compare/copy example; inspect marked numeric discrepancies before execution. CPY R6→R7, XRI R7 with octal 377, zero branches and RSR. Several printed mnemonic/machine-code pairs disagree with figure 5.1. E004/E005 are accepted byte-field corrections: 052→057 at 012 and 340→343 at 014; preserve the printed fields. PDF page 160. |

## Working findings and assumptions

- **consistency-supported extrapolation; H011 selected in v010; likely:** Reuse the selected JCR buffered source route: R(A)→DI at F1T0, drive DB at T1 with MOP31 phase skip, hold through F2T5 and capture BR, then MOP4+20+22 writes X at T6. No execute memory access. A=N reads the PC after the one-byte fetch; N=7 makes the destination the active PC. Sources: pp. 67, 153, 75, 70.

## Open questions

- No full CPY MOP table located. Figure 8.10 corroborates R(A)→X semantics; its exact two-cycle transfer timing remains to be reconstructed.
- Earlier buffer capture or a full F1 execute cycle remain unselected timing alternatives. Passing tests do not establish the historical CPY capture slot.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 19,21 | 19,21,23,31 | — | — | — | — | — | — |
| F2 | — | — | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23,2 | 4,20,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

2 candidate line matches on proposed printed pages: 67, 153.

[All snippets and scan links](../instruction-mentions.md#cpy). These are unreviewed leads and may include other-architecture examples.
