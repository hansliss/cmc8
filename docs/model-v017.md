# Architecture model v017: RESET

Predecessor: [v016](model-v016.md), preserved unchanged. v017 adds opt-in
active-low RESET sampling and the eight-slot reset cycle. The instruction
repertoire, datapath state fields and interrupt behavior are otherwise
retained. No new CPU data-storage component is introduced.

```sh
python3 -m cmc8 --model v017
python3 -m cmc8 --model v017 --json
python3 -m unittest tests.test_v017
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demonstration executes NOP on page 2 using R3 as PC, samples RESET low
at T7, releases the pin, runs the selected reset cycle, then executes
LRI R3,#A6 from address 000. Its 32 subdivisions end at N=0, PG=0, R0=02,
R3=A6 and INTA=0. Numbers here are hexadecimal unless otherwise stated.

## Source and controls

[Printed p.64](../bookpages/Page_070.jpg) explicitly states that MOP47 is
active only during T7. RESET is active low. A low level during T7 makes
the **following machine cycle** the reset cycle shown in
[figure 4.21b, p.65](../bookpages/Page_071.jpg). Figure 4.20 on the same
page is the separate interrupt circuit/entry sequence.

The reset table is preserved as `fig4.21_reset` in the
[literal source file](../specification/book-microprograms.json). It gives
functional operations, rather than a complete held-level numbered MOP row.
The executable `RESET_CYCLE` realizes it as:

| Slot | Numbered MOPs | Functional effect |
| --- | --- | --- |
| F0T0 | 42, plus named `clear_inta` | PG=0; INTA=0 |
| F0T1 | 40 | Constant zero drives DI |
| F0T2 | 40,45 | Hold zero; N=0 |
| F0T3 | 40 | Hold zero |
| F0T4 | 40,18,22 | Write zero into R(N), now R0 |
| F0T5 | — | No opcode capture |
| F0T6 | — | No AB preload |
| F0T7 | 30; 47 if reset input configured | Return to F0T0; sample RESET again |

Figure 4.21 explicitly clears INTA, but figure 4.2 assigns no numbered
MOP to that clear. The model exposes a named `clear_inta` control at F0T0.
It does not use MOP28, which samples INTR and could set INTA instead.
Evaluation traces expose both this control and MOP47's `reset_request`.

Zero is held on DI through T4 because DI is a wire, not a retained register.
The held controls and leading-boundary captures follow the existing endpoint
model; they are not additional printed entries or recovered physical edges.

## What changes, and what is preserved

The selected reset cycle sets **INTA=0, PG=0, N=0 and R0=0**, and returns
the phase/timing cursor to F0T0. It does not fetch an opcode, select external
memory, assert WRITE or strobe a control byte. The first ordinary fetch
therefore addresses page 0, byte 00 using R0.

The table does not specify clears for INTE, INTR, L, Z, SSE, WAIT, IR,
BR, AB, H, the TEST observation, EXR's provisional holding latch or R1–R7.
The model preserves those values, including unknown values. This is an
explicit interpretation of the listed reset operations; a more extensive
physical reset distribution would require further evidence.

External memory and peripherals retain their contents. Reset does not undo
writes or control strobes completed before its sample. The example external
control latch remains an example peripheral, not part of CPU reset state.

A prior SCWR wait can leave the modeled WAIT latch high during reset.
Reset selects its own cycle regardless; the table gives no WAIT clear.
The next ordinary fetch's always-ready MOP29 clears WAIT. The trace's
`waiting` field reports the latch value, not a claim that the reset sequence
itself is stalled.

## Sampling and controller integration

`ResetInput` is optional, as is interrupt integration. With reset configured,
MOP47 is added at every T7, including execute, interrupt-entry, reset and
SCWR wait cycles. The next cycle starts at F0T0 using `RESET_CYCLE` if the
sample was low. A selected cycle still runs if RESET returns high before
that cycle begins. Holding RESET low selects repeated reset cycles.

Page 64 describes T7 and the following machine cycle without restricting
the gate to instruction completion. Accordingly, reset can replace the
remaining cycles of a longer instruction. Work committed before the sample
remains committed; subsequent instruction actions are abandoned. A reset
sampled during an SCWR wait likewise selects reset without acknowledgement
or another control strobe. These are consistent controller interpretations
of the gate/prose, not separately printed interaction tables.

A previously sampled reset takes precedence over the following F0T0
interrupt check. This allows the reset cycle to clear INTA as specified,
without first consuming a pending request. Reset can also be sampled during
interrupt entry; effects already committed by entry remain committed.
This precedence is an integration choice consistent with the selected
following-cycle reset rule, not an explicit complete PLA priority table.

RESET is sampled at the start endpoint of T7, consistently with the existing
capture model. `set_reset()` changes the pin without advancing time or
changing CPU state. Pulses outside a sampled T7 are not latched. A pulse
arriving inside a subdivision, electrical pulse-width requirements and
propagation races remain outside this discrete-time model.

An unknown RESET level is permitted until MOP47 needs a decision. At that
point the simulator raises `ModelError`, rolls back the failing slot and
allows the experiment to supply the pin level and retry.

## Unknown startup state and the API

A cycle-accurate experiment must specify where observation begins. To start
with unknown CPU data immediately **after a known low RESET sample at a
preceding T7**, use `reset_sampled=True`:

```python
from cmc8.versions.v017 import InstructionSimulator, Memory, ResetInput, State

