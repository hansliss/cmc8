# Z-flag investigation after the logical instructions

The book supports **Z=1 for a zero computational result, Z=0 otherwise**.
It does not establish one universal capture slot or detector input for every
instruction. v012 implements the remaining Z-affecting logical families,
without changing the selected DCR detector from v011.

## Evidence checked

- [Figure 5.1, p.67](../bookpages/Page_073.jpg) identifies Z effects for
  AND, XOR, ANI, XRI, INR and DCR, as well as explicit SEZ/REZ.
- [Figure 5.7 and p.75 prose](../bookpages/Page_081.jpg) explicitly sample
  AND's ALU output at F2T3, setting Z for zero and clearing it otherwise.
- [Figure 5.8, p.76](../bookpages/Page_082.jpg) puts INR's operation and
  MOP32 at F2T3. The preceding prose says F2T2, an unresolved discrepancy.
- [P.77](../bookpages/Page_083.jpg) explicitly says DCR sets Z when the
  result is zero and omits its special circuitry and associated MOPs.
- [P.94](../bookpages/Page_100.jpg) explains ANI's mask and accumulator
  result; [p.95](../bookpages/Page_101.jpg) explicitly gives Z=0 for a
  nonzero masked result and explains BZ0's polling behavior. No internal
  flag-capture slot is supplied.
- [Figure 8.10, p.153](../bookpages/Page_159.jpg) uses XRI R7,#377 octal
  followed by zero branches in keyboard polling. This corroborates testing
  the transformed value: FF becomes zero, while other codes do not.

The general ALU/flag discussion on [p.74](../bookpages/Page_080.jpg)
contains an explicit **8080 comparison**. Its other flags and instruction
examples are not evidence for CMC8 hardware.

## Current computational model

| Family | Result | Selected Z sample | Confidence in detailed sample |
| --- | --- | --- | --- |
| AND | R(A) AND X → X | ALU zero, F2T3 | Documented functional slot |
| XOR | R(A) XOR X → X | ALU zero, F2T3 | H015, consistent operation substitution |
| ANI | R(A) AND immediate → R(A) | ALU zero, F2T3 | H016, AND timing precedent |
| XRI | R(A) XOR immediate → R(A) | ALU zero, F2T3 | H016, AND timing precedent |
| INR | R(A)+1 modulo 256 → R(A) | ALU zero, F2T3 | H013, detailed table selected over prose T2 |
| DCR | R(A)−1 modulo 256 → R(A) | Final DI zero, F2T6 | H014, provisional omitted circuitry |

For all six, the final Z predicate follows the result. For the five using
the uncomplemented ALU result, the same modeled MOP32 ALU-zero detector is
sufficient. Held controls and inferred slots retain their stated confidence.
SEZ/REZ are separate explicit flag operations, still modeled at T2 during
the following fetch; computational Z updates do not use that deferred path.

## What this says about DCR

The new logical operations require no new detector extension: they reuse
AND's ordinary ALU-zero function. This supports a simple shared detector
for the uncomplemented ALU results. It supplies **no new evidence for DCR's
chosen T6 position or physical DI input**.

DCR first computes `intermediate = (~original + 1) & 255`, then writes
`result = ~intermediate & 255`. Consequently:

| Original | Intermediate | Final | Correct Z | Ordinary intermediate-zero test |
| --- | --- | --- | --- | --- |
| 00 | 00 | FF | 0 | Wrong: would set Z |
| 01 | FF | 00 | 1 | Wrong: would clear Z |
| FF | 01 | FE | 0 | 0 |

Two detector candidates satisfy the required predicate for every byte:

- **H014, selected:** final DI equals zero at F2T6, when the register is written.
- **Unselected alternative:** intermediate ALU result equals FF at F2T3.

The book's explicit omission means the result semantics alone cannot tell
us which circuit or capture slot was used. The tests check equivalence of
these predicates without claiming both are executed or selecting one by
simulation success. v012 leaves H014 and its trace-visible research control
unchanged. An earlier flag capture would require a later numbered model
if stronger evidence favors it.

## Executable cross-checks

For all 256 input bytes, the direct DCR path agrees in final register value
and Z with this program:

```text
XRI R3, #FF
INR R3
XRI R3, #FF
```

This independently exercises the ALU-zero detector on the final complemented
result. It is a consistency check between modeled paths, not a hardware
measurement; PC advance, BR contents and intermediate flag timing differ.

Further tests execute the lamp-polling structure using ANI and the complete
keyboard press/release structure using XRI, CPY, branches, JSR and RSR.
The keyboard test explicitly uses the accepted byte
corrections E004/E005 from [the errata](errata.md); it does not silently
execute the inconsistent literal bytes. These programs verify that branches
consume the new result's flag and that polling can both repeat and exit.

See [v012](model-v012.md), [v011](model-v011.md) and the
[instruction reference](instruction-set.md) for sequences and remaining
uncertainties. No instruction-level Z assignment bypasses the modeled
detector: trace evaluations expose the tested source and byte.
