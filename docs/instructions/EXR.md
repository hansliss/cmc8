# EXR

[All instructions](../instruction-set.md)

**Encoding:** `10111RRR`; **bytes:** 1; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Exchange R(A) and X.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [39: Figure 4.1: processor principle diagram](../../bookpages/Page_045.jpg) | One selected register port and one DI bus in the simplified schematic; no ALU input holding latch is explicitly drawn. Register selectors, buses, ALU, latch paths and interrupt controls; explicitly simplified. PDF page 46. |
| [75: Figure 5.7: AND microprogram](../../bookpages/Page_081.jpg) | X→DI→DB→BR preparation provides the first saved operand; does not describe exchange or a holding latch. R(A) and X operands, X→DI/DB→BR preparation, Z from ALU result. Numbered row sparse; held levels need reconstruction. PDF page 82. |

## Working findings and assumptions

- **architecture hypothesis; H019 selected in v014 and accepted by project owner as working model; historical latch remains unverified:** Add an explicitly controlled 8-bit ALU input-A holding latch. Save X in BR during F1. Capture R(A) into held A at F2T0; BR→R(A) at T4; held A→ALU→BR at T5; BR→X at T6. No register-port conflict or self-alias special case. The latch and exact controls/slots are not documented for EXR. Sources: pp. 67, 39, 75.
- **restricted-model consistency finding; executable investigation, not proof about original hardware:** Pure transfers through R(A)↔BR and X↔BR cannot swap two distinct register values without another path/holding detail. Three-XOR swap has a self-alias counterexample. These observations motivate exploring an omitted holding path but do not prove the selected latch or exclude every possible ALU algorithm. Sources: pp. 39, 67.
- **project decision; accepted working architecture hypothesis:** Project owner accepts H019 as the working EXR architecture because it provides a coherent solution to a missing detail in the simplified book model and no better-supported alternative has been identified. Acceptance does not establish the latch as original CMC8 hardware; retain its explicit provenance and revisit if evidence favors another path.

## Open questions

- No additional EXR description or dedicated MOP sequence was located in the searched OCR. OCR absence is not proof of book absence.
- Does the real ALU hold an input, or does exchange use another omitted register/bus path? H019 is a provisional architecture extension, not established from figure 4.1.
- Operand preservation and three cycles are tested, but EXR capture/write timing remains unknown.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 20,21 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23 | 20,21,23,2 | — | — |
| F2 | 19,21,7 | — | — | — | 4,19,22 | 12 | 4,20,22 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

**Architecture hypothesis H019:** this candidate needs an undocumented ALU input holding latch. Static MOPs alone do not reproduce it. The named research controls are:

| Slot | Additional control |
| --- | --- |
| F2T0 | `alu_a_mode="capture"` |
| F2T5 | `alu_a_mode="held"` |

Trace state `alu_a` and evaluation fields `alu_a_mode` / `alu_a_value` expose this assumption. See [v014](../model-v014.md); successful simulation does not establish the latch.

## OCR cross-references

1 candidate line matches on proposed printed pages: 67.

[All snippets and scan links](../instruction-mentions.md#exr). These are unreviewed leads and may include other-architecture examples.