sim = InstructionSimulator(
    State(),
    Memory(program={0: 0}),  # NOP at the reset entry address.
    reset=ResetInput(1),     # Pin has already been released after that sample.
    reset_sampled=True,
)
event = sim.run_instruction()
assert len(event) == 8 and all(row.reset_cycle for row in event)
assert (sim.state.n, sim.state.pg, sim.state.registers[0], sim.state.inta) == (0, 0, 0, 0)
assert sim.state.registers[1:] == [None] * 7
assert sim.state.inte is None and sim.state.intr is None
sim.run_instruction()
assert sim.state.registers[0] == 1
```

That option supplies the prior controller context; it does not assert an
asynchronous reset or silently clock an unobserved T7. Otherwise the caller
steps the existing execution to T7 with RESET low. `set_reset(0)` alone
does not initialize unknown registers or make an earlier ambiguous fetch
executable. Clock startup and unknown initial timing-counter behavior are
not recovered from these figures.

`run_instruction()` now runs to a boundary that may represent an instruction,
interrupt entry, reset cycle, or an instruction prefix displaced by a reset
sample. Inspect the last row's `reset_sampled` to detect that displacement;
the following call returns the reset cycle. `SlotTrace.reset_cycle` identifies
all eight reset slots; `reset_level` records the pin. Partial reset cycles
can be stepped or resumed after a host run limit through the existing API.

## Interrupt and retained-IR consequences

Reset does not silently clear INTR or INTE. An already pending request can
therefore cause interrupt entry immediately after reset, before the first
ordinary startup opcode. Unknown INTR can likewise prevent an interrupt-
integrated experiment from choosing the next cycle: a quiet pin does not
initialize the latch. Experiments must state their interrupt initialization
assumptions explicitly; reset alone does not supply them in this model.

Reset also leaves IR unchanged, while suppressing ordinary opcode controls
throughout the reset cycle. On the following ordinary fetch, the inherited
IR-only decoder again permits deferred flag effects at T2. For example,
reset after fetching EIN can leave INTE unchanged during reset and enable
it during the first ordinary post-reset fetch.

This is the same retained-IR uncertainty exposed by interrupt entry in
v016. Tests preserve the prediction; they do not establish historical silicon
behavior or justify a new consumed-effect latch. Complete reset/interrupt/
opcode decoder precedence remains an open source question.

## Validation and remaining work

The 22 new tests cover:

- T7 gating, unknown inputs, named INTA clearing and exact reset landmarks.
- Every original N/page selection and preservation of unlisted storage.
- Startup after a stated prior sample, released/held RESET and missed pulses.
- Reset at all **626 machine-cycle boundaries across 239 opcode variants**,
  including abandoning later actions and fetching from 000 afterward.
- Reset before a store, after a committed store, during an SCWR wait and
  interrupt entry, plus reset priority over a pending interrupt.
- Unknown interrupt state, retained EIN, failing-slot rollback, retry and
  bounded/resumable reset execution.
- All 239 opcode traces/effects against v016 with reset off and with the
  configured pin quiet, and the 32-slot runnable demonstration.

Generic MEMR waits, HALT, single-step and detailed physical pin behavior
remain future work. The [v016 holistic review](holistic-review-v016.md)
continues to describe inherited instruction-level hypotheses.

Validation completed: **298 tests pass** across the complete suite. All
46 generated reference artifacts are current, the v017 guide links resolve,
and v016 source-package hashes are unchanged.

## Reopened question: interrupt initialization by RESET

The project owner raised a plausible omission after reviewing v017: should
RESET also clear INTR? The current preservation rule is a literal-table
baseline, not an established hardware fact.

Figures 4.20a/4.21 do not show a RESET clear for INTR or INTE. Nevertheless,
interrupt-request capture is asynchronous: selecting the reset microprogram
does not by itself close the INTE-controlled INT→INTR set gate. Reset and
interrupt-entry sequences can be mutually exclusive while the request gate
continues to operate. Preserved pending or unknown INTR therefore raises a
real startup question, particularly if reset is expected to establish a
reliable path into initialization software.

Retain these alternatives without selecting a new architecture yet:

- An omitted RESET clear of INTR would discard a stale pending request.
- An omitted RESET clear of both INTR and INTE would additionally prevent
  a held-low INT from immediately setting INTR again, until software enables
  interrupts. This would give a stronger initialization guarantee.
- Additional decoder gating could prevent acceptance or request capture
  around reset; its duration and release condition are not documented.

Clearing INTR alone is insufficient to keep requests clear if INTE remains
one and INT remains low. Clearing only INTE also does not remove an already
latched request under the figure-4.20a interpretation. The book does not
currently distinguish these alternatives. Figure4.18's simplified RESET→
FETCH path is relevant context, but not a complete startup-priority circuit.
The v017 implementation and its preservation tests remain unchanged; those
tests demonstrate the selected baseline's consequences, not proof that the
physical reset distribution excludes these omitted clears.

In subsequent discussion, the project owner clarified that INTA clearing
while INTR survives is coherent: the old acknowledgement ends and a pending
request can be acknowledged after reset. This is now treated as a startup
behavior, rather than evidence requiring an omitted clear. The baseline
remains selected; the alternatives above are retained for future evidence.
