# REZ

[All instructions](../instruction-set.md)

**Encoding:** `00000110`; **bytes:** 1; **cycles:** 1; **flag column:** Z.

**Book summary (documented summary):** Clear Z.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [51: Common fetch description](../../bookpages/Page_057.jpg) | Single-cycle fetch framework and bit-level flag encoding. Common through T5; one-cycle instructions use T6/T7. IR open during T5. PDF page 58. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Single-cycle fetch framework and bit-level flag encoding. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |

## Working findings and assumptions

- **consistency-supported extrapolation; working:** Likely next-fetch F0T2 flag update, matching EIN; preserve earlier own-T6/T7 update as an unselected alternative. Sources: pp. 68, 64.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

The instruction’s own flag change occurs at **F0T2 of the next fetch**, selected by retained IR. Returning from `run_instruction()` does not force that deferred effect early. See [flag timing](../flag-instruction-timing.md).

## OCR cross-references

2 candidate line matches on proposed printed pages: 67, 75.

[All snippets and scan links](../instruction-mentions.md#rez). These are unreviewed leads and may include other-architecture examples.
