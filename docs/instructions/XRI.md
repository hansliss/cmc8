# XRI

[All instructions](../instruction-set.md)

**Encoding:** `00101RRR`; **bytes:** 2; **cycles:** 3; **flag column:** Z.

**Book summary (documented operation; destination corroborated by keyboard example):** Exclusive-OR immediate; result to R(A).

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Immediate operand format; listed flag effect Z. Exact destination is read with register/immediate family convention. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [153: Figure 8.10: keyboard subroutine](../../bookpages/Page_159.jpg) | Keyboard read/compare/copy example; inspect marked numeric discrepancies before execution. CPY R6→R7, XRI R7 with octal 377, zero branches and RSR. Several printed mnemonic/machine-code pairs disagree with figure 5.1. E004/E005 are accepted byte-field corrections: 052→057 at 012 and 340→343 at 014; preserve the printed fields. PDF page 160. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | AND supplies the ALU/Z T3 and register-result T4 precedent used by the selected immediate logical schedule. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |

## Working findings and assumptions

- **consistency-supported extrapolation; H016 selected in v012; likely:** Fetch the immediate into BR during full F1 using the established PC increment and program-read controls, without target→AB preload. F2 follows AND: R(A) on DI, ALU operation and MOP32 at T3, result→R(A) at T4, phase reset at T7. The detailed timing and held controls are inferred; no dedicated XRI/ANI MOP table located. Sources: pp. 67, 68, 75, 53.
- **derived from documented application; visually rechecked in v012 investigation:** Figure 8.10 uses XRI R7,#377 octal followed by zero branches; FF transforms to zero, while other key codes give nonzero. This corroborates destination R7 and Z based on the transformed result, not the original byte. Accepted byte corrections E004/E005 preserve the literal listing mismatches. Sources: pp. 153.
- **established project correction; E004; accepted by project owner:** Figure 8.10 at octal 012 intends XRI R7,#377: the keyboard value is loaded into R7/X and inverted for the Z test. Printed opcode 052 selects R2; correct to 057, also printed correctly at 003. Preserve the literal field. Sources: pp. 153, 67.

## Open questions

- Exact immediate logical capture/write slots remain inferred from the AND and operand-fetch precedents.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | — | — |
| F2 | 19,21 | 19,21 | 19,21 | 19,21,3,7,8,32,12 | 4,22,19 | — | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

1 candidate line matches on proposed printed pages: 67.

[All snippets and scan links](../instruction-mentions.md#xri). These are unreviewed leads and may include other-architecture examples.
