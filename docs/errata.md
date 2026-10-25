# Working errata for *Mikroprocessor i CMOS*

Project findings, not publisher-issued errata. Page numbers below are printed
book pages; links open the scans. Corrections preserve what is printed and
state the evidence for changing it. Simulation checks internal consistency;
it does not independently establish the original hardware.

“Established” means accepted as a correction for this project's working
specification. Candidate corrections and unresolved discrepancies remain
separate. Possible explanations of how an error arose are hypotheses.

## Established corrections

### E001 — Figure 4.12: MOP1 → MOP2 at LRS execution reads

**Location:** [p.54, figure 4.12](../bookpages/Page_060.jpg), F1T5 and F2T5.

**Printed:** MOP1 (DB→IR). **Correction:** MOP2 (DB→BR).

Figure 4.11's functional sequence and the accompanying explanation require
the fetched address/data to enter BR. Figure 4.2 identifies that transfer as
MOP2; MOP1 would overwrite the instruction register instead. Accepted by the
project owner in the earlier LRS investigation; applied from v002 onward.
The literal table remains in each model's `PRINTED_LRS`.

### E002 — Figure 5.6: MOP6 → MOP4 at BB0 F1T4

**Location:** [p.73, figure 5.6](../bookpages/Page_079.jpg), numbered F1T4 cell.

**Printed:** MOP6+18+24+22. **Correction:** MOP4+18+24+22.

The functional row and adjacent prose explicitly require BR→R(N), completing
the PC increment before the operand arrives at T5. MOP4 drives BR onto DI;
MOP18 selects R(N), and MOP22 writes DI into that register. MOP6 instead
loads AB and cannot supply the required DI value. Compare
[figure 4.2, p.38](../bookpages/Page_044.jpg) and
[figure 4.1, p.39](../bookpages/Page_045.jpg).

Selected in v009 and subsequently accepted by the project owner. BB1 uses
the same corrected preparation under the shared branch-circuit model. The
literal numbered row remains in `specification/book-microprograms.json`.
v009 separately inherits an always-ready MOP29 check; that addition is not
part of this printed-cell correction.

**Possible cause, suggested by the project owner:** the nearby BR output
paths in figure 4.1 may make MOP6 look like another route to DI, although
its arrow ends at AB. This is a plausible explanation, not evidence of the
author's actual reasoning.

### E003 — Figure 5.12: MOP30 → MOP31 at RRL F1T1

**Location:** [p.79, figure 5.12](../bookpages/Page_085.jpg), F1T1.

**Printed:** MOP30 beside functional 2→F. **Correction:** MOP31.

Figure 4.2 assigns 2→F to MOP31 and phase reset 0→F to MOP30.
The stated phase skip requires 31; 30 would return to fetch instead.
Selected in v013 and subsequently accepted by the project owner as a typo.
The final T7 reset still uses MOP30. The literal source row remains unchanged.
This establishes the control-number correction, not every electrical detail
of the shift or Link circuitry.

### E004 — Figure 8.10: XRI R7 byte 052 → 057

**Location:** [p.153, figure 8.10](../bookpages/Page_159.jpg), octal position 012.

**Printed:** XRI R7,#377 with opcode 052. **Correction:** opcode 057.

The routine loads the keyboard value into R7/X, then inverts it to test
through Z whether any bits are set. R7 is therefore intended; figure 5.1
encodes XRI R7 as 057, whereas 052 selects R2. The same mnemonic at position
003 correctly uses 057. Accepted by the project owner from the program context.
The existing keyboard integration test already uses 057.

### E005 — Figure 8.10: BZ0,3 byte 340 → 343

**Location:** [p.153, figure 8.10](../bookpages/Page_159.jpg), octal position 014.

**Printed:** BZ0,3 with opcode 340. **Correction:** opcode 343.

[Figure 8.9, p.152](../bookpages/Page_158.jpg) places the KEX start at
3,363 octal. The initial code on [p.150](../bookpages/Page_156.jpg) jumps
to 3,017, the byte immediately after the “Läs KB” routine in figure 8.10.
That adjacency supports, but does not by itself prove, placement of the
routine on page 3. The branch at position 005 and the explicit BZ0,3 mnemonic
at 014 independently support page 3; only the machine-code field 340
indicates page 0. Figure 5.1 encodes BZ0,3 as 343. Accepted by the project
owner as a byte-field typo. The existing keyboard integration test already
uses 343; the literal printed byte remains recorded.

