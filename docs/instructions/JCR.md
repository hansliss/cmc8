# JCR

[All instructions](../instruction-set.md)

**Encoding:** `11111RRR`; **bytes:** 1; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Jump to the contents of R(A).

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [40: Register addressing and X](../../bookpages/Page_046.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. PC=R(N), operand register=R(A); MOP20 selects R7/X; subroutines change N. PDF page 47. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [71: Figure 5.4: JSR and RSR](../../bookpages/Page_077.jpg) | Unconditional control semantics; complete JMP MOPs and functional call/return diagrams. JCR has no dedicated numbered table in the inspected sections. JSR increments caller PC again during F1, increments N at F2T2 and writes target to new PC at F2T6. RSR skips phase then decrements N. PDF page 78. |

## Working findings and assumptions

- **consistency-supported extrapolation; selected in v008:** H007: prepare R(A) through DI/DB into BR, skip F1 to F2 at T1, capture BR at F2T5 and write R(N) at T6. N and PG stay unchanged. Direct two-selector transfer is not assumed. Sources: pp. 70, 75.

## Open questions

- No dedicated JCR MOP table located: exact register-to-buffer preparation and write slot must be extrapolated from existing paths.
- Alternative timing: use an earlier buffer capture or perform the register read later; preserve if new evidence distinguishes it from selected H007. No runtime fallback is used.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 19,21 | 19,21,23,31 | — | — | — | — | — | — |
| F2 | — | — | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23,2 | 4,18,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

4 candidate line matches on proposed printed pages: 67, 69, 70.

[All snippets and scan links](../instruction-mentions.md#jcr). These are unreviewed leads and may include other-architecture examples.
