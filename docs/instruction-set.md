# CMC8 instruction reference

Generated from [the authored catalogue](../specification/instructions.json). Baseline: [figure 5.1, printed p.67](../bookpages/Page_073.jpg).

[Working book errata](errata.md) collects established corrections and candidate discrepancies without altering the source transcriptions.

All **43 mnemonic families / 239 encoded variants** are catalogued. Zeros are normalized to `0`; spacing is normalized. The printed image remains the authority. Cycle counts exclude optional memory waits; SCW explicitly adds acknowledgement waits.

The transcription reproduces the book’s distribution: seven one-cycle, fourteen two-cycle and twenty-two three-cycle families. A visually checked source is evidence for its stated observation, not certification of every line on that page.

MOP tables below reflect **v018**, not a claim of original silicon truth. Documented summaries, working extrapolations and unresolved questions are separate in each entry. The inherited flag timing and indexed route retain their provisional status.

[Searchable OCR mentions](instruction-mentions.md) cover all 226 PDF pages. Search results may miss damaged OCR or include other architectures; they are leads, not facts. Printed-page coordinates use PDF p+7 (1-based) / image Page_(p+6).jpg, checked at multiple anchors.

**EXR is especially provisional:** its executable candidate adds an undocumented ALU input holding latch. This is an architecture hypothesis, not merely inferred slot timing. See [v014](model-v014.md).

[Interrupt integration](model-v016.md) adds a separate eight-slot entry cycle and asynchronous INTR observations when explicitly enabled. This is not another opcode family and does not change the 43-family count.

[Reset integration](model-v017.md) implements the figure-4.21 reset cycle selected by active-low RESET at T7. It is separate from the opcode repertoire; reset does not silently initialize unlisted flags or registers.

[Shared execution control](model-v018.md) integrates MEMR, HALT and single-step with eight-subdivision wait continuations. Read-check coverage and the omitted SSE circuitry retain explicit H022/H023 interpretations.