### E006 — Figure 8.12: SRD R7 byte 032 → 037

**Location:** [p.155, figure 8.12](../bookpages/Page_161.jpg), octal position 052.

**Printed:** SRD R7 with opcode 032. **Correction:** opcode 037.

The program reads and increments R7, then writes that register back; the
mnemonic correctly names R7. Figure 5.1 encodes SRD R7 as 037, whereas 032
selects R2. Accepted by the project owner from the program context.

### E007 — Page 95: output-port address 001 → 00

**Location:** [p.95, “Portarnas uppbyggnad”](../bookpages/Page_101.jpg).

**Printed:** output-port address 001 in the prose. **Correction:** 00.

The input port's address 001 in the preceding paragraph is correct. Figure
6.10 on [p.94](../bookpages/Page_100.jpg) labels output 00 and input 01;
figure 6.11 on p.95 also decodes output address 00. Other port addresses
normally use two digits. Accepted by the project owner as a typo in the
output-port paragraph, not a change to the input address or CPU signaling.

All numbers in E004–E006 are octal. These four corrections change the
interpretation of application listings and prose, not the simulator's
instruction implementation. The printed fields remain recorded separately.

### E008 — Page 100: F2 labels → F1 for control-byte enable and strobe

**Location:** [p.100, paragraph above figure 6.17](../bookpages/Page_106.jpg).

**Printed:** PME rise F2T2 and strobe F2T6. **Correction:** F1T2 and F1T6
in that paragraph, as shown by figures 6.17/6.18 and the later prose.
The separate F2T6 PME fall is correct and retained. Selected in v015 and
subsequently accepted by the project owner as a typo. The source wording
remains preserved.

## Candidate comment corrections

These newly checked application-listing comments have not yet been accepted
as established project errata. The executable machine bytes are preserved.

| ID | Location | Printed | Proposed correction and evidence |
| --- | --- | --- | --- |
| E009 | [p.147, fig.8.6](../bookpages/Page_153.jpg), octal103 | `#172 (dec76)` | Decimal122: octal172 equals122, and p.144 explicitly calculates122 outer iterations for the approximately ten-second delay. |
| E010 | [p.146, fig.8.6](../bookpages/Page_152.jpg), sensor comment | T1 or T2 = 1? | T1 or T3: the two instructions are BT1,1 and BT1,3, agreeing with pp.140/143. |

## Unresolved discrepancies and notation

These should not yet be presented as straightforward typographical errors.

- **RSR phase labels:** [p.64, fig.4.19](../bookpages/Page_070.jpg) labels
  execution F1; [p.71, fig.5.4](../bookpages/Page_077.jpg) explicitly skips
  to F2. v008/v009 follow the latter account. See [RSR](instructions/RSR.md).
- **H versus inverted H:** figure 5.6 describes the taken predicate as
  H=1, whereas figure 5.5 draws H.Q-bar driving the conditional write.
  v009 stores physical Q and reports the taken predicate separately.
  This may be functional shorthand rather than an erroneous circuit.
- **INR zero-test placement:** the p.75 prose places it at F2T2, while
  figure 5.8 on p.76 places it at T3. See [INR](instructions/INR.md).
  v011 selects the detailed table's T3 placement, retaining the prose
  alternative; this is a working interpretation, not an established erratum.
- **BT “subroutine” wording:** p.106 calls test-input actions subroutine
  jumps, whereas figure 5.1 specifies branches and gives no N increment.
  The project owner's working reading is that this is likely loose language;
  BT remains an ordinary conditional branch in the model.
  See [BT0](instructions/BT0.md) and [BT1](instructions/BT1.md).

## Maintenance

Assign stable E-numbers to new entries, cite the exact scan location, and
retain the printed version. State the proposed correction, supporting
cross-reference, confidence and implementation impact. Promote a candidate
when the evidence and project decision support it; retain its identifier.
The [instruction reference](instruction-set.md) holds fuller per-instruction
evidence and the [source sequence file](../specification/book-microprograms.json)
keeps literal rows separate from executable interpretations.
