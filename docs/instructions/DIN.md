# DIN

[All instructions](../instruction-set.md)

**Encoding:** `00000010`; **bytes:** 1; **cycles:** 1; **flag column:** INTE.

**Book summary (documented summary):** Disable interrupts.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [51: Common fetch description](../../bookpages/Page_057.jpg) | Single-cycle fetch framework and bit-level flag encoding. Common through T5; one-cycle instructions use T6/T7. IR open during T5. PDF page 58. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | Single-cycle fetch framework and bit-level flag encoding. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [62: Interrupt enable delay](../../bookpages/Page_068.jpg) | EIN delayed enable is explicit; matching DIN timing is extrapolation. EIN sets INTE at next instruction F0T2; request gating and interrupt entry overview. PDF page 69. |
| [63: Figure 4.18: interrupt state flow](../../bookpages/Page_069.jpg) | EIN delayed enable is explicit; matching DIN timing is extrapolation. N increments on interrupt entry and RSR decrements it; discusses MOP38/39 and INTR. PDF page 70. |
| [64: Figure 4.19: EIN followed by RSR](../../bookpages/Page_070.jpg) | EIN delayed enable is explicit; matching DIN timing is extrapolation. Explicit delayed enable; RSR execute row is labeled F1, unlike the skipped-to-F2 presentation later. PDF page 71. |
| [65: Figures 4.20/4.21](../../bookpages/Page_071.jpg) | EIN delayed enable is explicit; matching DIN timing is extrapolation. INTR→INTA clocked F0T0, then the entry table clears INTE/INTR, increments N and writes constant002 into the new PC. No PG change is shown. Adjacent reset table is distinct; not evidence RSR alone re-enables INTE. PDF page 72. |

## Book microprograms (source transcription)

These are functional/sparse printed tables, **not executable held-level controls**. An empty cell is an empty printed cell, not proof every gate is released.

### Interrupt-entry cycle, figure4.20b (not an opcode)

[65: Figures 4.20/4.21](../../bookpages/Page_071.jpg)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 1→INTA; 0→INTE; 0→INTR | 02→DI | N+1→N | — | DI→R(N) | — | — | 0→F |

- Interrupt entry takes one eight-slot cycle and does not fetch a replacement opcode.
- INTA is clocked from pending INTR at F0T0; accepted entry clears INTE and INTR after sampling.
- No PG write or flag stack is shown. Complete held controls in v016 are derived from the functional row.

## Working findings and assumptions

- **consistency-supported extrapolation; working:** Likely next-fetch F0T2 flag update, matching EIN; preserve earlier own-T6/T7 update as an unselected alternative. Sources: pp. 68, 64.
- **interrupt integration of documented circuit and sequence; selected in v016; sampled endpoint realization:** With explicit InterruptInput, enabled active-low INT asynchronously sets INTR; MOP28 samples pending INTR at F0T0. An accepted request selects the eight-slot figure4.20 entry cycle: clear INTE/INTR at T0, increment N T2, write002 to new PC T4. Return PC is the previous instruction’s completed PC; PG and L/Z are unchanged by entry. Sources: pp. 62, 63, 65.
- **derived from the detailed latch circuit; selected in v016; circuit preferred over simplified flowchart:** DIN clears INTE but not a request already latched in INTR. The detailed circuit clocks INTR directly into INTA, so that pending request can still be accepted after masking. Near-edge races are outside the model. Sources: pp. 63, 65.

## Open questions

No instruction-specific question recorded; absence of a question is not completeness of evidence.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

The instruction’s own flag change occurs at **F0T2 of the next fetch**, selected by retained IR. Returning from `run_instruction()` does not force that deferred effect early. See [flag timing](../flag-instruction-timing.md).

[v016 interrupt integration](../model-v016.md) tests this instruction with request latching and F0T0 acceptance. The separate entry cycle has no opcode and is not included in this instruction’s own cycle count. Retained-IR/interrupt decoder edge cases remain explicit.

## OCR cross-references

3 candidate line matches on proposed printed pages: 62, 67, 114.

[All snippets and scan links](../instruction-mentions.md#din). These are unreviewed leads and may include other-architecture examples.
