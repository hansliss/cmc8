# DCR

[All instructions](../instruction-set.md)

**Encoding:** `10100RRR`; **bytes:** 1; **cycles:** 3; **flag column:** Z.

**Book summary (documented summary):** Decrement R(A).

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [76: Figure 5.8: INR/DCR microprograms](../../bookpages/Page_082.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. Increment and complemented increment/decrement; captures and final register writes. Held gates across phases are implicit; the three-cycle model uses both F1 and F2 without a phase skip. PDF page 83. |
| [77: Figure 5.9 and omitted DCR flag circuitry](../../bookpages/Page_083.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. SHR/ROR/RRL semantics; explicitly says DCR zero-detection controls omitted from figure 5.8. PDF page 84. |
| [143: Figure 8.5: wait subroutine](../../bookpages/Page_149.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. LRI, INR, BZ0, DCR, RSR with octal machine code and per-instruction cycles; INR explicitly three cycles. PDF page 150. |
| [147: Figure 8.6 part 2](../../bookpages/Page_153.jpg) | Detailed arithmetic sequences; DCR zero flag needs circuitry omitted from the printed table. NOP padding; LRI/INR/BZ0/DCR/RSR delay routine. Printed octal172 is retained; its parenthetical decimal76 conflicts with decimal122 and the p.144 calculation (candidate E009). PDF page 154. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### DCR, figure 5.8

[76: Figure 5.8: INR/DCR microprograms](../../bookpages/Page_082.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | R(A)→DI | DI→DB | — | — | — | DB→BR | — | — |
| F2 | complement BR→DI | — | — | DI+1→BR | — | — | complement BR→R(A) | 0→F |

- The functional output arrow has an overbar on BR; the numbered row also uses MOP5 at T6.
- Page 77 explicitly states the special zero-flag circuitry/MOPs are omitted.

Literal numbered row (conditional overlays may be described in the notes):

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 19,21 | 23 | — | — | — | 2 | — | — |
| F2 | 5 | — | — | 10,7,12 | — | — | 5,19,22 | 30 |

## Working findings and assumptions

- **documented arithmetic sequence; derived held controls; selected in v011:** Capture R(A) through CPU-driven DB into BR at F1T5. At F2T3 capture (~BR+1)&255 using MOP5+7+10+12, then use MOP5+19+22 at T6 to write its complement, yielding (original-1)&255. Sources: pp. 76, 38.
- **hypothesis constrained by documented flag semantics; H014 selected in v011; provisional circuit and timing:** Represent omitted DCR flag circuitry by adding functional MOP32 at F2T6 with named research control zero_source="di", testing the final complemented result at writeback. This is not a recovered physical MOP assignment. An all-ones test on the intermediate ALU result at T3 is an unselected equivalent final-semantics alternative with different timing. Sources: pp. 77, 76, 38.
- **cross-instruction consistency finding; v012 reassessment; H014 unchanged, timing still provisional:** ANI polling and XRI keyboard examples corroborate Z from the logical result. Across all 256 bytes, DCR result/Z agree with XRI #FF; INR; XRI #FF reconstruction. This checks final semantics only: T3 intermediate all-ones and T6 final-DI zero predicates are equivalent and cannot distinguish hardware/timing. Retain H014 without promoting its detector location to documented fact. Sources: pp. 95, 153, 77, 75.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

- Page 77 explicitly says Z-update circuitry/MOPs were omitted. A mechanically literal figure 5.8 replay is incomplete.
- Exact omitted DCR zero-detector circuitry and capture slot remain unknown. v011 selects DI at T6; an intermediate all-ones test at T3 remains an alternative.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 19,21 | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23 | 19,21,23,2 | — | — |
| F2 | 5 | 5 | 5 | 5,10,7,12 | — | — | 5,19,22,32 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

**Additional research control at F2T6:** `zero_source="di"` selects the value tested by the modeled MOP32. This represents the omitted DCR flag circuitry; neither this source selection nor the added MOP32 slot is a literal printed control. Trace evaluations record `zero_source` and `zero_value`. See [v011 interpretation](../model-v011.md).

## OCR cross-references

8 candidate line matches on proposed printed pages: 67, 76, 143, 147, 148.

[All snippets and scan links](../instruction-mentions.md#dcr). These are unreviewed leads and may include other-architecture examples.
