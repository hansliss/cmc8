# Architecture model v009: conditional branches

Predecessor: [v008](model-v008.md), preserved unchanged. This complete
numbered package adds **BB0, BB1, BL0, BL1, BZ0, BZ1, BT0 and BT1**, the
branch circuit from figure 5.5, and four logical test inputs. It supports
29 of the 43 families / 141 encoded opcode bytes. No additional libraries.

```sh
python3 -m cmc8 --model v009
python3 -m cmc8 --model v009 --json
python3 -m unittest discover -s tests
python3 -m tools.build_instruction_reference --check
```

The demonstration executes SEL; BL1 (taken to page 2); SEZ; BZ0
(untaken, keeps page 2); BB0 R3 (taken); BT1 T2 (taken); NOP. It consumes
96 subdivisions and finishes at N=0, PG=2, PC=81 (hex).

## Source basis and confidence

| Material | Status |
| --- | --- |
| Figure 5.1, p.67: opcodes, lengths, cycles and effects | Documented; visually rechecked |
| Figure 5.5, p.72: condition selection, XOR, H sampling and conditional write | Documented circuit; normalized model realization |
| Figure 5.6 and p.73 prose: BB0 sequence | Documented functional sequence; held controls derived |
| BB1 uses BB0 controls with opposite IR bit 3 | Derived from the documented common XOR circuit |
| BL/BZ/BT complete two-cycle control tables | H008, likely consistency-supported extrapolation |
| Conditional BL/BZ MOP15 at T6 | Likely extrapolation consistent with JMP and page-branch semantics |
| Selected external test level available to H at T2 | H009, provisional; T sampling edge not specified |

Scans: [p.67](../bookpages/Page_073.jpg),
[p.72](../bookpages/Page_078.jpg), [p.73](../bookpages/Page_079.jpg),
[p.105](../bookpages/Page_111.jpg), [p.106](../bookpages/Page_112.jpg).
Source rows remain in `specification/book-microprograms.json`; the
[individual instruction entries](instruction-set.md) separate source,
interpretation and executable tables.

## Extension to the original platform

The book explicitly says the figure-4.1 simplification omits these circuits.
v009 adds physical H.Q as `state.h`, a selected test observation `state.t`,
and the numbered controls shown in figure 5.5:

| MOP | Function |
| --- | --- |
| 51 | Select Z as condition |
| 52 | Select L as condition |
| 53 | Select the test path T, using input IR[1:0] |
| 54 | Select DI bit 0 |
| 55 | Clock H during T2 |

The datapath computes **H.Q = condition XOR IR[3]**. The inverted Q output
then enables the conditional write at T6. IR[3]=0 means branch on zero;
IR[3]=1 means branch on one. Therefore physical `h=0` means **taken**.
The functional figure-5.6 row calls the taken predicate “H=1”, whereas
figure 5.5 draws Q-bar feeding the gate. The model keeps the physical value
and records the human-facing outcome as `SlotTrace.branch_taken`.

| Condition | IR[3] | H.Q | Conditional write |
| --- | --- | --- | --- |
| 0 | 0 | 0 | Taken |
| 1 | 0 | 1 | Untaken |
| 0 | 1 | 1 | Untaken |
| 1 | 1 | 0 | Taken |

H is captured once at the modeled start of T2. Later flag/register/input
changes do not alter that branch's outcome. This uses the platform's
functional capture convention; it does not establish an electrical edge
inside T2. Unknown conditions fail without committing the slot, rather
than silently choosing a path. Unknown H does not affect other instructions.

MOP22 has two sources: the static PLA controls and the conditional circuit.
The sequencer adds the conditional MOP22 at branch F2T6, leaving the static
operand-PC increment untouched. Complete branch decoding is not drawn in
figure 5.5; restricting this overlay to branch execute is an explicit
consistency assumption. A stale H does not enable writes in later NOPs or
loads. Trace `mops` includes the effective controls; catalogue tables show
static controls and explain the overlay separately.

## BB0 and BB1: three cycles

F0 is the established fetch. F1 fetches the target byte using the original
page and increments PC again through DI/ALU/BR at T3/T4. At T5, DB replaces
the incremented value in BR with the target. AB stays on the operand
address; no target-address preload is shown in figure 5.6.

