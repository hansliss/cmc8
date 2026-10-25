# NOP

[All instructions](../instruction-set.md)

**Encoding:** `00000000`; **bytes:** 1; **cycles:** 1; **flag column:** blank.

**Book summary (documented summary):** No operation beyond fetch and PC advance.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [51: Common fetch description](../../bookpages/Page_057.jpg) | Single-cycle fetch framework and bit-level flag encoding. Common through T5; one-cycle instructions use T6/T7. IR open during T5. PDF page 58. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Single-cycle fetch framework and bit-level flag encoding. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [147: Figure 8.6 part 2](../../bookpages/Page_153.jpg) | Octal 000 used for padding reserved data positions. NOP padding; LRI/INR/BZ0/DCR/RSR delay routine. Printed octal172 is retained; its parenthetical decimal76 conflicts with decimal122 and the p.144 calculation (candidate E009). PDF page 154. |
| [153: Figure 8.10: keyboard subroutine](../../bookpages/Page_159.jpg) | Keyboard read/compare/copy example; inspect marked numeric discrepancies before execution. CPY R6→R7, XRI R7 with octal 377, zero branches and RSR. Several printed mnemonic/machine-code pairs disagree with figure 5.1. E004/E005 are accepted byte-field corrections: 052→057 at 012 and 340→343 at 014; preserve the printed fields. PDF page 160. |

## Working findings and assumptions

- **consistency-supported extrapolation; working:** Keep BR→AB at F0T6 for consistency with EIN (v006 onward); v005 preserves idle T6 alternative. Sources: pp. 64.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

8 candidate line matches on proposed printed pages: 67, 73, 147.

[All snippets and scan links](../instruction-mentions.md#nop). These are unreviewed leads and may include other-architecture examples.