| Instruction | Encoding | Bytes | Cycles | Flags | Implemented | Key sources |
| --- | --- | --- | --- | --- | --- | --- |
| [LRM](instructions/LRM.md) | `01000RRR` | 2 | 3 | — | v018 | 38, 39, 40, 43, 126 |
| [LRS](instructions/LRS.md) | `01010RRR` | 2 | 3 | — | v018 | 30, 31, 38, 39, 40, 43, 49, 50, 51, 52, 53, 54, 126 |
| [LRX](instructions/LRX.md) | `01001RRR` | 1 | 3 | — | v018 | 38, 39, 40, 43, 68, 75, 155 |
| [LSX](instructions/LSX.md) | `01011RRR` | 1 | 3 | — | v018 | 38, 39, 40, 43, 68, 75, 151 |
| [LRD](instructions/LRD.md) | `00010RRR` | 2 | 3 | — | v018 | 38, 39, 40, 43, 93, 94, 95, 96, 113, 126, 153, 154, 155 |
| [SRM](instructions/SRM.md) | `01100RRR` | 2 | 3 | — | v018 | 38, 39, 40, 43, 126 |
| [SRS](instructions/SRS.md) | `01110RRR` | 2 | 3 | — | v018 | 38, 39, 40, 43, 52, 54, 55, 126 |
| [SRX](instructions/SRX.md) | `01101RRR` | 1 | 3 | — | v018 | 38, 39, 40, 43, 68, 75 |
| [SSX](instructions/SSX.md) | `01111RRR` | 1 | 3 | — | v018 | 38, 39, 40, 43, 68, 75 |
| [SRD](instructions/SRD.md) | `00011RRR` | 2 | 3 | — | v018 | 38, 39, 40, 43, 93, 94, 95, 96, 113, 126, 155 |
| [BB0](instructions/BB0.md) | `11010RRR` | 2 | 3 | — | v018 | 70, 72, 73, 154 |
| [BB1](instructions/BB1.md) | `11011RRR` | 2 | 3 | — | v018 | 70, 72, 73 |
| [BL0](instructions/BL0.md) | `111001PP` | 2 | 2 | — | v018 | 70, 72, 73 |
| [BL1](instructions/BL1.md) | `111011PP` | 2 | 2 | — | v018 | 70, 72, 73 |
| [BZ0](instructions/BZ0.md) | `111000PP` | 2 | 2 | — | v018 | 70, 72, 73, 93, 94, 153 |
| [BZ1](instructions/BZ1.md) | `111010PP` | 2 | 2 | — | v018 | 70, 72, 73, 153 |
| [BT0](instructions/BT0.md) | `110000TT` | 2 | 2 | — | v018 | 68, 70, 72, 73, 105, 106 |
| [BT1](instructions/BT1.md) | `110010TT` | 2 | 2 | — | v018 | 68, 70, 72, 73, 105, 106 |
| [JMP](instructions/JMP.md) | `111100PP` | 2 | 2 | — | v018 | 31, 40, 70, 71, 89, 90, 91, 146, 147, 155 |
| [JCR](instructions/JCR.md) | `11111RRR` | 1 | 2 | — | v018 | 40, 70, 71 |
| [LRI](instructions/LRI.md) | `00100RRR` | 2 | 2 | — | v018 | 68, 93, 94, 126, 143, 147, 154 |
| [XRI](instructions/XRI.md) | `00101RRR` | 2 | 3 | Z | v018 | 68, 75, 153 |
| [ANI](instructions/ANI.md) | `00110RRR` | 2 | 3 | Z | v018 | 68, 75, 93, 94, 95 |
| [CPY](instructions/CPY.md) | `00111RRR` | 1 | 2 | — | v018 | 153 |
| [INR](instructions/INR.md) | `10000RRR` | 1 | 3 | Z | v018 | 75, 76, 77, 143, 144, 147, 155 |
| [ROR](instructions/ROR.md) | `10001RRR` | 1 | 2 | — | v018 | 77, 78, 79 |
| [SHR](instructions/SHR.md) | `10010RRR` | 1 | 2 | — | v018 | 77, 78, 79, 154 |
| [RRL](instructions/RRL.md) | `10011RRR` | 1 | 2 | L | v018 | 77, 78, 79, 107 |
| [DCR](instructions/DCR.md) | `10100RRR` | 1 | 3 | Z | v018 | 76, 77, 143, 147 |
| [XOR](instructions/XOR.md) | `10101RRR` | 1 | 3 | Z | v018 | 75 |
| [AND](instructions/AND.md) | `10110RRR` | 1 | 3 | Z | v018 | 75 |
| [EXR](instructions/EXR.md) | `10111RRR` | 1 | 3 | — | v018 | 39, 75 |
| [SCW](instructions/SCW.md) | `00001000` | 2 | 3+ waits | — | v018 | 56, 97, 98, 99, 100, 101, 144 |
| [SCS](instructions/SCS.md) | `00001001` | 2 | 3 | — | v018 | 97, 98, 99, 100, 101 |
| [JSR](instructions/JSR.md) | `00001100` | 2 | 3 | — | v018 | 40, 63, 64, 70, 71, 105, 144, 146 |
| [RSR](instructions/RSR.md) | `00001111` | 1 | 2 | — | v018 | 40, 63, 64, 70, 71, 143, 147, 153 |
| [NOP](instructions/NOP.md) | `00000000` | 1 | 1 | — | v018 | 51, 68, 147, 153 |
| [EIN](instructions/EIN.md) | `00000011` | 1 | 1 | INTE | v018 | 51, 62, 63, 64, 65, 68 |
| [DIN](instructions/DIN.md) | `00000010` | 1 | 1 | INTE | v018 | 51, 62, 63, 64, 65, 68 |
| [SEL](instructions/SEL.md) | `00000101` | 1 | 1 | L | v018 | 51, 68 |
| [REL](instructions/REL.md) | `00000100` | 1 | 1 | L | v018 | 51, 68 |
| [SEZ](instructions/SEZ.md) | `00000111` | 1 | 1 | Z | v018 | 51, 68 |
| [REZ](instructions/REZ.md) | `00000110` | 1 | 1 | Z | v018 | 51, 68 |

## Maintaining this reference

Edit `specification/instructions.json` for the catalogue and `specification/book-microprograms.json` for source sequence transcriptions, then run `python3 -m tools.build_instruction_reference`. `--check` verifies generated files are current. To re-extract OCR, run `python3 -m tools.index_book` (requires the installed `pdftotext` executable). The simulator and reference renderer otherwise use only Python’s standard library.

Machine-readable OCR leads are in `specification/instruction-mentions.json`; the page-separated OCR cache is `specification/ocr-pages.json`. Source comments and findings are authored; search hits and displayed MOP tables are generated.