The printed F1T4 row contains MOP6, but the functional row and adjacent
prose explicitly say BR→R(N). v009 selects **MOP4+18+22**, replacing 6 with
4. This was initially a source-supported working correction and has since
been accepted by the project owner as [erratum E002](errata.md#e002--figure-56-mop6--mop4-at-bb0-f1t4).
The literal printed row remains preserved.
The always-ready MOP29 check at that slot is inherited from the existing
operand-fetch model, not printed in figure 5.6.

F2T0 selects R(A) onto DI; the source is held through T2 with MOP54.
MOP55 samples its low bit at T2. T6 selects BR and R(N); H.Q-bar supplies
the write enable if taken. T7 resets phase. BB1 shares this sequence and
changes only XOR polarity through IR[3]. N, PG, L, Z and INTE are unchanged.

If A=N, the tested register is the PC **after both instruction bytes**.
This follows the documented order: the increment finishes in F1, then
R(A) is read in F2. No special alias handling is invented.

## BL/BZ/BT: selected two-cycle schedule H008

These instructions need both a fall-through PC and a buffered target,
unlike unconditional JMP. The condition path is separate from PC's DI
path, so the following schedule fits without conflicting bus drivers:

| Actual slot | Function |
| --- | --- |
| F1T0 | R(N)→DI, already points to operand byte |
| F1T1 | Hold PC source; MOP31 sets phase 2 without restarting T |
| F2T2 | PME asserted; MOP51/52/53 selects condition; MOP55 samples H |
| F2T3 | DI+1→BR while operand read remains enabled |
| F2T4 | BR→R(N), establishing fall-through PC irrespective of H |
| F2T5 | DB→BR captures target from original page |
| F2T6 | BR→DI, select R(N); conditional MOP22; conditional MOP15 for BL/BZ |
| F2T7 | Reset phase |

This reuses documented phase skip, operand increment, T2 condition capture
and T6 target write. No complete printed microprogram for these six
instructions has been located; successful simulation establishes internal
consistency, not historical timing truth. No extra ready-check control is
added to the two-cycle table; the runner remains explicitly always-ready.

BL/BZ load PP→PG only when taken. An untaken branch keeps the original
page and falls through after the operand. The page gate and exact slot are
inferred: figure 5.5 depicts MOP22, not conditional PG circuitry. The target
byte is always read before PG changes, even for untaken branches.

BT uses IR[1:0] for the test input, so it keeps the current page. BB also
keeps the current page. All eight preserve N; none introduces a call stack.
PC arithmetic wraps within the selected page, without carrying into PG.

## Test-input harness and remaining ambiguity H009

```python
from cmc8.versions.v009 import InstructionSimulator, Memory, State

state = State(n=0, pg=1)
state.registers[0] = 0x20
sim = InstructionSimulator(
    state,
    Memory(program={0x120: 0xCA, 0x121: 0x80}),  # BT1 T2, address 80
    test_inputs=(0, 0, 1, 0),
)
sim.run_instruction()  # PG=1, PC=80
```

Inputs are logical levels, not inverted electrical pin voltages. Defaults
are four unknowns. Only the selected input must be known when H samples.
For timing experiments assign `sim.test_inputs` between calls to `step()`.
MOP53 exposes the selected current mux level to H and records it in
`state.t`; the T box in figure 5.5 has no labeled clock. A synchronizer or
earlier T capture remains possible and is not simulated. Keep inputs
stable through the condition sample when using the default interpretation.

The original TEST input bias is unknown: the book does not establish
pullups, pulldowns or floating inputs. The project owner's preference is
to add pullups in a future hardware implementation for convenient use.
This is a design choice, not a historical claim. Simulator defaults remain
unknown; a pullup-equipped experiment can explicitly supply high levels
for undriven inputs, with an external low overriding them.

The opening p.106 paragraph loosely calls BT actions subroutine jumps.
Figure 5.1 specifies branches, and no BT N increment is described. The
project owner considers this likely loose language. v009 preserves
ordinary branch semantics, retaining the wording in the source record.
The subsequent Intel 8048 discussion is another architecture.

## Validation and next work

Tests cover both outcomes/polarities, all PC selectors, source and target
pages, every byte value for the BB bit test, all register/PC alias pairs,
PC wrap, every test input, physical H truth tables, T2 sampling persistence,
unknown-data rollback, operand timing and actual destination/fall-through
fetches. Existing v008 instructions retain their tables and CPU/memory
traces apart from new trace fields and version identity.

SEL/REL/SEZ/REZ followed by matching/opposite branches now verify the
selected deferred flag timing as complete programs. This raises confidence
in the model's consistency but does not turn the assumed L/Z timing into
documented silicon behavior. ALU flag updates, interrupts, WAIT and SCW/SCS
remain future work. No earlier version has been altered.

Validation of this version: **131 tests pass** across all numbered models;
the 46 generated reference artifacts are current, and local documentation
links were checked. The CLI JSON demonstration contains the expected 96
slots and taken/untaken outcomes.
