# Architecture model v004

Predecessor: [v003](model-v003.md). Earlier numbered models remain unchanged.
This complete package adds LRD/SRD and simple external-device registers,
using Python's standard library.

## Evidence and model change

The project owner's proposal H003 is implemented as LRS/SRS with MOP26
(EDE) replacing MOP25 (SME). Instruction and operand fetch still use PME.
No CPU handshake or extra subdivision is added. The load still captures BR
at the start of F2T5; the store retains DBDIR and WRITE timing from SRS.

| Source | Observation |
| --- | --- |
| p.43, `Page_049.jpg` | I/O uses only the eight-bit base address, unlike the paged memories |
| p.67, fig.5.1, `Page_073.jpg` | LRD=00010RRR, SRD=00011RRR, both three cycles, no flags |
| p.95, fig.6.11, `Page_101.jpg` | Address decode, EDE and WRITE control an output latch |
| p.96, fig.6.13, `Page_102.jpg` | Address decode, EDE and physical DBDIR high enable an input; outputs are tristated otherwise |
| p.97, fig.6.14, `Page_103.jpg` | SCW/SCS are separate control instructions using STRCS |
| pp.112–113, fig.7.5, `Page_118.jpg`–`Page_119.jpg` | Bidirectional register behaves like a memory word enabled by EDE instead of PME/SME |
| p.126, `Page_132.jpg` | LRD R3 and SRD R3 examples use octal 023 and 033 |

The external interface analogy is explicit in the book. The complete
numbered LRD/SRD control tables remain derived from that description and
the working LRS/SRS sequences; these inspected pages do not supply a full
LRD/SRD MOP table.

## Run the demonstration

```sh
python3 -m cmc8 --model v004
python3 -m cmc8 --model v004 --json
python3 -m unittest discover -s tests -v
```

On program page 3, the demonstration runs LRD R3,[05], SRD R3,[04], then
LRD R4,[04]. Both registers and device 04 end up containing A6. Storage[304]
remains 11. All these numbers are hexadecimal. The 72-subdivision trace
shows EDE, data direction, WRITE and register capture points.

```python
from cmc8.versions.v004 import InstructionSimulator, Memory, State

state = State(n=0, pg=3)
state.registers[0] = 0x20
memory = Memory(program={0x320: 0x13, 0x321: 0x05}, devices={5: 0xA6})
simulator = InstructionSimulator(state, memory)
simulator.run_instruction()
assert simulator.state.registers[3] == 0xA6
```

Read `cmc8/versions/v004/sequences.py` for the enable substitution and
`instructions.py` for the external-bus adapter. This version keeps the
complete datapath and MOP definitions locally, following the version policy.

## Device-harness assumptions

`Memory.devices` holds bidirectional byte registers at addresses 0–255.
The name `Memory` is retained for API continuity; the harness now contains
three distinct address spaces. I/O address selection uses AB alone, even
if PG is unknown during the I/O phase. Program fetching still needs PG.
Program/storage addressing remains PG+AB. Multiple simultaneous space
enables are rejected.

An enabled input supplies its stored byte while the CPU is receiving;
missing registers read as unknown. `device_delay` optionally delays input
data by an integer number of subdivisions. When the CPU drives DB, the
external harness releases it. In logical traces `DBDIR` means CPU-output
assertion, corresponding to the physical low level; its absence permits
input, matching p.96's high physical DBDIR.

For a stable output transfer, the harness records the byte in `devices` at
WRITE falling, F2T5. This is an explicit **adapter assumption**, not a claim
that every peripheral captures on that edge. The book's latch examples gate
EDE, address decode and WRITE; a specific latch's transparency or edge
behavior needs its own device model. A trace's `memory_write` can now have
`space="devices"` and an eight-bit address. Writes to nonexistent output
registers create them in this ideal harness.

These registers have no read side effects, independent external inputs,
output callbacks or device-specific handshakes. They illustrate the
bidirectional register of fig.7.5 rather than reproduce all MIDAHS ports.
Port input/output direction is determined by the CPU bus controls. A future
peripheral adapter may implement distinct input and output behavior at the
same address without changing the CPU's instruction sequence.

As before, slot errors roll back CPU/trace changes and now all three
address spaces. Previously completed slots remain committed. Wait cycles,
HALT, interrupts, reset sequencing, SCW/SCS/STRCS and SCWR/SSE handshakes
remain unimplemented. Existing timing, ALU and electrical limitations from
v003 remain in force.

## Validation

All six direct-address instruction families are tested on every page and
N/A register pairing, including selecting the PC as source or destination.
Paired traces verify the EDE substitution and unchanged transfers. Tests
cover memory/device isolation, page-independent I/O, bidirectional-register
round trips, control windows, late/missing input data and rollback. The
four preexisting instruction families are also compared with preserved
v003 state and control traces. These tests establish consistency under the
adapter assumptions, not verified behavior of every possible peripheral.
