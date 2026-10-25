# Architecture model v002

Predecessor: [v001](model-v001.md), preserved without semantic changes.
Status: LRS/SRS instruction experiments with always-ready memory, 24
subdivisions per instruction. Python standard library only.

## Run and read

```sh
python3 -m cmc8 --model v002
python3 -m cmc8 --model v002 --json
python3 -m unittest discover -s tests -v
```

The demonstration loads R3 from storage address 80 and stores it at 81.
The table shows AB, PC, BR, IR, DI/DB, control assertions and capture points
for every subdivision. Numbers are hexadecimal. `??` denotes unknown or
undriven data. The JSON output includes numbered MOPs, complete state at
both endpoints, model version and interpretation choice.

Read these files in order:

1. `cmc8/versions/v002/sequences.py`: printed LRS table, explicit alternative
   interpretation, and derived SRS controls.
2. `cmc8/versions/v002/instructions.py`: subdivision stepping and external
   memory harness.
3. `cmc8/versions/v002/model.py`: datapath, copied in full from v001 and
   extended with capture endpoints and a ready-only MOP29 path.

## Evidence

All sources here concern CMC8, not Z80 or other example processors.
See [the extraction notes](../Original_book.md) for preserved observations.

| Source | What it supports |
| --- | --- |
| p.49, fig.4.9, `Page_055.jpg` | LRS address/control windows and DB capture deadlines |
| p.50, `Page_056.jpg` | LRS encoding 01010RRR; operand fetch and data-memory read |
| p.52, fig.4.10, `Page_058.jpg` | Fetch MOPs; direct BR→AB path needed for stores |
| p.53, fig.4.11, `Page_059.jpg` | Functional LRS sequence; IR latch and BR capture distinction |
| p.54, fig.4.12, `Page_060.jpg` | Full printed LRS MOP table |
| pp.54–55, fig.4.13, `Page_060.jpg`/`Page_061.jpg` | SRS external signaling; writing ends when WRITE falls |
| p.67, fig.5.1, `Page_073.jpg` | LRS=01010RRR, SRS=01110RRR, both three cycles, neither changes flags |

## Established correction to the printed MOP table

**C001:** Figure 4.12 prints MOP1 at F1T5 and F2T5. Figure 4.2 defines
MOP1 as DB→IR; MOP2 is DB→BR. Figure 4.11 and p.53 prose explicitly
specify DB→BR in both execution phases. These interpretations cannot all
be applied literally to the same model.

**Resolution (project-owner decision, 2026-10-24): I001 is established for
the working specification. F1T5 and F2T5 use MOP2; the printed MOP1s are
treated as book errors.** This is supported by the explicit transfer
description, the MOP definitions and successful execution of the sequence.
The mechanism that caused the printing error is unknown. The literal table
is retained for provenance and reproducing the investigation, not as an
equally plausible account of intended LRS behavior. The existing API names
are retained so saved experiments remain reproducible.

- `interpretation="text"` (default, choice **I001**) uses MOP2 at these two
  positions, following the explicit transfer description and prose.
- `interpretation="printed"` retains the printed MOP1s. It can be stepped
  to observe the opcode being overwritten and BR retaining the incremented
  PC instead of the operand address. It may subsequently fail on missing
  data; this alternative is intentionally not made to behave like LRS.

`PRINTED_LRS` preserves the source table separately. F0T2 also prints 24
twice; both occurrences are transcribed, and circuit evaluation treats them
as one asserted control. The prose list under fig.4.10 omits MOP29 at T4
although the diagram includes it; v002 follows the diagram.

## Timing changes from v001

The p.53 text states that IR is open throughout T5 and retains DB's value
at its end. BR captures DB at the positive clock transition from T4 to T5.
The sequencer therefore records both start and end of every subdivision.
IR can update at both endpoints; BR captures only at the start. The test
harness can deliver data during T5, exposing the different deadlines.
This models endpoint observations of transparency, not arbitrary transitions
inside T5 or a transistor-level latch.

