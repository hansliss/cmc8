# Architecture model v014: provisional EXR

Predecessor: [v013](model-v013.md), preserved unchanged. This complete
numbered package executes **EXR**, but with a material architecture
hypothesis: an **undocumented ALU input holding latch**. Its confidence is
lower than the recent instructions whose transfer paths were already present.
Successful execution does not establish that latch in the original CMC8.

**Project decision:** the project owner accepts H019 as the working EXR
architecture. This is an agreed research baseline, not a promotion to
documented historical fact. Keep the latch explicit and revisit it if
new evidence supports a different path.

```sh
python3 -m cmc8 --model v014
python3 -m cmc8 --model v014 --json
python3 -m experiments.exchange_routes
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demo initializes R3=80 and X=A6, exchanges them to use X=80 for an
indexed storage read, then exchanges them back. Six instructions consume
112 subdivisions, ending at PG=1, PC=28, R3=80, R4=69, X=A6. Values here
are hexadecimal.

## What is documented

[Figure 5.1, p.67](../bookpages/Page_073.jpg) lists EXR as `10111RRR`, one
byte, three cycles, exchange R(A) and X, with no affected flags. It is a
register data-transfer operation, related to CPY and the load/store family.

The book-wide OCR and broader exchange/Swedish wording searches produced
no additional EXR instruction description. Manufacturing “utbyte” means
yield in those chapters, not register exchange. No dedicated EXR MOP table
was located; OCR search failure does not establish absence from the scans.

## Why an ordinary copy recipe is insufficient in the current model

[Figure 4.1](../bookpages/Page_045.jpg) has one selected register path and
one DI bus. Saving X in BR is already supported, as in AND. But writing
old X from BR into R(A) drives DI from BR; the register port cannot at the
same time read old R(A) through that DI bus into another temporary location.
Once R(A) is overwritten, its old value must already have been preserved.

The restricted experiment in `experiments/exchange_routes.py` enumerates
pure copies along R(A)→BR, X→BR, BR→R(A) and BR→X. From distinct initial
register values and an old BR value, ten token states are reachable; none
swaps the register pair. AB is a sink in this abstraction, with no return
path into DI, so it supplies no usable extra temporary.

This is only a statement about those copy paths. It does **not** prove that
no ALU algorithm can work or that the real chip must have an extra latch.
A three-XOR swap is an alternative mathematical idea, but unconditionally
using it loses the data when R(A)=X. Extra self-alias decoding and additional
ALU scheduling would introduce other assumptions; it is not silently used
as the exchange implementation.

## Selected H019: explicit ALU input holding

H019 adds an eight-bit `state.alu_a` latch, initially unknown, and two
named research control modes. These are not invented numbered MOPs or
recovered physical signals:

| Mode | Meaning |
| --- | --- |
| `alu_a_mode="di"` | Existing combinational ALU-input behavior; default |
| `alu_a_mode="capture"` | With MOP7, capture DI in the provisional input latch |
| `alu_a_mode="held"` | Supply held A instead of opening MOP7 from DI |

Other instructions do not acquire hidden holding behavior. The existing
MOP7 passthrough and ALU→BR path are used to recover held A later. The mode
map is visible as `ALU_A_MODES` in `sequences.py`; evaluations expose
`alu_a_mode` and `alu_a_value`, and full trace state exposes `alu_a`.

The full three-cycle candidate is:

| Phase/slot | Operation |
| --- | --- |
| F0 | Established one-byte opcode fetch and PC increment |
| F1T0 | X→DI |
| F1T1–T4 | X→DI→DB held |
| F1T5 | DB→BR saves old X |
| F1T6–T7 | Idle |
| F2T0 | R(A)→DI→ALU input; named capture mode saves old R(A) |
| F2T1–T3 | Idle |
| F2T4 | BR→DI→R(A), installing old X |
| F2T5 | Named held mode, ALU→BR, recovering old R(A) |
| F2T6 | BR→DI→X, completing the exchange |
| F2T7 | Reset phase |

This borrows the established X-buffer preparation and register-write slots
T4/T6. The input holding, its enable/source modes, and exact EXR slots are
**hypotheses**, not dedicated source transcriptions. The schematic does not
explicitly show this latch. A different omitted register or bus path could
explain the real exchange instead. Retain v013 as the baseline without H019
and use later numbered versions if evidence favors another architecture.

There is no external memory/device enable during execute, no second-byte
fetch, no ALU flag update and no direct instruction-level register swap.
All transfers go through explicit controls and storage captures. Z, L,
INTE, N and PG are preserved. The extra latch retains its last value but is
used only when a named mode requests it.

## Aliases and errors

The same sequence handles every selector without a special case:

- A=7 exchanges X with itself and preserves its value.
- A=N uses the PC after the one-byte fetch as R(A)'s old value. The T4
  write replaces the active PC with old X.
- N=7 makes X the active PC. Its old value includes the fetch increment;
  the T6 write installs old R(A) as the next fetch address.
- A=N=7 performs self-exchange on the already incremented PC.

Unknown X fails at F1T5. Unknown R(A) fails at the holding capture before
any exchange register write. A stale held value is never substituted.
Errors roll back only the failing slot, as in previous versions; manually
destroying held A after a committed register write is not a whole-instruction
rollback mechanism. Capture occurs once at the modeled start boundary;
end observations do not recapture the latch.

## Validation and remaining work

Tests exercise every byte with several equal, unequal and complement
partners; all register/PC/X aliases and pages; PC wrap; every flag combination;
self-exchange; two exchanges restoring data; explicit capture/hold timing;
unknown-data rollback; actual next fetches after PC exchange; and indexed
load integration. Mode/source conflicts are rejected. The pure-copy search
and XOR self-alias example remain reproducible research checks.

All 229 previously supported opcode bytes retain v013 traces and memory
effects apart from version identity and the new latch state/metadata.

The catalogue now has **41 of 43 executable families / 237 opcode bytes**,
**including provisional EXR H019**. SCS and SCW remain unimplemented.
The EXR latch hypothesis is a new uncertainty; it does not change the status
of earlier timing assumptions, DCR's detector, or interrupt/reset/wait/
single-step work.

Validation: **222 tests pass** across the versioned suite. The 46 generated
reference artifacts are current, local documentation links resolve, and
v013 source-package hashes remain unchanged. Text and JSON demonstrations
finish after the expected 112 slots. These checks validate H019's internal
consistency, not its historical correctness.
