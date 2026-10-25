# Architecture model v016: interrupt integration

Predecessor: [v015](model-v015.md), preserved unchanged. v016 retains all
43 instructions and adds **opt-in INT/INTR/INTA integration**, a separate
eight-subdivision entry cycle, and complete EIN/handler/RSR tests. The
existing INTE, INTR and INTA storage fields suffice; no extra CPU latch or
flag stack is added for this work.

```sh
python3 -m cmc8 --model v016
python3 -m cmc8 --model v016 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demonstration holds INT low while main executes EIN and NOP. It enters
the handler at address002 on page1, loads R4=69, executes EIN; RSR, then
resumes main to load R3=A6. The example source releases INT after acceptance.
Six opcodes plus one entry event consume 80 subdivisions, ending at N=0,
PG=1, PC=24, INTE=1, INTR=0, INTA=0. Values here are hexadecimal.

## Sources and selected interpretation

| Source | Observation |
| --- | --- |
| [P.62](../bookpages/Page_068.jpg) | INTE gates active-low INT into an immediate request latch; EIN takes effect at next-fetch T2 |
| [P.63, fig.4.18](../bookpages/Page_069.jpg) | Finish the current instruction; acknowledge, mask/clear request, increment N, vector to002; return via RSR |
| [P.64, fig.4.19](../bookpages/Page_070.jpg) | EIN delayed enable during following RSR fetch; retained opcode timing |
| [P.65, fig.4.20a](../bookpages/Page_071.jpg) | INTR is an SR latch; INTA samples INTR at F0T0 and feeds the PLA |
| P.65, fig.4.20b | Functional eight-slot entry sequence, separate from normal instruction fetch |

The circuit is more precise than the simplified flowchart for pulses and
already-latched requests. v016 follows it: an enabled low INT sets INTR,
which remains set after INT returns high or DIN masks further input. INTA
samples the retained INTR directly; current INTE is not an extra gate on
an already pending request. A request latched before masking can therefore
still be accepted. This is a source-supported circuit interpretation, not
an assumption that DIN clears pending work.

Endpoint sequencing, interrupt-entry decoder precedence and some cross-page/
retained-IR edge cases remain model interpretations. No claims about analog
pulse widths, propagation races or the electrical polarity of the external
acknowledge driver follow from the logical state fields below.

## Request latching and F0T0 acceptance

INT is a raw active-low input. INTE=1 and INT=0 asynchronously set INTR.
An inactive or masked input does not clear INTR; MOP46 clears it. Unknown
state/input values propagate rather than defaulting to zero.

MOP28 clocks INTR into INTA **only at F0T0**. It is not the asynchronous
request gate itself, despite the original list's shorthand “sample INT”.
At the start of each ordinary boundary event, the simulator settles a
stable input and previews that clock. If pending INTR is1, the entry table
replaces the normal fetch. Otherwise INTA becomes0 and opcode fetch proceeds.
No opcode is consumed by the entry event.

At accepted T0, the pending request is sampled first, then the documented
INTE/INTR clear takes effect. The set gate is settled again with INTE=0,
so a still-low INT does not immediately relatch. At an ordinary EIN effect,
INTE becomes1 and the gate is settled again; a low input can then set INTR
without clocking INTA. This atomic endpoint ordering realizes the functional
circuit/table; simultaneous analog set/reset races are not modeled.

## Entry controls

The book gives functional operations, not a complete held-level numbered
row. v016 realizes them as:

| Slot | MOPs | Operation |
| --- | --- | --- |
| F0T0 | 28,39,46 | INTR→INTA; disable INTE; clear INTR |
| F0T1 | 41 | Constant02→DI |
| F0T2 | 41,16 | Hold02; increment N modulo8 |
| F0T3 | 41 | Hold02 |
| F0T4 | 41,18,22 | Write02 to newly selected R(N) |
| F0T5 | — | No opcode capture |
| F0T6 | — | No AB preload |
| F0T7 | 30 | Return to F0T0 |

There is no PME/SME/EDE/WRITE, extra PC increment, memory return-address
push, automatic PG change or L/Z save. The old R(N) remains the return PC
already established when the interrupted instruction finished. The next
register becomes PC and is overwritten with002. After eight entries N
wraps, following the inherited three-bit counter; no unbounded stack or
software overflow protection is invented.

The vector uses the **current PG**. Figure4.20 has no PG write, whereas
the adjacent reset table explicitly clears PG. RSR restores N and thereby
the saved PC; it does not restore PG. A handler changing page needs an
explicit convention, as with the established subroutine model.

INTA remains logically1 during entry and is clocked again at the next
F0T0. With INTR cleared and INTE disabled, that next sample normally makes
INTA0 while fetching the first handler opcode. Trace state `inta` represents
the logical latch Q; it is not a complete electrical acknowledge-pin model.

## EIN followed by RSR

With INTE initially0 and INTR0, a held low input is ignored during EIN's
own fetch. At the following instruction's F0T0, INTR is still0, so no entry
is selected. At T2, retained EIN asserts MOP38; INTE becomes1 and the input
can set INTR. F0T0 has already passed. That following instruction completes
before its next F0T0 can accept the request.

Inside a handler this gives the documented EIN; RSR order: enable during
RSR fetch, latch a still-held request, complete RSR's decrement of N, then
accept at the caller boundary. The test verifies the second entry increments
from the restored caller N, rather than nesting before the return finishes.

RSR alone does not enable interrupts. The p.64 prose suggesting reenable
by RSR is read with the explicit preceding EIN sequence. An ISR that runs
EIN followed by a non-return instruction can instead allow nested entry
after that instruction; no hidden “inside ISR” mask prevents it.

## An exposed retained-IR uncertainty

Entry does not overwrite IR. Its selected PLA table suppresses ordinary
IR-based fetch controls, including deferred flag effects, throughout the
entry cycle. The next ordinary handler fetch again uses retained IR until
T5. No consumed-flag latch or post-entry suppression state has been added.

Consequently, **consecutive EINs with a held request** expose an edge case:
the request can be accepted after the second EIN, entry clears INTE, but
IR still contains EIN. Under the current IR-only interpretation, that old
opcode can reenable INTE during the first handler fetch. The executable
test deliberately records this consequence rather than silently hiding it.

The book does not settle all such combinations or the complete gating of
IR-based controls by INTA. A design could consume/suppress an old effect or
use different interrupt decoder precedence. No new circuit is claimed here.
The ordinary EIN; RSR case has much stronger direct support; this edge case
remains a hypothesis to revisit. Similar interrupted flag instructions
should retain that distinction in future investigations.

## API and experiment boundaries

Interrupt integration is enabled by explicitly supplying `InterruptInput`.
Without it, instruction-only experiments retain v015 behavior and need no
assumed interrupt initialization. This is an experiment configuration,
not a claim that the actual CPU lacks its circuit when a pin is quiet.
With integration active, acceptance must have a known pending request;
quiet INT does not magically clear an unknown initial INTR latch.

```python
from cmc8.versions.v016 import InstructionSimulator, InterruptInput, Memory, State