Other transfers occur at the start of their table slot as a functional
sequencing assumption. Their complete physical latch/edge behavior remains
unresolved. Enables remain asserted for every slot in the table; they are
not treated as one-time software commands. State phase/timing identifies
the next slot after `step()`; each trace records the slot just executed.
An error rolls back that slot, not earlier completed slots of an instruction.

MOP29 is permitted only with the explicit `memory_ready=True` condition;
it sets WAIT=0. The instruction runner requires the always-ready scenario.
No wait insertion, interrupt, HALT, reset sequence or handshake is inferred.
The other five previously unresolved MOPs still raise explanatory errors.

## SRS reconstruction — derived, not a printed MOP table

The inspected pages provide SRS's external timing but not a numbered
internal table equivalent to fig.4.12. **D001** constructs one using:

- the same F0 and operand-fetch sequence as LRS;
- BR→AB at F1T6, while R(A) drives DI (the reason for MOP6 given on p.52);
- continued source-register drive during the store;
- symbolic CPU→DB enable from F1T7 through F2T5;
- SME from F2T0 through F2T5, WRITE from F2T1 through F2T4;
- a storage-memory commit on WRITE falling at F2T5, with source data
  still driven; return to F0 after F2T7.

The slot boundaries for the drawn edges are visual readings of fig.4.13;
sub-slot propagation and setup/hold margins are not established. The
internal choice of when to select R(A), duration of that selection and
use of MOP30 at F2T7 are derived choices. Alternatives remain possible.
The diagram draws DBDIR low during CPU output; our `DBDIR` name denotes
logical output-enable assertion, not a physical high voltage.

## Memory adapter assumptions

Program and storage memory are separate dictionaries. The adapter combines
PG and AB for program addresses, `(PG << 8) | AB`, and uses AB alone for
storage. This is an experiment mapping, not a reconstructed MIDAHS map or
an assertion that PG cannot participate in some other memory arrangement.
Missing data is unknown. The runner rejects it at a required capture.

Integer memory delays count subdivisions since an enable/address pair
became active. A delay of 4 reaches the end of T5 after a T2 enable; a
delay of 3 reaches its start. Equality at the sampling boundary is accepted
in this ideal adapter. This tests event ordering, not the book's strict
physical access-time bound or setup time. A 4 MHz clock is not simulated
in nanoseconds. Storage writes require stable address/data throughout
WRITE and through its falling edge, an explicit conservative adapter rule.
Memory releases DB whenever the CPU drives it.

Only 0x50–0x57 and 0x70–0x77 are decoded. Unsupported opcodes stop at F0T6.
Start at F0T0 with known N, its selected PC register and PG. No artificial
reset of unrelated registers is performed. PC arithmetic wraps within its
eight-bit register; PG is unchanged by these instruction tables.

The unresolved ALU/MUX assumptions from v001 remain in this package; these
two instructions exercise increment and transfers, not all ALU functions.
Each trace identifies `v002` and the `text` or `printed` interpretation.
Future changes to architecture semantics should become a complete v003
package, following the version policy in the v001 guide.

## Validation and remaining work

Tests compare independently written expected register-transfer landmarks
and control windows with the traces, exercise late memory data, and run
both instructions across every N/A pairing (including the PC alias), byte
boundary values, nonzero program pages and PC wraparound. A two-instruction
load/store program verifies that the second opcode is fetched from memory.
The literal printed alternative is also tested as a reproducible experiment.

This establishes the functional sequences and selected timing observations
under the documented assumptions. It does not establish complete physical
clocking, wait-state behavior or silicon conformance. Next priorities are
resolving the counter/WAIT mechanism and adding a trace viewer for comparing
alternative timing interpretations.

## Later source finding: storage paging

Inspection of printed p.43 (`Page_049.jpg`) subsequently established that
storage memory, like program memory, has four pages of 256 words. The
AB-only storage mapping above is therefore a limitation of this preserved
experimental adapter, not a faithful representation of the full CMC8 storage
address space. Correct this in the next numbered model.
