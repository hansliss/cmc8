# Flag instructions: EIN timing and consistent extrapolation

Status: source analysis, now implemented provisionally in [v006](model-v006.md).
Earlier numbered models remain unchanged; EIN has higher timing confidence.

**Integration update:** [v016](model-v016.md) now tests request latching,
F0T0 acceptance, handler entry and EIN/RSR return together. The original
analysis below is retained; the guide also records newly exposed retained-IR
edge cases rather than treating every flag/interrupt combination as settled.

## Evidence

CMC8 sources visually inspected:

- p.62 (`Page_068.jpg`): EIN sets INTE at the beginning of T2 in F0 of the
  following instruction; that following instruction is RSR in fig.4.19.
- p.63 (`Page_069.jpg`): INTE gates /INT into INTR, which retains a request
  until the current instruction completes.
- p.64, fig.4.19 (`Page_070.jpg`): EIN is a fetch-only cycle, including
  BR→AB at T6 and phase reset at T7. In the following RSR fetch, INTE is
  set at T2; DB→IR occurs later, at T5.
- p.65, fig.4.20 (`Page_071.jpg`): INTR drives INTA's D input; INTA is
  clocked at F0T0. INTE set/reset are MOP38/39, and INTR reset is MOP46.
- p.44, fig.4.4 (`Page_050.jpg`): the control unit decodes IR into timed
  MOPs. The surrounding non-CMC8 examples are not source facts about CMC8.
- Earlier p.53 evidence establishes IR's transparent T5 window and final
  capture at its end. IR is not cleared just because a new fetch begins.

The text on p.64 says RSR re-enables INTE, while fig.4.19 explicitly
attributes the T2 enable in RSR's fetch to preceding EIN and p.62 describes
that delay. Do not infer automatic re-enabling by RSR alone from that
sentence without resolving the ambiguity.

## Mechanism that explains the diagram

This is a source-supported derivation, not a recovered silicon truth table:

1. EIN's opcode 03 enters IR during its own F0T5.
2. EIN completes its nominal one-cycle fetch at T7; IR still holds 03.
3. The next instruction's fetch starts, but IR still holds EIN through T4.
4. A decoder condition `IR == 03 and phase == F0 and timing == T2` can
   therefore assert MOP38 in that fetch, without any additional pending-EIN
   latch.
5. At the following T5, the new opcode replaces EIN in IR. That instruction
   is decoded for its own subsequent control slots.

Thus a phase labeled as fetching the next instruction can still contain a
control effect of the previous opcode. Book-level instruction-cycle
boundaries need not coincide with the last physical effect of an opcode.
A simulator must retain IR across those boundaries and permit old-IR
controls during early fetch, rather than select every MOP solely from the
new instruction's symbolic name.

An explicit deferred-effect latch could reproduce the documented behavior,
but it is unnecessary for this interpretation and is not established by
these figures. Prefer the existing IR-based mechanism under the project's
consistency principle, retaining the latch alternative if later evidence
requires it.

## Why the delay is useful

Documented: INTA samples INTR at F0T0. EIN's enable takes effect at F0T2
of the next instruction. Consequently, with interrupts initially disabled
and no previously pending request, the next instruction's T0 sampling has
already passed when INTE becomes set. A newly admitted interrupt request
can enter INTR but cannot reach INTA at that already-passed boundary.

Derived consequence: the following instruction can finish before that
new request is accepted at a subsequent F0T0. In the illustrated EIN; RSR
sequence, RSR can restore N before a newly enabled request is serviced.
This explains a practical purpose of the ordering; the book excerpt does
not explicitly state the designers' rationale. This is not a claim that
requests cannot be latched while RSR executes, nor a guarantee for every
initial INTR/INTA state.

## The three low opcode bits do help

Figure 5.1 (p.67) gives the six flag instructions. Section 1, format a,
on p.68 (`Page_074.jpg`) explicitly describes this encoding; both pages
have been visually verified.
For these opcodes, bits 7–3 are zero, bits 2–1 select the flag, and bit 0
selects clear/set:

| IR bits 2–1 | Flag | bit 0 = 0 | bit 0 = 1 |
| --- | --- | --- | --- |
| 01 | INTE | DIN 02, MOP39 | EIN 03, MOP38 |
| 10 | Link | REL 04, MOP35 | SEL 05, MOP34 |
| 11 | Z | REZ 06, MOP37 | SEZ 07, MOP36 |

A shared F0T2 decode for all six is a **consistency-supported
extrapolation**: EIN's timing is documented, the family shares its encoding
and single-cycle classification, and the same IR lifetime supports the
other controls. It remains distinct from direct evidence of each operation's
timing. Earlier T6/T7 execution for some or all other flags remains an
alternative until additional source evidence distinguishes it.

### Working timing decision

Use next-fetch F0T2 for all six flag instructions in the provisional v006 implementation:

- EIN / MOP38: timing directly documented by p.62 and fig.4.19.
- DIN / MOP39: consistency-supported extrapolation within the INTE pair.
- SEL/REL / MOP34–35 and SEZ/REZ / MOP36–37: consistency-supported
  extrapolation across the shared flag-instruction encoding.

No inspected source requires different timing for Link or Z. Unlike INTE,
these flags do not gate asynchronous interrupt requests, so EIN's practical
reason for delaying interrupt enable does not itself establish their timing.
They could be updated earlier, for example at their own T6/T7, without
changing ordinary instruction results provided the next flag consumer sees
the new value. That possibility is not affirmative evidence for a different
schedule. Prefer the uniform decoder/timing interpretation under the stated
consistency principle; retain earlier capture as an unselected alternative.

A later interrupt test should verify INTE's delayed enable, INTR latching
and F0T0 acceptance together. Merely passing a program that sets a flag
then branches on it cannot distinguish early update from next-fetch T2;
timing traces or additional source evidence are needed for that distinction.

This also supports reconsidering NOP's optional T6 BR→AB transfer: fig.4.19
shows it for a one-cycle EIN. Under the new consistency principle, retaining
it for NOP is now a stronger extrapolation than v005's chosen idle T6.
Preserve v005; record a changed choice in a subsequent numbered model.
