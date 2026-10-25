# ANI

[All instructions](../instruction-set.md)

**Encoding:** `00110RRR`; **bytes:** 2; **cycles:** 3; **flag column:** Z.

**Book summary (documented operation; destination corroborated by accumulator-mask example):** AND immediate; result to R(A).

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Immediate operand format; listed flag effect Z. Exact destination is read with register/immediate family convention. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [93: Figure 6.9: lamp polling example](../../bookpages/Page_099.jpg) | Worked polling loop using the named instruction. LRI/SRD/LRD/ANI/BZ0 polling sequence; generic OUT/STORE references in surrounding prose are not CMC8 mnemonics. PDF page 100. |
| [94: Lamp polling interpretation](../../bookpages/Page_100.jpg) | Explanation of accumulator effects and immediate masking. Explains immediate data load, port transfer and ANI mask replacing accumulator contents; octal numeric notation. PDF page 101. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | AND supplies the ALU/Z T3 and register-result T4 precedent used by the selected immediate logical schedule. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |
| [95: Lamp polling: ANI result and Z](../../bookpages/Page_101.jpg) | Explicit result-based Z behavior and polling-loop exit condition; does not establish a T3 or T6 detector edge. Opening paragraph explicitly says ANI gives Z=0 for a nonzero masked accumulator result, causing BZ0 to repeat; low input bit3 lets execution continue. No internal capture slot is given. PDF page 102. |

## Working findings and assumptions

- **consistency-supported extrapolation; H016 selected in v012; likely:** Fetch the immediate into BR during full F1 using the established PC increment and program-read controls, without target→AB preload. F2 follows AND: R(A) on DI, ALU operation and MOP32 at T3, result→R(A) at T4, phase reset at T7. The detailed timing and held controls are inferred; no dedicated XRI/ANI MOP table located. Sources: pp. 67, 68, 75, 53.
- **documented result semantics; visually rechecked in v012 investigation:** Pages 94–95 mask to octal 010; a nonzero masked result clears Z and repeats the BZ0 loop, while zero lets execution continue. A nonzero source byte can therefore produce Z=1 after masking. Sources: pp. 94, 95.

## Open questions

- Exact immediate logical capture/write slots remain inferred from the AND and operand-fetch precedents.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 2,24 | — | — |
| F2 | 19,21 | 19,21 | 19,21 | 19,21,3,7,9,32,12 | 4,22,19 | — | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

4 candidate line matches on proposed printed pages: 67, 93, 94, 95.

[All snippets and scan links](../instruction-mentions.md#ani). These are unreviewed leads and may include other-architecture examples.
