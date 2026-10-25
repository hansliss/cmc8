# BT1

[All instructions](../instruction-set.md)

**Encoding:** `110010TT`; **bytes:** 2; **cycles:** 2; **flag column:** blank.

**Book summary (documented summary):** Branch to the address byte if test input TT is one.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [70: Figure 5.3: JMP MOP table](../../bookpages/Page_076.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. F1T1 MOP31 changes phase to F2 without restarting T; F2T5 reads target; F2T6 writes PC and PG. Prose also specifies JCR register target. PDF page 77. |
| [72: Figure 5.5: conditional branch circuits](../../bookpages/Page_078.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. MOP51–54 select Z/L/T/DI bit0; MOP55 clocks H at T2. XOR uses IR bit3; inverted H output gates MOP22 at T6. Separate T capture edge and complete branch/page decoding are not drawn. PDF page 79. |
| [73: Figure 5.6: BB0 functional/MOP sequence](../../bookpages/Page_079.jpg) | Conditional flag/test selection and an explicit BB0 example; some controls are conditional or omitted from figure 4.1. Operand fetch increments PC; conditional MOP22 at F2T6 selects branch or fall-through. PDF page 80. |
| [105: Figure 6.22: test inputs](../../bookpages/Page_111.jpg) | Four direct test inputs; distinct from asynchronous interrupt requests. Four direct test lines and BT0/BT1; compares software subroutine, interrupt and test-input polling. PDF page 112. |
| [68: Instruction formats a–f](../../bookpages/Page_074.jpg) | TT selects one of four test inputs, not a target page. Explains flag encoding, SSX register selector, immediate bytes, address bytes and test/page selector fields. PDF page 75. |
| [106: CMC8 test-input discussion; then Intel 8048 comparison](../../bookpages/Page_112.jpg) | Retain p.106 subroutine wording without adding an undocumented N increment. Opening paragraph loosely calls BT actions subroutine jumps. No N increment or return-address mechanism is specified; later 8048 discussion belongs to another architecture. PDF page 113. |

## Working findings and assumptions

- **derived from documented circuit; selected in v009:** Store physical H.Q = selected condition XOR IR bit3 at F2T2. H.Q-bar controls MOP22 at F2T6; the functional table’s H=1 taken notation refers to the logical predicate, not physical Q. Restrict the conditional write overlay to branch execute; complete decoding is not drawn. Sources: pp. 72, 73.
- **consistency-supported extrapolation; H008 selected in v009; likely:** Use MOP31 at F1T1; sample condition at F2T2; increment PC through BR at T3/T4 while fetching the operand; capture target at T5; conditionally write PC at T6. This fits the documented two-cycle duration and reuses operand-fetch controls. No dedicated complete MOP table was found. Sources: pp. 67, 72, 73, 70.
- **hypothesis; H009 selected in v009; provisional:** Expose four logical test_inputs; MOP53 makes the selected current level available to H at T2 and records it in state.t. The T box has no documented capture edge, so separate synchronization/latency is not simulated. BT leaves N and PG unchanged. Sources: pp. 72, 68, 105, 106.
- **project interpretation; accepted working reading:** Project owner considers p.106 subroutine-jump terminology likely loose language. Treat BT as an ordinary conditional branch, preserving N; retain the literal wording as a source discrepancy. Sources: pp. 67, 106.
- **implementation preference; future hardware; not simulated historical behavior:** Project owner favors pullups on TEST inputs in a future implementation. Original input bias (pullup, pulldown or floating) remains unknown. Keep the research simulator default inputs unknown unless the experiment explicitly supplies levels.
- **consistency-supported extrapolation; H022 selected in v018 when execution control enabled:** Add a T4 MEMR checkpoint to the external operand/control-byte read where the sparse selected table omits MOP29. Preserve the active access during complete eight-slot waits and resume original T4 actions once. Do not extend this to CPU loopback, write strobes or SCW’s already-fetched control byte in F2. Sources: pp. 56, 58, 59.
- **implementation validation; board integration; shortened fixtures and literal program passed:** The complete figure8.6 traffic-light program runs through unchanged v018 MOP sequencing: literal bytes completed11,288,752 subdivisions and564,443 CPU events, returning to normal polling. Both T1/T3 demands are covered by explicitly shortened fixtures; observed lamp states, nine real subroutine calls and exact interval arithmetic are checked. This is internal consistency evidence, not hardware validation. Sources: pp. 146, 147, 144, 141.

## Open questions

- Does the T box add synchronization or an earlier sample? No timing edge is specified in figure 5.5.
- Original TEST input electrical bias is unknown; future-design pullups are a project choice, not recovered CMC8 behavior.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21,31 | — | — | — | — | — | — |
| F2 | — | — | 18,21,24,53,55 | 18,21,7,10,24,12 | 4,18,22,24 | 2,24 | 4,18 | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

The table shows static controls. At **F2T6**, the branch circuit adds MOP22 only when sampled physical H.Q=0 (Q-bar=1). N and PG remain unchanged. The actual overlay appears in trace `mops` and `branch_taken`. H samples at F2T2; static MOP22 at F1/F2T4 advances the operand PC regardless of outcome. See [v009 interpretation](../model-v009.md).

## OCR cross-references

7 candidate line matches on proposed printed pages: 70, 105, 106, 140, 145, 146.

[All snippets and scan links](../instruction-mentions.md#bt1). These are unreviewed leads and may include other-architecture examples.
