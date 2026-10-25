# Architecture model v018: MEMR, HALT and single-step

Predecessor: [v017](model-v017.md), preserved unchanged. v018 integrates
memory-ready waits, HALT and single-step through one continuation mechanism,
also used by SCWR. It adds the **documented HALT latch** from figure 4.15;
SSE and WAIT were already represented. The 43 instruction families and
239 encodings are unchanged.

```sh
python3 -m cmc8 --model v018
python3 -m cmc8 --model v018 --json
python3 -m unittest tests.test_v018
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demonstration begins LRS R3,[80] on page 1. MEMR initially holds its
opcode fetch waiting; memory then becomes ready, HALT retains the wait,
and SS grants one instruction while HALT stays low. Its 40 subdivisions
end with PC=22, R3=69 and SSE=0. There are two wait cycles, not repeated
instruction fetches. Numbers here are hexadecimal unless otherwise stated.

## Source evidence

| Source | Observation |
| --- | --- |
| [p.56](../bookpages/Page_062.jpg) | MEMR high requests an eight-subdivision F3 wait; low resumes. Execute reads can wait as well as opcode fetch |
| [p.58, fig.4.15](../bookpages/Page_064.jpg) | HALT request latch, OR with MOP29-gated MEMR, T4 WAIT capture and output masking |
| [p.59, fig.4.16](../bookpages/Page_065.jpg) | LRS with one wait per read: six machine cycles, three instruction phases; enables/addresses retained |
| [p.60](../bookpages/Page_066.jpg) | Resume original work at T4; high HALT asynchronously clears its request latch; WAIT pin pulses high each T4 |
| [p.61, fig.4.17](../bookpages/Page_067.jpg) | Three HALT wait cycles suspend opcode fetch before operand/data execution |
| [p.88](../bookpages/Page_094.jpg), [p.89, fig.6.6](../bookpages/Page_095.jpg) | HALT-low SS/SSE handshake permits one instruction and requires release to rearm |
| [p.90](../bookpages/Page_096.jpg), [p.91, fig.6.8](../bookpages/Page_097.jpg) | SS low during a later T3 leaves the wait; next instruction fetch waits again; full SSE circuitry omitted |

MEMR means **memory ready** in this book. Its raw pin is high while waiting
is requested and low when ready. It is distinct from PME/SME read enables.
The 8080 and Z80 comparisons in chapter 6 are not CMC8 circuit evidence.

## Shared wait continuation: H022

At a read checkpoint, the model samples the wait decision at the start of
T4. If blocked, it selects F3 and suppresses the original T4 actions. Timing
continues T5,T6,T7,T0,T1,T2,T3; the following T4 checks again. Each rejected
check therefore adds exactly eight subdivisions. When ready, the interrupted
phase's original T4 actions run once and normal T5 follows.

For example, opcode fetching has already calculated PC+1 into BR at T3.
During the wait, it retains BR and the old architectural PC. At the returning
T4, BR is written into PC; T5 then fetches IR. The PC increment is neither
lost nor repeated. Operand-fetch PC increments follow the same rule.

AB, PG and the external read enable remain stable throughout the pause,
so the external memory harness's access age continues accumulating. Normal
register transfers, ALU operations, opcode captures, strobes and deferred
flag effects are suppressed in the intervening F3 subdivisions. The retained
PME/SME/EDE controls express the held outputs in the timing diagrams; the
book's statement that F3 has no instruction MOPs does not mean those enables
fall while waiting.

`WaitContext` records the interrupted phase, held enables and wait kind.
It is an explicit sequencer continuation, not a claim that the real chip
contains a newly identified phase-save register. The implementation is
in [instructions.py](../cmc8/versions/v018/instructions.py); storage and
combinational gates remain in [model.py](../cmc8/versions/v018/model.py).

**Read-check coverage is partly inferred.** Some sparse selected schedules
omit MOP29, including JMP and two-cycle flag/TEST branch operand reads.
With execution control enabled, H022 consistently adds the T4 checkpoint
for external reads whose T5 captures data, and for SCS/SCW's F1 control-byte
read. This overlay appears in traces, not as a silent change to the printed
source rows or the retained static instruction tables.

CPU-driven register→DB→BR loopback does not get a memory wait. Neither does
an external write strobe, for which the selected tables provide no MOP29
checkpoint. SCW's F2 retains a control byte already fetched in F1; MEMR does
not repeatedly delay that retained byte. Its F2 checkpoint is SCWR instead.
I/O read waits inherit the existing load-family/EDE consistency hypothesis.

## HALT latch and single-step: H023

Figure 4.15 adds detail absent from the simplified figure 4.1: a HALT request
latch set during F0T2 and asynchronously cleared when HALT is high. v018
represents its Q as `State.halt`. This is documented storage, unlike EXR's
provisional extra latch.

A low HALT reaching the fetch T2 window causes the later T4 check to wait.
A low assertion after that window does not interrupt operand/data execution;
it is recognized at the next opcode-fetch window. A subsequent high HALT
can clear the latch before T4, allowing the read to proceed. During a fetch
wait, the controller repeats the corresponding T2 window without repeating
the instruction's ordinary fetch controls.

Single-step is consulted on the HALT-low path:

| SS/SSE condition | Selected effect |
| --- | --- |
| SS high | MOP49 sets SSE; remain halted |
| SS low, SSE=1 | MOP48 clears SSE; grant completion of this instruction |
| SS low, SSE=0 | Remain halted; a held button does not grant another instruction |
| HALT high | Run normally; SS is not consulted |

The model places this handshake at fetch-context T3, supported by the p.90
SS timing statement. The exact MOP48/49 placement and internal gating are
**H023**, because p.91 explicitly omits the full SSE circuit. Unknown SSE
is not assumed armed: holding HALT low and SS high can establish SSE=1
before the first step.

A selected step still respects MEMR. If memory is busy, the controller
retains the grant until the current fetch can finish, rather than consuming
another grant or becoming stuck because SSE has already cleared. Returning
SS high during that granted fetch does not revoke permission; the next
halted fetch can rearm. This grant/continuation interaction is a consistent
working interpretation, not an additional printed circuit.

After the instruction finishes, its successor's address is presented and
its fetch can halt again before PC writeback. Single-step executes an entire
instruction, including operand/data and SCWR waits; it does not bypass an
unacknowledged SCW. HALT does not create an early stop inside that execution.

## WAIT latch versus physical output

`State.wait=1` is the internal WAIT request. Figure 4.15 masks its active-low
output during T4, so the physical WAIT pin is **high throughout every T4**,
even during repeated wait cycles. Outside T4 it is the inverse of WAIT.Q.
This produces the one-subdivision high pulses shown in figures 4.16/4.17.

Evaluations expose that logical pin level as `wait_pin`, independently of
`SlotTrace.waiting`, which continues to report the internal latch value.
This is an ideal subdivision-level output; propagation delay and electrical
pulse shapes are not modeled.

## Inputs, memory harness and API

Execution control is opt-in using `RunInputs`; without it the preceding
always-ready experiments remain available. The fixture defaults to unknown
pin levels. A normal-run experiment supplies them explicitly:

```python
from cmc8.versions.v018 import InstructionSimulator, Memory, RunInputs, State

