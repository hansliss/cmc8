# Architecture model v001

Status: first experimental datapath, not an instruction-running CPU.
Architecture: ASEA-HAFO CMC8. Sources: printed p.38, figure 4.2
(`bookpages/Page_044.jpg`), and printed p.39, figure 4.1
(`bookpages/Page_045.jpg`). Other-architecture examples are excluded.

## Read and run

Python 3.10 or later; no dependencies or virtual environment required.
From the repository root:

```sh
python3 -m cmc8
python3 -m unittest discover -s tests -v
```

Read `cmc8/versions/v001/mops.py` first, then `model.py`. The demo in
`cmc8/__main__.py` increments a register through the datapath and prints
both captures as JSON. This is a manual experiment, not a book timing trace.

```python
from cmc8.versions.v001 import Simulator, State

state = State(n=0)
state.registers[0] = 41
sim = Simulator(state)
sim.capture([18, 21, 7, 10, 12], label="R(N) + 1 into BR")
sim.capture([4, 18, 22], label="BR into R(N)")
assert sim.state.registers[0] == 42
```

## Coverage and evidence

All 50 functions are catalogued using their book numbers. Forty-four can
participate in experiments. MOP28, 29, 32, 33, 47 and 50 raise an explanatory
error: their detailed semantics need further source evidence. No interrupt,
reset, wait-state or handshake sequence is silently synthesized.

Figure 4.1's datapath storage and paths are represented, including the
register bank, IR, BR, N, AB, PG, ALU, MUX, flags and DB output control.
DI and DB are wires rather than retained registers. X selects register 7;
A is IR bits 0–2; PC is the R(N) alias. A and N can select the same storage.
AB and PG remain separate; combining their outputs into a system memory
address is left to a future memory adapter.

WAIT, INTE, INTR, INTA, SSE, phase and timing have explicit storage fields.
The PLA, automatic phase/timing counter, test input routing and external
memory devices are not implemented yet. The manual MOP set substitutes for
the control unit; phase can be explicitly written, but no automatic
advancement occurs. State values initially remain unknown, not zero.

## Explicit provisional assumptions

These are model choices, not additional facts transcribed from these pages:

- **A001 — capture boundary:** evaluate all paths from old storage, then
  capture all requested writes simultaneously. Each `capture()` is a manual
  event; it does not yet represent a full T slot, rising edge or falling edge.
  Transparent-latch windows must be added from the timing evidence.
- **A002 — combinational evaluation:** DI has no memory between evaluations.
  Gated ALU inputs are unknown unless their MOPs are present. These figures
  alone do not settle whether some real paths retain values.
- **A003 — ALU default:** with both inputs enabled, no XOR/AND/increment
  selection means eight-bit addition. Increment requires input A enabled.
  Carry is not yet connected to Link because MOP33's precise source is open.
- **A004 — MUX:** right shift inserts Link unless MOP13 selects ALU bit 0
  or MOP43 selects zero. Without shift, MOP13/43 replace bit 7. These
  combinations need checking against the instruction examples and prose.
- **A005 — flags and selectors:** register selection uses pre-capture N/IR;
  N wraps modulo eight. PC clear uses pre-capture R(N), including when N
  is cleared in the same experiment. Flag set/reset MOPs capture directly.
- **A006 — conflicts:** multiple enabled drivers, selectors or write sources
  are rejected, even if values agree. This is a conservative diagnostic,
  not proof that the original circuit forbids each combination.
- **A007 — pins:** PME, SME, EDE, WRITE and DBDIR are symbolic assertions,
  not physical voltage levels or edge events. They last for the evaluation.
  No access-time, propagation-delay or electrical compatibility claim is made.

`None` denotes unknown data or an undriven wire; this version does not yet
separate those two cases or model individual unknown bits. Invalid control
experiments raise `ModelError` without committing partial writes. The public
state is intentionally easy to inspect and initialize; validate it on use.

## Version policy

`cmc8/versions/v001/` is a complete numbered model with its own MOP catalogue.
Keep it available when creating `v002`; copy the complete small package rather
than making old models inherit changing new behavior. Each new model needs
a document explaining its evidence, changed assumptions and predecessor.
Experiments must import a specific version. JSON traces embed that identity.
The top-level demo explicitly names its version; there is no moving `latest`.

Correct defects within an unreleased model while developing it. Once used as
an investigation baseline, semantic changes require a new model number.
Documentation/typo fixes can remain in place. Numbering is intended to preserve
scientific interpretations, not create a new architecture for every edit.

## Next validation milestone

Locate, visually verify and transcribe the CMC8 LRS/SRS reference sequences.
Separate held signal levels from capture events. Use them as independent
expected traces to refine capture semantics and resolve missing controls.
Current tests establish simulator invariants; they do not establish agreement
with those book timing diagrams or original silicon.