state = State(n=0, pg=1, inte=0, intr=0, inta=0)
state.registers[0] = 0x20
sim = InstructionSimulator(
    state,
    Memory(program={0x120: 3, 0x121: 0, 0x102: 3, 0x103: 0x0F}),
    interrupts=InterruptInput(0),
)
sim.run_instruction()  # Main EIN; still disabled.
sim.run_instruction()  # NOP completes; request now pending.
entry = sim.run_instruction()
assert len(entry) == 8 and entry[0].interrupt_accepted
assert sim.state.n == 1 and sim.state.registers[0] == 0x22
sim.set_interrupt(1)    # Example source releases its request after acknowledgement.
sim.run_instruction()  # Handler EIN.
sim.run_instruction()  # RSR: enable during fetch, then restore N.
assert sim.state.n == 0 and sim.state.inte == 1
assert sim.state.registers[0] == 0x22
```

`run_instruction()` runs to the next boundary and therefore returns either
an ordinary instruction or the eight-slot event labeled `INTERRUPT`.
Its bounded/resumable host API remains available. `SlotTrace.int_level`
records the input and `interrupt_accepted` marks the accepted T0 event;
evaluation `inta_input` records the request sampled before clearing.

Use `set_interrupt(level)` to record pulses without advancing a clock slot.
It settles the asynchronous gate and returns a CPU trace observation;
these observations do not inflate the timed slot trace. For example, in an
enabled configured experiment, calling `set_interrupt(0)` then
`set_interrupt(1)` leaves INTR latched. Plain field changes are observed at
slot boundaries; changing a Python field twice between observations cannot
represent the missing pulse. Real subslot transitions, pulse-width limits
and metastability remain outside this endpoint simulator.

Requests can latch during instruction execution or SCWR waits, but entry
is selected only at F0T0 after completion. A wait-phase T0 is not a fetch
boundary. v016 does not assume INT cancels an unacknowledged SCW; that wait
still needs SCWR. This follows the selected completion rule, not additional
source evidence for every external-control interaction.

## Validation and remaining work

Tests cover the request latch truth table and unknowns, pulse retention,
masked pulses, sample-before-clear, EIN's post-enable gate, all N/page
combinations, PC preservation, actual handler fetching, wrapped N return,
nested requests, DIN with an already pending request, RSR without EIN,
EIN; RSR under a held request, host-limit resumption and requests during
SCWR waits or between EXR's two register writes.

All 239 opcode variants retain v015 traces with interrupt integration off,
and their final CPU/memory/peripheral effects agree with a quiet interrupt
input enabled. The complete demonstration resumes main after servicing the
request. These are consistency checks of the sourced/selected model, not
hardware validation.

The 43-instruction repertoire is unchanged. Full reset sequencing, generic
MEMR waits, HALT and single-step remain future work. IRQ endpoint ordering,
INTA/retained-IR precedence and partial physical pin behavior remain explicit
uncertainties alongside earlier instruction timing and the accepted EXR
working latch hypothesis.

Validation: **273 tests pass** across the versioned suite. The 46 generated
reference artifacts are current, local documentation links resolve, and
v015 source-package hashes remain unchanged. The text/JSON demonstration
has 80 slots with one accepted entry at slot16, and the guide's runnable
example completes the handler return.

## Whole-model review

The subsequent [holistic review](holistic-review-v016.md) found no new
instruction-result contradiction and adds three independent current-model
checks covering 5,736 instruction cases, 1,434 deferred-flag pairs and
239 mid-instruction interrupt requests. It also inventories control overlays
and distinguishes instruction coverage from reset/external-control work.
The numbered simulator implementation is unchanged.
