# Architecture model v010: LRI and CPY

Predecessor: [v009](model-v009.md), preserved unchanged. This complete
numbered package adds **LRI** and **CPY** through MOP tables and the existing
datapath. No new datapath components or instruction-level register shortcuts
are needed. Python's standard library remains sufficient.

```sh
python3 -m cmc8 --model v010
python3 -m cmc8 --model v010 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demo executes LRI R3,#80; CPY R3; LSX R4; LRI R5,#A6; SSX R5; NOP,
using page 1. It initializes X through CPY, reads storage[180]=69 into R4,
then replaces that cell with A6. It finishes after 104 subdivisions with
PC=28, X=80 and R4=69. Values here are hexadecimal.

## Evidence and status

| Instruction | Encoding | Bytes | Cycles | Flags |
| --- | --- | --- | --- | --- |
| LRI | 00100RRR | 2 | 2 | None |
| CPY | 00111RRR | 1 | 2 | None |

These properties come from [figure 5.1, p.67](../bookpages/Page_073.jpg).
[Page 68, format c](../bookpages/Page_074.jpg) explicitly identifies LRI's
second byte as immediate data. [Figure 8.10, p.153](../bookpages/Page_159.jpg)
corroborates CPY R6→R7 in both its flowchart and listing.

No complete dedicated MOP table for either instruction has been located.
Their executable schedules are **likely / consistency-supported
extrapolations**, H010 and H011. They follow established operand fetching,
buffered register transfers and the selected two-cycle phase-skip convention.
Tests establish consistency with these premises, not original silicon timing.
The source scans and reviewed comments remain in the
[LRI](instructions/LRI.md) and [CPY](instructions/CPY.md) catalogue entries.

## LRI: selected H010

F0 fetches the opcode, increments PC and preloads AB with the immediate
byte's address. The execute cycle runs:

| Actual slot | Controls / operation |
| --- | --- |
| F1T0 | MOP18+21: PC→DI |
| F1T1 | Hold PC source; MOP31 sets phase 2 without restarting timing |
| F2T2 | Hold PC source; PME asserted |
| F2T3 | DI+1→BR, keeping the operand read enabled |
| F2T4 | BR→R(N), advancing PC past the immediate; inherited always-ready check |
| F2T5 | DB→BR, capturing immediate data |
| F2T6 | MOP4+19+22: BR→DI→R(A); memory enable released |
| F2T7 | MOP30 returns to F0 |

This reuses the LRS operand-fetch controls, including the provisional
always-ready MOP29 at T4. T6 writes the immediate into R(A), rather than
loading it into AB for a third-cycle access. There is no second memory
dereference. Operand fetching wraps within the original page; PG and N
are unchanged.

When **A=N**, the PC first advances past both bytes at T4, then receives
the immediate at T6. This naturally acts as a same-page transfer of control
through the normal register alias. No special branch semantics are added.
A=7 initializes X, including the case where N=7 also makes X the active PC.
Loading zero does not update Z; the figure-5.1 flag column is blank.

An ordinary full F1 execute cycle could perform the same transfers in
16 total subdivisions without MOP31. It remains an unselected alternative;
F2 slot labels and the selected ready-check position are not independently
established LRI timing facts.

## CPY: selected H011

The selected JCR route already transfers a source register through DI/DB
into BR in two cycles. CPY uses that route with **X rather than R(N)** as
the destination:

| Actual slot | Controls / operation |
| --- | --- |
| F1T0 | MOP19+21: R(A)→DI |
| F1T1 | Hold source, drive DB with MOP23, and skip phase with MOP31 |
| F2T2–T4 | Hold source and CPU-driven DB |
| F2T5 | MOP2 captures that DB in BR |
| F2T6 | MOP4+20+22: BR→DI→X |
| F2T7 | Reset phase |

No PME, SME or EDE is asserted during execute, and there is no operand-byte
fetch. The buffer separates reading R(A) from writing X; simultaneous
source and destination selection on the single register port is unnecessary.
IR retains the CPY opcode, and all flags, N and PG are unchanged.

Aliasing follows the normal register bank:

- **A=7:** X copies itself after the fetch.
- **A=N:** the source is the PC already incremented past CPY's one byte.
- **N=7:** writing X replaces the active PC; the next fetch uses that value.
- **A=N=7:** the already incremented PC is copied back to itself.

Earlier buffer capture or execution entirely within F1 could also fit the
visible semantics and cycle count. These remain unselected alternatives,
consistent with the uncertainty already recorded for JCR's buffered route.

## Validation and remaining work

Tests exercise all 256 immediate values; all 256 CPY source values for every
source selector; all PC/source/destination aliases; all four pages; PC wrap;
actual next fetches after writes to the active PC; unchanged flags and memory;
unknown-source rollback; and delayed/missing data. LRI data that happens to
encode EIN remains data and cannot trigger a deferred flag action.

Every one of v009's 141 supported opcode bytes is compared against v010
for identical CPU/memory traces apart from version identity. Complete-program
tests use the new instructions to initialize X and perform indexed reads
and writes. All earlier numbered packages are retained.

The reference now marks **31 of 43 families / 157 opcode bytes** implemented.
The remaining twelve families are XRI, ANI, INR, DCR, XOR, AND, EXR, ROR,
SHR, RRL, SCS and SCW. Interrupt handling, reset sequencing, wait/HALT and
single-step behavior retain their earlier limitations. No assumptions about
TEST input bias or sampling were changed by this version.

Validation: **146 tests pass** across the complete versioned suite. The
46 generated reference artifacts are current, local documentation links
resolve, and the v009 source-package hashes remain unchanged.
