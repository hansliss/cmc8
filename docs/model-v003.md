# Architecture model v003

Predecessor: [v002](model-v002.md). Both earlier numbered packages remain
unchanged. This is a complete model package, not a subclass of a changing
predecessor. It uses only Python's standard library.

## What changed

- Added LRM and SRM using hypothesis H002: replace MOP25 (SME) with MOP24
  (PME) in the LRS and SRS sequences. All transfers and timing slots remain
  the same. Fetch and operand fetch already use PME and are unchanged.
- Both program and storage memories now contain four pages of 256 bytes,
  addressed by `(PG << 8) | AB`. This corrects v002's AB-only storage adapter.
- WRITE can target either memory space. It still commits at the falling
  edge, F2T5, and requires stable selected memory, full address and data.
- Write traces identify the memory space as well as the full address and
  value. Optional read-only program pages belong to the external harness.

There are no new datapath connections or ALU functions. PG stays unchanged
through all four instruction sequences, including when the eight-bit PC
wraps. Page-boundary arithmetic therefore wraps within the selected page.

## Try it

```sh
python3 -m cmc8 --model v003
python3 -m cmc8 --model v003 --json
python3 -m unittest discover -s tests -v
```

The demonstration runs on page 2 and fetches four instructions from program
memory: LRM R3,[280], SRM R3,[281], SRS R3,[282], LRS R4,[282]. The actual
operand bytes are 80, 81 and 82; PG supplies the upper address bits.
It leaves R3, R4, program[281] and storage[282] equal to A6. Storage[082]
remains 11, demonstrating that page 0 is distinct from page 2. Numbers in
this description and the trace display are hexadecimal.

For an individual experiment:

```python
from cmc8.versions.v003 import InstructionSimulator, Memory, State

state = State(n=0, pg=2)
state.registers[0] = 0x20
memory = Memory(program={0x220: 0x43, 0x221: 0x80, 0x280: 0xA6})
simulator = InstructionSimulator(state, memory)
trace = simulator.run_instruction()
assert simulator.state.registers[3] == 0xA6
```

Read `cmc8/versions/v003/sequences.py` for the control tables and substitution,
then `instructions.py` for the memory harness and sequencing. `model.py`
and `mops.py` preserve the complete datapath and MOP catalogue within this
version, so the model can be inspected without following implementation
inheritance across versions.

## Evidence and remaining inference

| Item | Evidence | Status |
| --- | --- | --- |
| Two 1024-byte memory spaces | pp.41–43, especially p.43, `Page_049.jpg` | Documented |
| PG supplies two page bits alongside the eight-bit base address | p.42, `Page_048.jpg`, plus fig.4.1 | Documented; shared PG+AB wiring is the model interpretation |
| LRM 01000RRR, SRM 01100RRR, three cycles, no flags | p.67, fig.5.1, `Page_073.jpg` | Documented |
| LRM R3 octal 103 and SRM R3 octal 143 | p.126, `Page_132.jpg` | Documented |
| LRM data on DB during F2T2–F2T5 | p.126 prose | Documented observation |
| Full LRM/SRM internal sequences via enable substitution | H002; LRS/SRS model, memory selection and p.126 | Derived, simulation-tested |
| MOP2 at LRS F1T5/F2T5 | I001 in the predecessor | Established project correction |
| Some program memory can be read-only | MIDAHS page 3 PROM, p.126 | Documented system example, optional harness configuration |

Successful experiments support the substitution's internal consistency;
they do not make it an independently documented transistor-level sequence.
The inherited SRS internal schedule remains derived from fig.4.13 and the
section 3.4 prose. The original LRS table, including its errors, is still
available as `PRINTED_LRS`; `interpretation="printed"` reproduces that LRS
investigation only. LRM/SRM use the corrected working model.

## Memory and trace API

`Memory.program` and `Memory.storage` are separate dictionaries, each with
addresses 0–1023. An absent byte is unknown. No automatic copying between
spaces occurs. Program writes can change subsequently fetched instructions;
this is explicitly tested. Initial fixture data can include ROM contents.
To model the MIDAHS program PROM page, construct memory with
`program_readonly_pages=frozenset({3})`. This blocks completed writes to page
3 but permits reads. By default all program pages are writable; SRM itself
is not prohibited by the CPU model.

`SlotTrace.memory_write` is either None or a `MemoryWrite` with `space`,
`address` and `value`. JSON therefore includes a record such as:

```json
{"space": "program", "address": 641, "value": 166}
```

The numbers are decimal JSON representations of address 281 and value A6.
This is a deliberate trace-schema change from v002's two-element storage
write tuple. Traces identify `v003`; old trace formats and implementations
remain available. Slot errors roll back CPU changes, trace additions and
both memories for that slot. Earlier completed slots remain committed.

## Inherited limits

The simulator still requires always-ready memory. WAIT insertion, HALT,
interrupts, reset distribution and SCWR/SSE handshakes are not implemented.
IR is sampled at the start and end of its T5 window; BR captures at its
start. Other transfers use the functional slot-start assumption described
in the v002 guide. Arbitrary transitions inside a slot, setup/hold times,
propagation delays and electrical behavior remain outside this model.

Memory delay values are ideal integer subdivisions, not nanosecond timing
specifications. The ALU/MUX assumptions from v001 are unchanged and these
instructions do not validate the other ALU functions. I/O instructions and
other instruction families remain unsupported.

## Validation

The tests exercise all four instructions for every page, every N selector
and every operand-register selector (including the PC alias). They verify
page isolation, memory-space isolation, PC wraparound, unchanged flags,
load/store round trips and instruction fetching after a program-memory
write. Paired traces check the enable substitution while keeping datapath
results and timing unchanged. Independent checks cover p.126's LRM data
window, BR/IR capture deadlines and the store-completion boundary. Read-only
memory errors and changes to the page during WRITE are checked for rollback.
