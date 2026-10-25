# Architecture model v015: SCS and SCW

Predecessor: [v014](model-v014.md), preserved unchanged. This complete
numbered package adds **SCS**, **SCW**, STRCS control-word capture and
SCWR acknowledgement waits. All **43 figure-5.1 families / 239 encoded
variants** are now executable, with the existing documented assumptions
and the accepted working EXR latch hypothesis retained.

```sh
python3 -m cmc8 --model v015
python3 -m cmc8 --model v015 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demo sends SCS #04, sends SCW #A6 with two full acknowledgement waits,
then executes NOP. It consumes 72 subdivisions (24+40+8), finishing at
PG=1, PC=25, external control latch=A6, with two strobe events. Values here
are hexadecimal.

## Sources and confidence

| Material | Interpretation |
| --- | --- |
| Figure 5.1, p.67 | SCS=09 and SCW=08, both two bytes / three base cycles; SCW adds waits; no flags |
| Figures6.14/6.15, pp.97–98 | Example external latch clocks from STRCS; SCS continues, SCW awaits active-low SCWR |
| Figure6.17 and later prose, p.100 | Full functional SCW sequence: strobe F1T6, acknowledgement sample F2T4, release PME F2T6 |
| Figure6.18, p.101 | Corroborates strobe/enable timing and an example with two eight-slot waits |
| P.56 general wait mechanism | Precedent for phase3 with ordinary instruction micro-operations suppressed |

Scans: [p.97](../bookpages/Page_103.jpg), [p.98](../bookpages/Page_104.jpg),
[p.99](../bookpages/Page_105.jpg), [p.100](../bookpages/Page_106.jpg),
[p.101](../bookpages/Page_107.jpg), [p.56](../bookpages/Page_062.jpg).
The [instruction reference](instruction-set.md) preserves the source table
and the derived complete controls separately.

SCW's functional timing has strong direct support. Complete held controls,
the explicit F3 realization of SCWR waits (H021), and the SCS schedule
obtained by removing acknowledgement sampling (H020) remain reconstructed.
The later PIO/other-architecture examples on p.101 are not CMC8 circuit evidence.

## E008: conflicting phase labels

One p.100 paragraph places PME rise at F2T2 and strobe at F2T6. Both the
functional table and figure6.18 instead show **PME rise F1T2 and STRCS
F1T6**, as does the later prose on the same page. v015 selects those F1
labels as correction E008, now accepted by the project owner as a typo.
The literal wording is retained.
The separate, correct **PME fall F2T6** remains unchanged.

## Control-byte path

The second byte is not sent through BR by the CPU. Program memory itself
drives it onto DB while the CPU asserts STRCS. External hardware can use
that byte in any suitable way. Figure 6.14 illustrates a latch as one
possible receiver; such a latch is not a required part of the system.
No EDE, WRITE or CPU DBDIR output is asserted. This interface is separate
from the LRD/SRD device-register harness.

| Slot | Operation |
| --- | --- |
| F0 | Common opcode fetch; PC increments; AB preloads the second-byte address |
| F1T0–T1 | PC→DI, already points to control byte |
| F1T2 | PME asserted |
| F1T3 | DI+1→BR |
| F1T4 | BR→R(N), advancing PC past both bytes |
| F1T5 | Keep PME; no DB→BR capture |
| F1T6 | STRCS high with control byte on DB; example peripheral captures it |
| F1T7–F2T3 | Keep PME and the control-byte address |
| F2T4 | SCW samples SCWR with MOP50; SCS does not sample it |
| F2T5 | Keep PME |
| F2T6 | Release PME |
| F2T7 | Reset phase |

AB retains the operand address throughout execution and waiting; BR retains
PC+2. PG and N are unchanged, and PC arithmetic wraps within the original
page. The control byte cannot replace IR or trigger a deferred flag effect,
even if its value happens to encode EIN.

STRCS has no numbered control in the supplied MOP list/table. The model
therefore uses a named `strcs` output mapped by `CONTROL_STROBES`, rather
than inventing a MOP number. Its slot-level pulse and rising capture use
the platform's functional endpoint convention. The harness requires known
data at the start of T6 and unchanged data at the end of the pulse; this
is not an analog setup/hold simulation.

## SCWR wait cycles: H021

SCWR is a **raw active-low pin level**: 0 permits continuation, 1 requests
waiting. At F2T4 MOP50 samples it into logical `state.wait`. High selects
the F3 wait controller while timing continues. After eight subdivisions,
T4 is sampled again; a low sample returns to F2 and the next slot is T5.
No instruction fetch, PC increment, strobe or register write is replayed.

Effective trace controls keep PME asserted in F3 and sample SCWR only at
T4. These describe retained memory enable and the wait controller, not a
claim that a new instruction PLA row drives ordinary data MOPs in F3.
The F3 choice follows the documented general wait mechanism; SCWR's exact
internal wiring is not supplied as a numbered circuit here.

For a high first sample and a low next sample, entry at F2T4 is followed
by F3T5, T6, T7, T0, T1, T2, T3, then the next T4 sample. The trace labels
that latter sample F3T4; after it, the controller returns to F2T5. Phase/
timing cursor changes occur after the slot's CPU capture observations,
consistent with existing end-of-cycle advancement conventions.

With N wait cycles, the instruction consumes **24+8N subdivisions**. The
book's two-wait example therefore takes 40. A low pulse entirely between
sample points does not become a queued acknowledgement. The selected model
needs a known level at each sampling boundary; unknown is an error that
leaves that slot uncommitted, not an invented high or low.

`SlotTrace.waiting` and `state.wait` describe the logical wait condition.
They do not simulate the detailed active-low /WAIT pin pulses, which the
book shows separately, including its behavior during T4.

## External harness and bounded execution

```python
from cmc8.versions.v015 import ControlPort, InstructionSimulator, Memory, State

