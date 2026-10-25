# Architecture model v008

Predecessor: [v007](model-v007.md), preserved unchanged. This complete
numbered package adds JMP, JCR, JSR and RSR. They use the existing MOP-driven
datapath; there are no direct instruction-level PC assignments or hidden
page/return stacks. Python's standard library is sufficient.

```sh
python3 -m cmc8 --model v008
python3 -m cmc8 --model v008 --json
python3 -m unittest discover -s tests -v
python3 -m tools.build_instruction_reference --check
```

The demonstration executes JMP from page 1 to page 2, JSR to a subroutine,
JCR through R3, RSR back to the caller, then NOP. It consumes 80 subdivisions
(16+24+16+16+8) and finishes at N=0, PG=2, PC=43 (hexadecimal).

## Sources and confidence

Start with the [instruction reference](instruction-set.md), which links all
43 figure-5.1 families to the book and displays both source microprograms
and this model's executable tables. Authored evidence and interpretations
live in `specification/instructions.json`; source microprograms are preserved
in `specification/book-microprograms.json`.

| Instruction | Encoding | Bytes | Cycles | Evidence |
| --- | --- | --- | --- | --- |
| JMP | 111100PP | 2 | 2 | Figure 5.1; p.70 fig.5.3 numbered MOP table; p.71 prose |
| JCR | 11111RRR | 1 | 2 | Figure 5.1; p.70 register-target semantics; H007 detailed schedule |
| JSR | 00001100 | 2 | 3 | Figure 5.1; p.71 fig.5.4 functional sequence; explicit MOP realization partly derived |
| RSR | 00001111 | 1 | 2 | Figure 5.1; p.71 fig.5.4 functional sequence and phase-skip explanation |

JMP has the strongest detailed table evidence. JCR's complete schedule is
**likely / consistency-supported extrapolation**. JSR/RSR closely follow
the documented functional operations; held controls and mappings onto the
simplified datapath remain model interpretations. Passing tests do not
promote these interpretations to silicon-level proof.

## Phase skip and two-cycle execution

JMP and RSR execute MOP31 at F1T1. It writes 2 to the phase counter without
resetting timing. Consequently the slots after normal fetch are:

```text
F1T0, F1T1, F2T2, F2T3, F2T4, F2T5, F2T6, F2T7
```

There is no extra full F1 followed by a full F2, and no replay of F2T0/T1.
The existing capture mechanism already supported an explicit phase write;
this version supplies the sequences that exercise it. End-of-cycle MOP30
returns to F0T0. Trace labels identify the slot that started, even if its
capture changes the phase for the next slot.

JCR uses the same skip to fit its documented two-cycle duration. Its skip
is extrapolated from the common control scheme, not copied from a dedicated
JCR figure. `run_instruction()` now documents 8, 16 or 24 returned slot
records and still ends at the next F0T0.

## JMP

F0 fetch increments PC once and preloads AB with the operand-byte address.
F1T1 skips to phase 2. PME is high for F2T2–T5. The destination low address
enters BR at the start of T5, still read using the **original PG**. At T6,
MOP4+18+22 write BR to R(N), and MOP15 loads PG from the low two bits of
IR. PME falls at T6; T7 resets the phase. There is no extra PC increment in
the execute cycle because the PC is replaced by the branch target.

The numbered table in fig.5.3 does not show MOP29. v008 preserves that
rather than adding an undocumented ready-check slot; the whole runner
continues to require the explicitly always-ready scenario.

## JSR and RSR

JSR fetches its address byte during F1 while incrementing the **old** PC a
second time, preserving the address after both instruction bytes. Unlike
a normal load, its F1T6 does not copy BR into AB: fig.5.4 leaves that
transfer absent. At F2T2, MOP16 increments N. At F2T6, MOP4+18+22 install
the buffered destination in the newly selected R(N). PG is unchanged.
F1's held controls, including the inherited ready check, are derived from
the established operand-fetch model.

RSR fetch increments the callee's current PC normally, skips to F2 at
F1T1, and uses MOP17 at F2T2 to decrement N. It then reaches the saved
caller PC without copying a return address through memory. N wraps modulo
eight, matching the inherited three-bit counter model; there is no new
software overflow/underflow check or unbounded return stack.

Figure 4.19 labels RSR's execute cycle F1; fig.5.4/p.71 explicitly describe
the phase skip and F2 execution. v008 selects the latter more detailed
account, retaining the earlier label discrepancy in the catalogue. RSR
alone does **not** assert MOP38. EIN preceding RSR can enable INTE during
RSR's fetch as documented, using the retained-IR mechanism from v006.

There is one PG register in this model. JSR/RSR do not save or restore it.
If a subroutine changes page via JMP, returning changes N but leaves that
new page active. Cross-page subroutines therefore need an explicit calling
convention; an automatic page stack is not invented by the simulator.

## JCR: selected H007

Read R(A) onto DI at F1T0. At F1T1, hold the source, drive DB and assert
MOP31. Hold source and DB through F2T5, where MOP2 captures the resolved
CPU-driven DB into BR. At F2T6, switch selection to N and write BR through
DI into R(N). Neither PG nor N changes. This works even if A=N, in which
case the source value is the PC already incremented by fetch.

The buffer separates source-register selection from destination selection,
avoiding two simultaneous selectors on the modeled register port. It
reuses AND/indexed preparation and the jump write slot. An earlier buffer
capture or a later source read could also be consistent with the visible
semantics; these alternatives remain unselected pending further evidence.

## Validation and remaining work

Tests check every PC selector, source/destination pages and target boundary
values for JMP; every JCR source/PC alias pairing; caller-PC preservation;
N wraparound; nested calls and returns; PC byte wrap; the exact phase-skip
slot labels; and the original-page operand fetch before PG changes. An
actual destination opcode is fetched after cross-page JMP. Delayed and
unknown target data are rejected without committing partial slots.

An EIN; RSR program verifies the documented deferred-enable sequence at
trace level. This is **not an interrupt test**: INTR/INTA acceptance and
external INT have not been implemented. Existing instructions are compared
with preserved v007, and the decoder is checked against the independent
43-family catalogue for all 256 possible bytes (101 are now supported).

The earlier provisional flag and indexed timing, always-ready assumption,
simplified devices, endpoint latch model and ALU/electrical limitations
remain. Conditional branches, full interrupt handling, wait states and
handshake instructions remain unimplemented. The catalogue provides source
locations and unresolved details for those next steps.
