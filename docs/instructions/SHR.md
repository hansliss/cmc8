# SHR

[All instructions](../instruction-set.md)

**Encoding:** `10010RRR`; **bytes:** 1; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Shift R(A) one step right, inserting zero at bit 7.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [77: Figure 5.9 and omitted DCR flag circuitry](../../bookpages/Page_083.jpg) | Right-shift/rotation semantics and dedicated mux/link circuits. Only RRL has a full illustrated functional example here. SHR/ROR/RRL semantics; explicitly says DCR zero-detection controls omitted from figure 5.8. PDF page 84. |
| [78: Figure 5.10: shift multiplexer](../../bookpages/Page_084.jpg) | Right-shift/rotation semantics and dedicated mux/link circuits. Only RRL has a full illustrated functional example here. MOP11 shifts ALU→BR. ROR wraps bit0; SHR grounds bit7; RRL uses a master/slave Link. Explicitly says figure-5.11 gates are only a principle and physical controls are partly coded. PDF page 85. |
| [79: Figures 5.11/5.12: RRL circuits and microprogram](../../bookpages/Page_085.jpg) | Right-shift/rotation semantics and dedicated mux/link circuits. Only RRL has a full illustrated functional example here. Link path and shift timing. Printed 30 at F1T1 conflicts with functional 2→F; figure 5.11 uses 57 for zero insertion. PDF page 86. |
| [154: Figure 8.11: key identification](../../bookpages/Page_160.jpg) | Bit-by-bit command classification. LRI R4, SHR R6 and BB0 R6 distinguish command bits; example octal encodings. PDF page 161. |

## Working findings and assumptions

- **derived datapath realization from documented sequence; H017 selected in v013:** Figure 5.12 uses MOP7 without B enable or arithmetic operation: model DI passthrough through ALU. MOP11 shifts; MOP13 wraps ALU bit0, MOP43/57 insert zero, MOP33 uses old Link for bit7 while sampling ALU bit0 into new Link. These are functional control abstractions, not recovered physical wire coding. Sources: pp. 79, 78, 38, 77.
- **consistency-supported extrapolation; H018 selected in v013; likely:** Reuse RRL timing and replace its MOP33 with MOP13 for ROR or MOP43 for SHR. This gives the documented rotation/zero-fill semantics without updating Link or Z. No dedicated complete ROR/SHR MOP table was located. Sources: pp. 67, 77, 78, 79, 38.

## Open questions

- Figure 5.11 labels zero insertion 57 while figure 4.2 uses 43. v013 models their stated function as equivalent, without asserting the physical encodings are identical; selected SHR tables use 43.
- Exact ROR/SHR control timing remains inferred by consistency with the RRL table.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 19,21 | 19,21,23,31 | — | — | — | — | — | — |
| F2 | — | — | 19,21,7,11,12,43 | — | — | 4 | 19,22,4 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

## OCR cross-references

6 candidate line matches on proposed printed pages: 67, 77, 78, 79, 154.

[All snippets and scan links](../instruction-mentions.md#shr). These are unreviewed leads and may include other-architecture examples.
