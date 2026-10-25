# Architecture model v012: XRI, ANI and XOR

Predecessor: [v011](model-v011.md), preserved unchanged. This complete
numbered package adds **XRI**, **ANI** and **XOR**, finishing the
computational Z-affecting instruction families in figure 5.1. The existing
ALU and MOP32 detector suffice; no new detector or datapath input is added.

```sh
python3 -m cmc8 --model v012
python3 -m cmc8 --model v012 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demo transforms FF XOR FF to zero in R3, branches, masks F7 AND 08 to
zero in R4, then XORs equal R5/X values into X=0. Nine instructions consume
160 subdivisions, ending at PG=1, PC=4A, R3=0, R4=0, X=0, Z=1. Values here
are hexadecimal.

## Evidence and confidence

| Instruction | Encoding | Bytes | Cycles | Result | Flags |
| --- | --- | --- | --- | --- | --- |
| XRI | 00101RRR | 2 | 3 | R(A) XOR immediate → R(A) | Z |
| ANI | 00110RRR | 2 | 3 | R(A) AND immediate → R(A) | Z |
| XOR | 10101RRR | 1 | 3 | R(A) XOR X → X | Z |

Figure 5.1 supplies the encodings, cycles, operations and Z column.
[Page 94](../bookpages/Page_100.jpg) and [page 95](../bookpages/Page_101.jpg) corroborate ANI's accumulator
result and result-based flag. [Figure 8.10, p.153](../bookpages/Page_159.jpg)
corroborates XRI R7's transformed value and zero branches in keyboard polling.
No dedicated complete MOP table for these three instructions was located.
Their detailed sequences are **likely / consistency-supported
extrapolations**, not promoted by successful simulation.

The [Z-flag investigation](zero-flag.md) records the evidence, distinguishes
the other-architecture material on p.74, and reassesses DCR. The new source
observations strengthen final-result Z semantics, **not DCR's particular
T6 detector choice**. H014 remains unchanged and provisional.

## XOR: selected H015

Reuse AND's complete selected sequence, substituting MOP8 for MOP9 and
changing nothing else. Figure 5.1 gives both instructions the same operands,
result destination, cycle count and affected flag. This is a direct use
of the project's consistency principle.

F1 captures X through DI/DB into BR at T5. In F2, R(A) drives DI through T3;
MOP3+7+8 compute XOR, MOP12 captures the result in BR and MOP32 samples ALU
zero. MOP4+22+20 writes BR to X at T4. T7 resets phase. No external memory
is enabled during execute, and there is no operand-byte fetch.

A=7 computes X XOR X, giving X=0 and Z=1. A=N reads the post-fetch PC.
N=7 makes X the active PC, so result writeback also determines the next
fetch address. These effects come from the existing register alias model.

## XRI and ANI: selected H016

The common F0 fetch advances PC and preloads AB with the immediate's address.
F1 reuses established LRS operand fetching/incrementing, including the
inherited always-ready MOP29 check. At T5, BR receives the immediate. T6/T7
are idle: the immediate is data, not an address to preload into AB.

F2 reuses AND's ALU/Z timing, with R(A) as result destination:

| Slot | Operation |
| --- | --- |
| T0–T2 | R(A) drives DI |
| T3 | DI XOR/AND BR → ALU; MOP12 captures BR and MOP32 captures ALU-zero Z |
| T4 | MOP4+22+19 writes BR into R(A) |
| T5–T6 | Idle |
| T7 | Reset phase |

There are three full cycles, no phase skip, and no F2 memory access.
PC has advanced past both bytes before R(A) is sampled in F2. If A=N,
the logical operation therefore uses that incremented PC and replaces it
with the result at T4. PG and N are unchanged. If A=7, the result goes to X
through the ordinary R(A) selector. Other registers and L/INTE are preserved.

Z samples the ALU result once at T3. This is particularly important for
XOR: capturing into BR replaces an ALU operand, so the combinational XOR
can change afterward. The end-of-slot observation does not capture BR or
Z again. This follows the platform's explicit capture model; it does not
establish an electrical edge inside T3.

## Z evidence and DCR assessment

The lamp example explicitly says ANI's nonzero masked accumulator clears Z
and BZ0 repeats; a zero masked value exits the loop. The keyboard example
uses XRI with FF to distinguish an idle FF byte from other key values.
Both support result-based Z independently of merely reading the flag column.
Neither provides an internal microprogram or capture slot for these logical
instructions, nor a new DCR circuit.

For every byte, tests compare direct DCR against XRI #FF; INR; XRI #FF.
Both agree in final target register and Z. An all-ones test on DCR's
intermediate ALU result also agrees with its selected final-DI zero test
for every byte. These are consistency checks; they do not choose hardware
or timing. See [zero-flag.md](zero-flag.md) for counterexamples to using an
ordinary intermediate ALU-zero detector and the retained alternatives.

## Validation and remaining work

Tests check all 65,536 XOR operand pairs at datapath level, full byte ranges
with equality/zero/complement cases at instruction level, all PC/register/X
aliases and pages, wraparound, source/destination roles, exact transfer and
flag slots, unknown-data rollback, operand delay boundaries, preservation
of unrelated storage and flags, and actual next fetches after writing PC.
Both BZ polarities are exercised after every new logical family.

Complete-program tests cover lamp polling through device registers and
keyboard idle/press/release/return with JSR, CPY, XRI, branches and RSR.
The keyboard test explicitly uses the intended mnemonics with accepted
E004/E005 byte corrections, preserving the literal source listing separately.
The 181 previously supported opcode bytes retain their v011 traces and
memory effects apart from version identity.

The reference now marks **37 of 43 families / 205 opcode bytes** implemented.
Six remain: EXR, ROR, SHR, RRL, SCS and SCW. All figure-5.1 computational
Z effects are now executable, but inferred logical timing, INR's T2/T3
conflict, DCR's omitted circuit, and earlier interrupt/reset/wait/single-step
limitations remain research questions.

Validation: **183 tests pass** across the versioned suite. The 46 generated
reference artifacts are current, local documentation links resolve, and
v011 source-package hashes remain unchanged. The CLI JSON demonstration
contains the expected 160 slots and three ALU-zero samples.
