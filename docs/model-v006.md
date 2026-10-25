# Architecture model v006

Predecessor: [v005](model-v005.md), preserved unchanged. This complete
numbered package adds EIN, DIN, SEL, REL, SEZ and REZ. All six are
**provisional implementations** pending wider validation; EIN has higher
confidence because its effect timing is directly documented.

## Run and inspect

```sh
python3 -m cmc8 --model v006
python3 -m cmc8 --model v006 --json
python3 -m unittest discover -s tests -v
```

The demo runs EIN; DIN; SEL; REL; SEZ; REZ; NOP on program page 1. Each
instruction occupies eight subdivisions. Its flag effect appears during
the following fetch, so the final NOP allows REZ's effect to happen. The
56-slot table shows IR, PC, flags and the originating opcode for each
update. The JSON records include `control_ir` (IR before the slot's captures)
and `flag_effect` (operation, MOP, flag/value, confidence and evidence basis).

Read `cmc8/versions/v006/sequences.py` for the six entries and
`instructions.py` for the old-IR controls. The datapath already implements
MOP34–39; flags are updated through those MOPs, not by a separate
instruction-level assignment. This version adds no pending-effect latch.

## Confidence and evidence

| Opcode | Instruction | MOP | Effect | Working confidence |
| --- | --- | --- | --- | --- |
| 02 | DIN | 39 | INTE=0 | Likely; consistency-supported extrapolation |
| 03 | EIN | 38 | INTE=1 | Higher; documented timing, derived decoder implementation |
| 04 | REL | 35 | L=0 | Likely; consistency-supported extrapolation |
| 05 | SEL | 34 | L=1 | Likely; consistency-supported extrapolation |
| 06 | REZ | 37 | Z=0 | Likely; consistency-supported extrapolation |
| 07 | SEZ | 36 | Z=1 | Likely; consistency-supported extrapolation |

Numbers in the opcode column are hexadecimal. The opcodes and one-cycle
classification are documented in fig.5.1, p.67 (`Page_073.jpg`). Page 68,
format a (`Page_074.jpg`), explicitly identifies bits 2–1 as the flag
selector and bit 0 as clear/set, with bits 7–3 zero.

Page 62 and fig.4.19 on p.64 (`Page_068.jpg`, `Page_070.jpg`) document
EIN setting INTE at the beginning of F0T2 in the following instruction.
IR retains EIN until the following fetch's T5, so a decoder using old IR
can generate MOP38 there. Applying the same mechanism to the other five
operations follows the project's consistency principle. It remains a
well-founded choice rather than established timing for those operations.
See [the source analysis](flag-instruction-timing.md) for alternatives.

## Deferred effects and instruction boundaries

All six instruction tables perform fetch and increment, preload AB from
BR at T6 and reset the phase at T7. Early fetch controls additionally
inspect retained IR. At F0T2, if IR holds one of 02–07, the corresponding
flag MOP is asserted alongside the ordinary fetch MOPs. At T5 the new
opcode replaces IR, preventing repeats during later phases or fetches.

`run_instruction()` returns after eight slots for a flag instruction,
**before that instruction's own flag effect has happened**. It does not
silently run part of the next instruction. Stepping the next three slots
(T0, T1, T2) exposes the deferred effect. Running the next instruction also
exposes it in that instruction's trace. No extra pending-state flag is
needed: retained IR carries the relevant opcode across the boundary.

Initializing or restoring a state whose IR already contains a flag opcode
means that opcode can take effect at the next F0T2. Initial IR defaults to
unknown and causes no invented flag operation. Restoring execution should
preserve IR as well as the programmer-visible registers.

## Consistent NOP tail

Figure 4.19 includes BR→AB at T6 for the one-cycle EIN. Under the new
consistency principle, v006 chooses that same preload for NOP and the
other flag instructions. This changes NOP's AB timing from v005's idle
T6 choice; its PC increment, instruction length and flag behavior are
unchanged. The old idle-T6 interpretation remains in v005 and its guide.
NOP's preload and the five other flags' matching fetch tails remain
consistency-supported extrapolations, not newly recovered source facts.

## Validation and next steps

Trace tests exercise all six operations for every N selector, all four
pages and both initial flag values. They check that own-cycle execution
does not update the flag early, T0/T1 leave it alone and the following T2
updates only the selected flag through the expected MOP. Tests also cover
consecutive set/clear instructions, PC wraparound, manual stepping,
resuming with retained IR, a delayed effect before a load, and a missing
next opcode after the effect has already occurred. Prior load/store
families are compared against v005, and v005's NOP tail remains tested.

These tests check the selected model and its trace bookkeeping. They do
not establish interrupt acceptance semantics or verify flag timing against
hardware. JMP, JSR and RSR should precede interrupt integration tests;
conditional branches are needed for meaningful programs consuming L/Z.
No jump, subroutine, branch or interrupt handling is added in this version.

The earlier always-ready memory assumption, simplified peripherals,
endpoint latch observations and other datapath/electrical limitations
remain unchanged. Confidence labels are not promoted by passing these tests.
