# Architecture model v011: AND, INR and DCR

Predecessor: [v010](model-v010.md), preserved unchanged. This complete
numbered package adds **AND**, **INR** and **DCR**, all three-cycle
instructions. It implements MOP32's ALU zero detector and an explicitly
provisional input for the omitted DCR detector. No extra libraries.

```sh
python3 -m cmc8 --model v011
python3 -m cmc8 --model v011 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demo computes F0 AND 0F → X=00, branches on Z=1, increments FF→00,
decrements 00→FF, then branches on Z=0. Nine instructions consume 160
subdivisions and finish on page 1 at PC=61, X=00, R4=FF, Z=0. Values here
are hexadecimal.

## Evidence and confidence

| Instruction / control | Evidence | Selected interpretation |
| --- | --- | --- |
| Encodings, three cycles, Z effects | Figure 5.1, p.67 | Documented |
| AND computation at F2T3, X write at T4 | Figure 5.7 and prose, p.75 | Documented functional sequence; held controls reconstructed |
| MOP32 samples ALU zero | P.75 explicitly describes ALU output sampling | Documented function, modeled capture endpoint |
| INR computation/Z at F2T3, register write at T6 | Figure 5.8, p.76 | H013 selects the table over prose F2T2 on p.75 |
| DCR complement/increment/complement | Figure 5.8 and example, p.76 | Documented arithmetic path; held controls reconstructed |
| DCR final-result zero flag | P.77 explicitly states the effect and omits its circuit/MOPs | H014 supplies a provisional DI detector at T6 |

Scans: [p.75](../bookpages/Page_081.jpg),
[p.76](../bookpages/Page_082.jpg), [p.77](../bookpages/Page_083.jpg),
[delay subroutine p.143](../bookpages/Page_149.jpg).
The [instruction reference](instruction-set.md) preserves literal source
rows separately from the executable tables and named research controls.

## MOP32 and simultaneous capture

For AND and INR, MOP32 writes Z=1 if the **ALU output** is zero, otherwise
Z=0. It examines the result produced from old operands in the same capture
as MOP12 writes BR. It does not test old BR, shifted MUX output, carry-out
or Link. L, INTE, N and PG are unaffected by these three instructions.

Evaluations expose `zero_source` and `zero_value`; JSON traces therefore
show exactly what drove the flag. A manual experiment may propagate an
unknown value to unknown Z. Instruction execution rejects unavailable ALU
or zero-test data before committing that slot, consistent with existing
DB-capture checks. Errors roll back the slot for experimental retry.

As in earlier versions, start-of-slot capture is a functional modeling
boundary, not a recovered electrical edge. End observations do not repeat
BR/register/Z capture. This matters for DCR's BR feedback: after BR changes,
the combinational ALU output can change again without another clock.

## AND: selected H012 held controls

F1 prepares X using the same X→DI→DB→BR route already selected for indexed
addressing. X drives DI at T0; DB drive begins T1 and is held through the
T5 BR capture. No external memory/device enable is asserted.

The functional figure places DI→DB at T1, while its sparse numbered row
also lists MOP23 at T0. H012 follows the functional placement and existing
indexed preparation; the literal discrepancy remains preserved.

In F2, R(A) drives DI through T3. At T3, MOP3+7+9 produce R(A) AND old BR,
MOP12 captures the result in BR, and MOP32 captures its zero predicate.
At T4, MOP4+22+20 writes BR into X. T7 resets phase. Neither F1 nor F2
increments PC; only the one-byte opcode fetch advances it.

If A=7, this ANDs X with itself. If A=N, the source is the PC after opcode
fetch. If N=7, X is also the active PC; its buffered operand is that
incremented PC and the T4 result controls the next fetch address.

## INR: selected H013

The sparse table shows R(A)→DI in F1, DI→DB at T1, then DI+1→BR and Z in
F2T3. It does **not** show DB→BR at F1T5. The model does not add that
capture: it holds the source register path across F1 and through F2T3.
DB drive is held during F1, then released at the phase boundary; DI remains
sourced from R(A).

F2T3 uses MOP10+7+12+32 along with the held register source. At T6,
MOP4+19+22 writes BR back to R(A). Full F1 and F2 execute, giving the
three cycles specified by figure 5.1 and application cycle calculations.
There is no phase skip.

The preceding prose says the Z update occurs at F2T2, while the detailed
table places the operation and MOP32 at T3. H013 follows the table and
retains T2 as the unselected source alternative. It does not claim to
resolve the historical edge from simulation.

Arithmetic wraps modulo 256: FF→00 sets Z; every other input clears it.
If A=N, fetch first increments PC and INR increments that selected register
again. A=7 simply operates on X unless N=7 also makes it the PC.

## DCR and omitted zero circuitry: selected H014

DCR captures R(A) via DI/DB into BR at F1T5. Its full F2 follows figure 5.8:

| Slot | Operation |
| --- | --- |
| T0–T2 | MOP5 drives complement of original BR onto DI |
| T3 | MOP5+10+7+12 capture complement(original)+1 into BR |
| T4–T5 | Release the arithmetic path; preserve intermediate BR |
| T6 | MOP5+19+22 write complement(intermediate BR) into R(A) |
| T7 | Reset phase |

Thus `intermediate = (~original + 1) & 255`, then
`result = ~intermediate & 255 = (original - 1) & 255`.
No direct subtraction shortcut is used.

An ordinary ALU-zero test on the intermediate result would be wrong:

| Original | Intermediate BR | Final result | Required Z |
| --- | --- | --- | --- |
| 00 | 00 | FF | 0 |
| 01 | FF | 00 | 1 |
| FF | 01 | FE | 0 |

Page 77 explicitly says the special zero circuitry and associated MOPs
were omitted. H014 models this missing function by testing **final DI at
T6**, alongside register writeback. The static DCR table adds functional
MOP32 there, with named research control `zero_source="di"` supplied by
`ZERO_SOURCES` in `sequences.py`.

Neither the T6 MOP32 assignment nor this DI input is a recovered physical
control. It is a visible model extension, not a silent instruction-level
Z assignment. Evaluations record the selected source and tested byte.
An alternative is an all-ones detector on the intermediate ALU result at
T3, which has the same final predicate but different timing. Keep that
alternative pending more evidence; a future version can select it.

## Validation and remaining work

Tests check all 65,536 AND operand pairs at the datapath level, executable
AND across every byte with several masks, every INR/DCR input and both
initial Z values, all register/PC/X aliases and pages, wraparound, exact
slot landmarks, unknown operands, unchanged memory and unrelated flags,
actual destination fetches, and both BZ polarities after all three operations.

A shortened figure-8.5-style loop executes 522 instructions / 10,432
subdivisions with the expected final counters. A separate JSR/loop/RSR
program checks return to the saved caller PC. The demo combines logical
and arithmetic Z updates with branches. Every previously supported opcode
retains v010 CPU/memory traces apart from version and new detector metadata.

The catalogue now marks **34 of 43 families / 181 opcode bytes** implemented.
Nine families remain: XRI, ANI, XOR, EXR, ROR, SHR, RRL, SCS and SCW.
INR's T2/T3 discrepancy and DCR's omitted detector remain explicit research
uncertainties. Interrupts, reset, waiting and single-step behavior retain
the earlier limitations.

Validation: **165 tests pass** across the versioned suite. The 46 generated
reference artifacts are current, local documentation links resolve, and
v010 source-package hashes remain unchanged. The CLI JSON demonstration
contains the expected 160 slots and three explicit zero-detector samples.
