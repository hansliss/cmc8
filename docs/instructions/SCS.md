# SCS

[All instructions](../instruction-set.md)

**Encoding:** `00001001`; **bytes:** 2; **cycles:** 3; **flag column:** blank.

**Book summary (documented summary):** Send control signals.

## Reviewed sources

| Printed page / figure | What to look for |
| --- | --- |
| [67: Figure 5.1: instruction repertory](../../bookpages/Page_073.jpg) | Baseline visually transcribed from figure 5.1. Primary baseline for all 43 mnemonic families, encodings, cycles and flag columns. Normalized zero glyphs and mnemonic spacing only; image remains authoritative. PDF page 74. |
| [97: Figure 6.14: SCW/SCS](../../bookpages/Page_103.jpg) | STRCS and SCWR are separate from ordinary port reads/writes; SCW adds acknowledgement waits. STRCS accompanies the second byte on DB; figure 6.14 illustrates an external latch as one possible receiving circuit, not required CMC8 hardware. Separate interface from LRD/SRD. PDF page 104. |
| [98: Figure 6.15: SCS vs SCW](../../bookpages/Page_104.jpg) | STRCS and SCWR are separate from ordinary port reads/writes; SCW adds acknowledgement waits. SCS continues after strobe; SCW waits for active-low SCWR acknowledgement. PDF page 105. |
| [99: SCW microprogram introduction](../../bookpages/Page_105.jpg) | STRCS and SCWR are separate from ordinary port reads/writes; SCW adds acknowledgement waits. Opcode fetch and second control-byte address; wired acknowledgement context. PDF page 106. |
| [100: Figure 6.17: SCW microprogram](../../bookpages/Page_106.jpg) | STRCS and SCWR are separate from ordinary port reads/writes; SCW adds acknowledgement waits. SCWR sampled at F2T4 and each wait T4. Figure6.17, figure6.18 and later prose put PME rise F1T2/strobe F1T6; one earlier paragraph says F2T2/F2T6. E008 selects the consistent F1 labels without altering literal source. PDF page 107. |
| [101: Figure 6.18: SCW handshake timing](../../bookpages/Page_107.jpg) | Confirms F1T6 strobe and retained program-memory bus data; SCW example adds two full eight-slot waits. Strobe F1T6; PME/control-byte address/data held through two complete waits (16 extra subdivisions), then F2T6 releases PME. SCWR low around T4 ends waiting. Later PIO examples on this page are other-architecture context. PDF page 108. |

## Working findings and assumptions

- **established project correction; E008; selected in v015 and subsequently accepted by project owner:** Use PME rise F1T2 and STRCS at F1T6, agreeing with both figures6.17/6.18 and later prose. Retain the conflicting F2T2/F2T6 paragraph separately; the genuine PME fall remains F2T6. Sources: pp. 100, 101.
- **documented functional behavior; derived held controls; selected in v015:** Advance PC past both bytes, keep AB on the control-byte address, and hold PME from F1T2 through F2T5. External program memory directly drives the control byte at STRCS F1T6; figure 6.14’s latch is an example receiver, not a CPU requirement. No control-byte→BR capture, CPU DB output, EDE or WRITE. STRCS is a named control because no numbered MOP was supplied. Sources: pp. 97, 99, 100, 101.
- **consistency-supported extrapolation; H020 selected in v015; likely:** Use the SCW three-cycle control-byte/strobe schedule but omit MOP50. SCS neither samples nor waits for SCWR, including an unknown input. Figure5.1 supplies three cycles and p.98 supplies send-and-continue semantics; no separate complete SCS timing table located. Sources: pp. 67, 98, 100, 101.
- **scope clarification; project-owner clarification:** The CPU presents the control byte with STRCS and, for SCW, samples SCWR. External hardware may use the byte in any suitable way. ControlPort models the book’s example latch and an acknowledgement source for experiments; its retained value is peripheral state, not mandatory system hardware or CPU state. Sources: pp. 97, 98.
- **consistency-supported extrapolation; H022 selected in v018 when execution control enabled:** Add a T4 MEMR checkpoint to the external operand/control-byte read where the sparse selected table omits MOP29. Preserve the active access during complete eight-slot waits and resume original T4 actions once. Do not extend this to CPU loopback, write strobes or SCW’s already-fetched control byte in F2. Sources: pp. 56, 58, 59.

## Open questions

- Exact internal STRCS generation and pulse edges within T6 are not specified by the numbered MOP list; v015 uses a named slot-level output and the example peripheral’s latch capture at its modeled rise.
- SCS detailed held controls and the F3 realization of SCWR waits retain the stated consistency-based confidence; generic memory-ready/HALT waits and physical /WAIT pulse shape remain outside this version.

## Executable control table

Implemented in [v018 sequences](../../cmc8/versions/v018/sequences.py). Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. Runtime overlays (notably deferred flag updates) are additional to this base table.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | — |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,22,24 | 24 | 24 | 24 |
| F2 | 24 | 24 | 24 | 24 | 24 | 24 | — | 30 |

A phase write (MOP31) can change F1 to F2 while T continues. Unreached table cells consume no time. The trace is the source for actually executed slot labels.

**Named external output:** STRCS is high at F1T6. It has no assigned MOP number in these source tables. Program memory supplies the control byte on DB; the CPU does not reload it through BR. Figure 6.14’s external latch is an example receiver, modeled by the peripheral harness rather than required by the CPU. SCS does not sample SCWR. See [v015 timing and API](../model-v015.md).

## OCR cross-references

33 candidate line matches on proposed printed pages: 3, 9, 13, 15, 22, 49, 50, 51, 53, 55, 64, 67, 71, 97, 98, 124, 129, 135, 136, 150, 151, 152.

[All snippets and scan links](../instruction-mentions.md#scs). These are unreviewed leads and may include other-architecture examples.