state = State(n=0, pg=0, ir=0)
state.registers[0] = 0
sim = InstructionSimulator(
    state, Memory(program={0: 0}),
    run_inputs=RunInputs(memr=1, halt=1, ss=1),
)
for _ in range(5):
    sim.step()  # Busy sampled at T4; original T4 PC write has not run.
assert sim.state.registers[0] == 0 and sim.state.phase == 3
sim.set_run_inputs(memr=0)
sim.resume_instruction()
assert sim.state.registers[0] == 1 and len(sim.trace) == 16
```

`set_run_inputs(memr=..., halt=..., ss=...)` changes only named pins. It also
settles HALT's asynchronous high-level clear, without advancing a timed
slot. Direct field changes are observed at the next step; unobserved pulses
between Python assignments do not create events. Pin validation and failing
slots preserve CPU/controller state and traces for retry.

Memory response delay and MEMR stimulus are separate external properties.
`Memory(program_delay=8)` delays data; it does not generate a ready pulse.
The harness or experiment must drive MEMR until the data is valid. Releasing
MEMR too early still causes the normal data-capture error. The book suggests
external pulse-generating hardware on slow memory boards; no automatic CPU
ready generator or fixed timeout has been invented.

The legacy `ready=True` argument remains the default. Raw waits are configured
through `RunInputs`, not by changing that argument. `InstructionLimit` remains
a host run guard, and `resume_instruction()` continues a paused instruction
once the inputs permit it to proceed.

New timed trace fields record `memr`, `halt_level`, `ss_level`, `resume_phase`
and `wait_reason`. `phase` records the physical model cursor at slot start;
a returning T4 can therefore be recorded as F3T4 with `resume_phase=0/1/2`.
CPU start/end snapshots precede the sequencer's final cursor update, as in
earlier versions. Use the live state after stepping for the next cursor.

## Interrupts, reset and preserved assumptions

INTR can latch during any wait, but an ordinary F3T0 is not a new instruction
boundary. The interrupted instruction finishes before acceptance at the next
ordinary F0T0. INT does not itself cancel HALT, a memory wait or an SCWR wait.
This retains the selected instruction-completion rule; a complete physical
HALT/interrupt priority circuit is not supplied by the book.

RESET is still sampled at T7. It discards the continuation and any pending
single-step grant, then executes the v017 reset cycle. It does not invent a
clear or rearm for HALT.Q or SSE. A held HALT can stop the subsequent startup
fetch; an unknown SSE still needs an explicit initial value or an SS-high
rearm opportunity.

The project's subsequent reset discussion accepted that clearing INTA while
preserving INTR is coherent: an old acknowledgement ends, while a pending
request can receive a new acknowledgement afterward. This remains the
working model, rather than an identified defect requiring additional reset
clears. Unlisted reset state and retained-IR decoder precedence remain as
documented in v017.

## Validation and remaining uncertainty

The 29 new tests include the 48-slot figure-4.16 LRS pattern, multiple/missed
ready pulses, retained access age, HALT timing and release, WAIT pin masking,
SS hold/release/rearm, unknown inputs, grant retention through memory waits,
SCWR integration, pending interrupts and reset escape.

All 239 encodings retain their ordinary results with quiet pins, execute
once under single-step, and retain their results with one wait per external
read. An additional 256 cases cover active-PC/X aliases and operand wrapping
across all pages. Quiet/disabled integration is compared with v017, and
control strobes and committed writes are checked for duplication.

The shared timing mechanism has direct source support. H022's omitted read
checks, H023's detailed SSE control and combined-controller priority retain
inferred status. Analog timing, subslot transitions, input electrical
requirements, complete opcode/control decoding and earlier EXR/DCR hypotheses
remain research limits. No external libraries are required.

Validation completed: **327 tests pass** across the full suite. All 46
generated reference artifacts are current, guide links resolve, the guide
example and 40-slot text/JSON demo run, and v017 source hashes are unchanged.
