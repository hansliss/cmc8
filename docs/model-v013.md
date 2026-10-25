# Architecture model v013: ROR, SHR and RRL

Predecessor: [v012](model-v012.md), preserved unchanged. This complete
numbered package adds **ROR**, **SHR** and **RRL** as two-cycle instructions.
The datapath now supports the documented ALU-through-MUX path and Link
capture used by figure 5.12. Python's standard library remains sufficient.

```sh
python3 -m cmc8 --model v013
python3 -m cmc8 --model v013 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demo starts R3 at 81, rotates it to C0, shifts it to 60, sets Link,
then rotates through Link to B0. RRL R4 shifts 01→00 and sets Link=1;
BL1 takes the resulting branch. Nine instructions consume 128 subdivisions,
ending at PG=1, PC=41, R3=B0, R4=00, L=1, Z=0. Values here are hexadecimal.

## Source basis and confidence

| Instruction | Encoding | Bytes | Cycles | Operation | Flags |
| --- | --- | --- | --- | --- | --- |
| ROR | 10001RRR | 1 | 2 | Bit0 wraps into bit7 | None |
| SHR | 10010RRR | 1 | 2 | Zero enters bit7 | None |
| RRL | 10011RRR | 1 | 2 | Old Link enters bit7; bit0 becomes new Link | L |

Figure 5.1 documents these properties. [Page 77](../bookpages/Page_083.jpg)
and figure 5.9 describe the effects; [p.78](../bookpages/Page_084.jpg)
explains the MUX paths and master/slave Link;
[figures 5.11–5.12, p.79](../bookpages/Page_085.jpg) supply the circuit and
RRL functional/numbered table. [Page 107](../bookpages/Page_113.jpg)
corroborates serial output and input through Link.

RRL's transfer slots closely follow the printed table. Its F1T1 MOP number
uses **E003**, the MOP30→MOP31 correction now accepted by the project owner. ROR/SHR detailed
slots are **H018, likely consistency-supported extrapolations** from RRL.
No dedicated complete ROR/SHR tables were located. Electrical latch edges
within each slot remain outside the endpoint model.

## ALU path and shift-in controls: H017

Figure 5.12 asserts MOP7 at F2T2 without enabling ALU input B or selecting
increment/AND/XOR. Its functional transfer requires DI to pass through the
ALU to the shift MUX. v013 therefore models **MOP7 alone as ALU passthrough**.
It does not add stale BR to DI. The pre-existing provisional addition
behavior when both ALU inputs are explicitly enabled remains unchanged.
This realizes the documented transfer, without claiming recovered internal
ALU gate coding.

MOP11 shifts ALU output right. Exactly one high-bit source is selected:

| Control | Shifted-in bit7 | Link write |
| --- | --- | --- |
| MOP13 | Original ALU bit0 | None |
| MOP43 | 0 | None |
| MOP57 | 0, as labeled in figure 5.11 | None |
| MOP33 | Old Link | Original ALU bit0 → Link |

MOP43 from the original figure-4.2 list remains the selected SHR control.
The later circuit labels its zero-insertion gate 57. The model retains
both numbers as functional aliases, not proven identical physical signals.
Page 78 explicitly says the drawn gates are only a principle and that
actual controls are partly coded. No MOP56 is invented to fill the gap.

Earlier models provisionally used Link as an implicit shifted-in source.
v013 requires an explicit source: an unspecified or unknown source yields
unknown MUX data rather than silently choosing Link. ROR/SHR work when
Link is unknown, preserving its unknown value; RRL requires known Link for
a fully known byte result. Prior numbered packages retain their old behavior.

Evaluations expose `shift_in` and `link_input`. At RRL capture, the MUX
reads old Link while MOP33 records original ALU bit0 as new Link. Both
writes commit simultaneously, consistent with the master/slave description.
The end observation may see the new Link on the combinational path, but
does not capture BR or Link again.

## RRL sequence and E003

The common opcode fetch increments PC once. Execute runs:

| Actual slot | Operation |
| --- | --- |
| F1T0 | MOP19+21: R(A)→DI |
| F1T1 | Hold source, drive DB with MOP23; MOP31 sets phase 2 |
| F2T2 | MOP19+21+7+11+12+33: shift through old Link into BR; capture new Link |
| F2T3–T4 | Idle |
| F2T5 | MOP4 drives BR→DI |
| F2T6 | MOP19+22+4 writes DI into R(A) |
| F2T7 | MOP30 resets phase |

Timing continues across the phase write: the next slot after F1T1 is
F2T2, not F2T0. Figure 5.12 prints **MOP30** at F1T1 beside functional
“2→F”. Figure 4.2 assigns that function to **MOP31**, and MOP30 would reset
rather than skip. E003 selects 31, keeping 30 at the final reset as printed.
The literal numbered source row remains unchanged in
`specification/book-microprograms.json`; it is not silently corrected or
advertised as an executable alternative.

RRL does not capture DB into BR at F1T5 or read an operand byte. The
apparently unused DB drive at F1T1 is retained from the source table.
There is no external memory/device enable during execute and no Z update.

## ROR and SHR: H018

Use the same schedule, replacing only MOP33 at F2T2 with MOP13 for ROR or
MOP43 for SHR. This produces the documented high-bit behavior while removing
the Link write. Neither instruction affects Z, including when the shifted
result becomes zero. Other flags, N and PG are unchanged for all three.

A=7 selects X normally. If A=N, the operand is the PC after fetch, and the
T6 result replaces the active PC. Its next fetch therefore follows that
result on the same page; there is no special exception for register aliases.

## Validation and remaining work

Tests cover every byte, both incoming Link values and both initial Z values;
all register/PC/X aliases and pages; PC wrap and actual destination fetches;
ALU passthrough despite stale BR; source conflicts and unknown data; the
exact phase skip; Link capture at T2; writeback at T6; and unchanged memory.
Both BL polarities consume shifted-out Link. SEL/REL followed by RRL exercise
the existing deferred flag timing: the flag takes effect during RRL's fetch,
then RRL consumes it and captures its outgoing bit during execute.

For every byte and Link state, eight RRLs emit the original byte's bits
LSB first, as p.107 describes, and nine rotations restore the full nine-bit
register-plus-Link state. Additional tests reconstruct serial bytes using
TEST→BT→SEL/REL→RRL programs, preserving the selected TEST sampling model.
These are logical Link observations, not an electrical LOUT pin simulator.
SHR/BB0 programs also reproduce the bit-classification structure on p.154.

All 205 previously supported opcode bytes are compared with v012 for
identical traces and memory effects apart from version identity and the new
shift metadata. No old instruction schedule or DCR detector choice changes.

The catalogue now marks **40 of 43 families / 229 opcode bytes** implemented.
Only **EXR, SCS and SCW** remain. ROR/SHR inferred timing, partial physical control coding, and earlier interrupt/reset/wait/
single-step uncertainties remain explicit.

Validation: **204 tests pass** across the versioned suite. The 46 generated
reference artifacts are current, local documentation links resolve, and
v012 source-package hashes remain unchanged. Both text and JSON demos
finish after the expected 128 slots with the stated register and flag values.