state = State(n=0, pg=1)
state.registers[0] = 0x20
port = ControlPort(ack_after=20)
sim = InstructionSimulator(
    state, Memory(program={0x120: 8, 0x121: 0xA6}), control=port,
)
trace = sim.run_instruction()
assert len(trace) == 40
assert port.value == 0xA6
assert len(port.strobes) == 1
```

`ControlPort` is an example peripheral harness based on figure 6.14’s
latch, with an optional test response. It does not require a real system to
contain that latch and is not another CPU register. `value` persists after PME falls. Each `ControlStrobe` records
absolute subdivision index, control-byte program address and captured value.
The byte can be used directly as eight outputs or decoded externally; the
model does not invent application-specific outputs.

With `ack_after`, the test peripheral drives SCWR high until the specified
number of subdivisions after the latest strobe, then low. Delay 20 produces
samples at relative indices20(high), 28(high), 36(low), following strobe14.
This deterministic response is harness behavior, not automatic CPU acknowledgement.

Alternatively use `ControlPort(scwr=1)` and change `port.scwr` between
`step()` calls. The default is unknown. SCS completes even with an unknown
or high input, because it never samples SCWR. `Memory.devices` is untouched.

An unacknowledged SCW can wait indefinitely in hardware. To keep research
runs bounded, `run_instruction(max_slots=1024)` raises `InstructionLimit`
if the host budget is exhausted, preserving all completed slots. This is
**not a hardware timeout or completion**. Drive the input and call
`resume_instruction()` to continue without restarting fetch or strobe:

```python
from cmc8.versions.v015 import (
    ControlPort, InstructionLimit, InstructionSimulator, Memory, State,
)

state = State(n=0, pg=1)
state.registers[0] = 0x20
port = ControlPort(scwr=1)
sim = InstructionSimulator(
    state, Memory(program={0x120: 8, 0x121: 0xA6}), control=port,
)
try:
    sim.run_instruction(max_slots=28)
except InstructionLimit:
    port.scwr = 0
    sim.resume_instruction()
```

The same resume method supports a partial instruction after manual stepping
or a recoverable data error. CPU/peripheral rollback remains per-slot only;
a valid external strobe committed earlier stays committed.

## Validation and scope

Tests cover all 256 control bytes, all PC selectors/pages, byte-address wrap,
unchanged registers/flags/EXR latch, SCS ignoring SCWR, immediate and delayed
acknowledgement, eight-slot quantization, the exact two-wait waveform landmarks,
missed between-sample pulses, unknown input/data, stable strobe data, one-time
capture, host-budget resumption, repeated commands and actual next fetch.
Every one of the 237 previously supported opcode bytes retains v014 trace
and memory behavior apart from version and new handshake metadata.

The instruction repertoire is now complete at the research-model level.
It retains the accepted EXR latch hypothesis, inferred timings and DCR
uncertainty. Full interrupt acceptance, reset sequencing, generic MEMR waits,
HALT and single-step remain future work. `ready=True` is still required for
ordinary memory accesses; implementing SCWR waits does not silently implement
those other wait sources or the complete electrical pin behavior.

Validation: **246 tests pass** across the versioned suite. The 46 generated
reference artifacts are current, local documentation links resolve, and
v014 source-package hashes remain unchanged. The JSON demo has 72 slots,
two strobe events and two SCWR waits; both documented Python examples run.
