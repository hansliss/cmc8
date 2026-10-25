# Original book: partial transcription and figure notes

This file preserves material inspected from the scans. It is incomplete.
Figure interpretations below are analysis, not verbatim transcription.

## Source guidance supplied by the project owner

- The book includes examples from other architectures. Label the architecture
  of each extracted example before using it as evidence about CMC8.
- Specifically, figure 4.5 on printed page 45 describes Z80 timing, not
  CMC8 timing. This identification is supplied by the project owner; that
  page has not yet been inspected in this analysis.
- The project owner identifies the LRS and SRS timing sequences in chapter 3
  as reliable initial reference sequences. Locate and transcribe them from
  the scans, preserving their printed section/page references. Use them to
  validate the datapath simulator before extrapolating other instructions.
- Similarities inferred for other instructions remain hypotheses, even when
  based on these reference sequences.

## Printed page 38 — `bookpages/Page_044.jpg`

The text explains that R(A) and R(N) can denote the same register (for
example R3). A addresses the register using instruction-register bits 0–2;
the remaining five bits contain the instruction code sent to the control
unit. N is a separate three-bit counter used to address R(N).

### Figure 4.2: complete MOP catalogue, English transcription

| MOP | Function |
| --- | --- |
| 1 | DB → IR |
| 2 | DB → BR |
| 3 | BR → ALU input B |
| 4 | BR → DI |
| 5 | complement BR → DI |
| 6 | BR → AB |
| 7 | DI → ALU input A |
| 8 | DI XOR BR in ALU |
| 9 | DI AND BR in ALU |
| 10 | DI + 1 in ALU |
| 11 | shift one step right in MUX |
| 12 | ALU → BR via MUX |
| 13 | ALU bit 0 → BR bit 7 in MUX |
| 14 | DI → AB |
| 15 | IR bits 0–1 → PG |
| 16 | N + 1 → N |
| 17 | N - 1 → N |
| 18 | select register N |
| 19 | select register A |
| 20 | select register X |
| 21 | register → DI |
| 22 | DI → register |
| 23 | DI → DB (DBDIR) |
| 24 | PME asserted |
| 25 | SME asserted |
| 26 | EDE asserted |
| 27 | WRITE asserted |
| 28 | sample /INT |
| 29 | sample /MEMR |
| 30 | 0 → phase |
| 31 | 2 → phase |
| 32 | update Z flag |
| 33 | update Link flag |
| 34 | 1 → L |
| 35 | 0 → L |
| 36 | 1 → Z |
| 37 | 0 → Z |
| 38 | 1 → INTE |
| 39 | 0 → INTE |
| 40 | 0 → DI |
| 41 | 2 → DI |
| 42 | 0 → PG |
| 43 | 0 → MUX bit 7 |
| 44 | 0 → PC |
| 45 | 0 → N |
| 46 | 0 → INTR |
| 47 | sample /RESET |
| 48 | 0 → SSE |
| 49 | 1 → SSE |
| 50 | sample /SCWR |

Slash prefixes preserve printed signal overbars; MOP5 complements BR.
The arrows printed for MOP24–27 are rendered here as “asserted”; their
precise level/edge interpretation still needs accompanying text.

The note under the table says that the MOPs in figures 4.1 and 4.2 describe
functions and do not in every case correspond to separate signal wires on
the chip. Executable behavior and provisional interpretations are recorded
separately in `docs/model-v001.md`.

## Printed page 39 — `bookpages/Page_045.jpg`

### Figure 4.1: partial visual interpretation

The caption identifies this as a principle diagram of CMC8 and says some
MOPs have been omitted for simplicity.

Visible datapath blocks include BR, IR, N, the register bank with decoder,
DI, ALU, MUX, L, Z, AB and PG. DB is the external eight-bit data bus.
The register bank is numbered 0–7; R(N) and R(A) are selectors into it.
The X selector is marked at register 7. The address outputs are shown as
eight bits from AB and two bits from PG.

The diagram explicitly distinguishes the direct BR-to-DI path (MOP4) from
the inverted path (MOP5). ALU inputs are supplied from DI and BR, and the
ALU output returns through MUX to BR. DI also feeds AB and the DB output
driver. Register selection (MOP18–20) is separate from reading (MOP21)
and writing (MOP22).

Control blocks include PLA, FAS, TIMING and a clock-driven counter, plus
WAIT, INTE, INTR and INTA storage/control logic. MOP29 gates the MEMR
path toward WAIT. Exact clock/capture behavior and signal polarities
must be established from accompanying text and timing diagrams before
implementing these paths.

### Modeling implications — hypotheses / design choices

- Represent one register bank with multiple selectors, not distinct PC
  and operand-register storage.
- Interpret simultaneous MOPs as circuit controls; do not execute them
  as an ordered list of software assignments.
- Separate combinational propagation from state capture. These figures
  alone do not specify capture behavior for every block.
- Preserve unspecified timing and control behavior as explicit model
  assumptions, allowing alternative implementations to be compared.

## Printed pages 49–50 — `Page_055.jpg`, `Page_056.jpg`

Architecture: CMC8. Figure 4.9 shows LRS over three phases with eight
subdivisions each. AB presents PC from F0T1, PC+1 from F0T6, and the
operand address from F1T6. PME is high during T2–T5 in phases 0 and 1;
SME is high during T2–T5 in phase 2. The caption says dashed arrows mark
the data-reading points / required data-valid times. The prose identifies
end-of-T5 for instruction capture and the shorter execution-read deadline.

Page 50 prints LRS as `01010RRR`, followed by the operand address byte.
It states that F1/F2 reads allow three subdivisions after memory enable,
and gives a strict access-time requirement below 375 ns at 4 MHz.

## Printed page 52 — `Page_058.jpg`

Architecture: CMC8. Figure 4.10 gives fetch functions and numbered controls.
All control orders in a slot are simultaneous at its beginning; placement
within the drawn cell is arbitrary. Its functions are:

| Slot | Function |
| --- | --- |
| T0 | R(N) → DI |
| T1 | DI → AB |
| T2 | PME rises |
| T3 | DI+1 → BR |
| T4 | BR → R(N) |
| T5 | DB → IR |
| T6 | BR → AB; PME falls |
| T7 | blank |

Its MOP row is the same fetch row preserved below for fig.4.12 except that
T2 shows only one occurrence of MOP24. MOP29 appears at T4 in the diagram
but is omitted in the prose list below it. The prose explains that
MOP4+MOP14 could replace MOP6 when DI is free, but MOP6 is needed for stores
at F1T6. It explicitly describes fig.4.1 as a principle diagram omitting
details, and fig.4.10b as one possible solution for that architecture.

## Printed page 53 — `Page_059.jpg`

Architecture: CMC8. Figure 4.11 adds the LRS execution phases:

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | R(N)→DI | blank | PME rises | DI+1→BR | BR→R(N) | DB→BR | BR→AB; PME falls | blank |
| F2 | blank | blank | SME rises | blank | blank | DB→BR | BR→R(A); SME falls | →F0 |

The prose states that IR is a data latch open throughout T5, retaining the
value at its end. BR is an MS flip-flop triggered by the positive-going
clock transition from T4 to T5. Thus DB sampling has different deadlines
in F0 and F1/F2. F2T7 clears the phase counter, returning to F0T0.

## Printed page 54 — `Page_060.jpg`

### Figure 4.12 — literal LRS MOP transcription

Architecture: CMC8. Numbers retain the printed table, including repeated
24 at F0T2 and the printed 1s at F1T5 and F2T5.

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | 18,21 | 18,21,14 | 18,21,24,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | blank |
| F1 | 18,21 | 18,21 | 18,21,24 | 18,21,7,10,24,12 | 4,18,29,22,24 | 1,24 | 6 | blank |
| F2 | blank | blank | 25 | 25 | 29,25 | 1,25 | 4,22,19 | 30 |

**Recorded discrepancy C001:** the F1/F2 MOP1s mean DB→IR according to
fig.4.2, whereas fig.4.11 and p.53 prose specify DB→BR. Interpretation
I001 uses MOP2 at those two positions. The literal and interpreted tables
are both preserved in `cmc8/versions/v002/sequences.py`.

**Resolution, project-owner decision (2026-10-24):** I001 is established
for the working specification. Both positions mean MOP2; the printed MOP1s
are treated as book errors. The literal transcription remains unchanged
for provenance. The cause of the errors is not established.

### Section 3.4 — SRS differences (summary)

During SRS phase 2 data flows out of CMC8 and DBDIR indicates that the
processor is transmitting. SME enables storage memory earlier than during
LRS. Data must be ready before WRITE rises; writing ends when WRITE falls.
These paragraphs do not provide a numbered SRS MOP table.

## Printed page 55 — `Page_061.jpg`

Architecture: CMC8. Figure 4.13 shows the SRS timing. Visual slot-boundary
readings: PME high at F0/F1 T2–T5; SME high at F2T0–T5; WRITE high at
F2T1–T4. DBDIR is drawn low from around F1T7 to F2T6, indicating CPU output.
AB changes to the operand address at F1T6. The sloped edges do not establish
exact sub-slot propagation times. Derived internal controls are recorded
separately as D001 in `docs/model-v002.md`.

The text below fig.4.13 says reset clears N, PC (R0) and PG. The current
simulator does not implement a reset sequence; experiments initialize these
explicitly.

## Printed page 67 — `Page_073.jpg`, selected entries only

Architecture: CMC8. Figure 5.1 prints:

| Instruction | First byte | Second byte | Cycles | Flags column |
| --- | --- | --- | --- | --- |
| LRS | 01010RRR | /ADR/ | 3 | blank |
| SRS | 01110RRR | /ADR/ | 3 | blank |

Other entries on this inspected page have not been transcribed here and
are not implemented by v002.

## Printed pages 41–43 — `Page_047.jpg`–`Page_049.jpg`

Selected CMC8 observations, visually verified:

- p.41 distinguishes three address areas selected by PME, SME and EDE,
  and specifies 1024 words each for program and storage memory.
- p.42 describes eight-bit base addresses supplemented by two bits in PG,
  giving four pages of 256 words. JMP can set PG from instruction bits 0–1.
- p.43 explicitly states that **both program and storage memory** have
  four pages of 256 words each. I/O uses only the base address (256 devices).
- p.43 says LSX and LRS both take three cycles to simplify the microprogram,
  despite LSX being a one-byte instruction.

The M6800/8080 addressing examples on pp.41–42 are comparisons, not CMC8
instruction formats. The figure 4.3 memory diagram on p.43 applies to CMC8.

**New evidence against adapter assumption:** v002 intentionally uses only
AB for storage addresses. That restriction does not represent CMC8's full
storage address space, as established by p.43. Preserve v002 as the earlier
experiment; a subsequent version should support paged storage addresses.

## Printed pages 125–126 — `Page_131.jpg`, `Page_132.jpg`

Selected CMC8/MIDAHS memory-test observations, visually verified:

- p.125 proposes LRI into R3, then SRM/SRS, LRM/LRS, and JMP to repeat.
- p.126 gives parallel program/storage tests. In the program-memory test,
  SRM R3 has octal opcode 143 (hex 63), LRM R3 has octal opcode 103
  (hex 43). The storage test uses SRS R3 octal 163 (hex 73) and LRS R3
  octal 123 (hex 53).
- The text says SRM stores the value in program memory and LRM reads it
  back. For LRM it explicitly identifies DB data during **F2T2–F2T5**.
- In MIDAHS, program-memory page 3 is PROM and cannot be written.
  This is a property of that system's memory, not a ban on SRM by the CPU.

The lower I/O example on p.126 was viewed but has not been transcribed here.

### H002 — LRM/SRM memory-enable substitution

Proposed by the project owner: reuse LRS/SRS controls, substituting MOP24
(PME) for MOP25 (SME) wherever the latter occurs. F0/F1 program reads remain
unchanged. This preserves the load/store distinction in timing, DBDIR,
WRITE and transfer paths. The p.126 LRM timing observation supports this
proposal; the full internal sequences remain derived pending further
confirmation. It has not yet been implemented or tested.

**H002 implementation update:** model v003 now implements the enable
substitution and tests it alongside LRS/SRS on all four pages. Both memory
spaces now use PG+AB. This validates the derived sequences against the
simulator and the documented observations; no new book timing table was
found or inferred to exist. See `docs/model-v003.md` for the model's scope
and evidence. The earlier statement that H002 was unimplemented describes
its status when initially recorded.

## Printed pages 95–97 — `Page_101.jpg`–`Page_103.jpg`

Architecture: CMC8; example external interface circuits, visually inspected.

- p.95, fig.6.11: an output-port address decoder produces AE, which is
  ANDed with EDE and WRITE high to load the output latch from DB.
- p.96, fig.6.13: input-port reading uses AE, EDE and physical DBDIR high.
  The input requires tristate outputs to avoid driving DB when not enabled.
  Figure 6.12 illustrates simple port-address decoding; this is an example
  wiring choice, not a restriction to those addresses in the CPU.
- p.97, fig.6.14 and section 2.2.2: SCW (send control signals and wait) and
  SCS (send control signals) are separate instructions. They use STRCS to
  strobe the second instruction byte into an external latch. They are not
  extra steps automatically attached to LRD/SRD by the current model.

## Printed pages 112–113 — `Page_118.jpg`, `Page_119.jpg`

Architecture: CMC8/MIDAHS, visually inspected.

- p.112 explains that an input and an output port can share an address;
  fig.7.5 combines them into a bidirectional port.
- The register is written under AE, EDE and WRITE and read under AE, EDE
  and DBDIR. Tristate gates isolate it from DB otherwise.
- p.113 explicitly describes the register as behaving like a memory word,
  activated by EDE instead of PME or SME.
- Figure 7.5 is an external device circuit, not extra internal CPU datapath
  machinery. The text names CD4034A registers for MIDAHS ED0, ED1 and ED2.
  The present simulator uses ideal registers, not a CD4034A timing model.

### H003 — LRD/SRD enable substitution

Proposed by the project owner: reuse LRS/SRS controls with MOP26 (EDE)
instead of MOP25 (SME), retaining program-memory fetches, bus direction
and WRITE timing. The interface description on pp.95–96 and explicit
memory-word analogy on p.113 support this derivation. I/O uses AB alone,
as established on p.43. Model v004 implements and tests this proposal.
Its ideal device registers commit outputs at WRITE falling; exact
peripheral latch capture behavior is an adapter assumption, not inferred
as a universal I/O rule.

### Additional selected instruction entries

Figure 5.1 on p.67 prints LRD as `00010RRR` and SRD as `00011RRR`, each
with an address byte, three cycles and blank flags column. The lower table
on previously inspected p.126 gives LRD R3 octal 023 (hex 13) and SRD R3
octal 033 (hex 1B), with external-device addresses 003 and 004 respectively.

## Printed page 51 — `Page_057.jpg`

Architecture: CMC8, visually inspected. Section 3.2 says fetch is shared
through T0–T5. Some one-byte instructions execute directly in F0, during
T6/T7. Its LRS fetch description puts R(N) on DI at T0, DI on AB at T1,
PME high at T2, PC+1 in BR at T3, BR back into R(N) at T4 and DB into IR
during T5. The description of T6's BR→AB transfer specifically interprets
the opcode as the two-byte LRS instruction; it does not supply NOP's tail.

### Selected p.67 entry and H004 — NOP

Figure 5.1 (`Page_073.jpg`, visually rechecked) prints NOP as `00000000`,
one cycle, no operation and blank flags column.

The project owner proposes reusing fetch/increment and stripping subsequent
execution. Model v005 implements shared fetch through T5, idle T6 and
MOP30 at T7. These tail controls are a derived minimal sequence, not a
transcription. Retaining BR→AB (MOP6) at T6 is a recorded alternative with
the same architectural result but different AB timing. v005 chooses idle
T6 until further evidence distinguishes them. See `docs/model-v005.md`.

## Printed pages 62–65 — `Page_068.jpg`–`Page_071.jpg`

Architecture: CMC8 interrupt behavior; visually inspected.

- p.62 explicitly says EIN enables INTE at the beginning of F0T2 of the
  following instruction, illustrated as RSR in fig.4.19.
- p.63 describes INTE gating active-low INT into the INTR request latch.
  After completion of the current instruction, interrupt entry acknowledges
  the request, clears INTE/INTR, increments N and supplies PC with 002.
- p.64, fig.4.19: EIN's one-cycle row has the normal fetch transfers,
  including BR→AB at T6, then phase reset at T7. The following RSR fetch
  has 1→INTE at T2, before its DB→IR at T5. RSR's execution row decrements
  N at T2 and resets phase at T7. Its execution row is labeled F1 here;
  the later fig.5.4 uses a phase skip to F2, an unresolved representational
  difference to retain when implementing RSR.
- p.65, fig.4.20a: MOP38 sets INTE, MOP39 clears it; INTE gates /INT into
  INTR. INTR feeds D of INTA, clocked at F0T0; INTA feeds the PLA.
- Fig.4.20b gives interrupt-entry functions: T0 sets INTA and clears
  INTE/INTR; T1 places 02 on DI; T2 increments N; T4 writes DI into R(N);
  T7 resets the phase. No implementation has been added from this note.
- The p.64 sentence attributing re-enabling to RSR needs care: p.62 and
  fig.4.19 attribute the illustrated delayed enable to preceding EIN.

Derived explanation: IR retains EIN until the following fetch's T5, so it
can directly select MOP38 at that fetch's T2. No extra deferred-effect
latch is required by this explanation. See `docs/flag-instruction-timing.md`
for the interrupt-sampling consequence, flag encoding and extrapolations.
The reset material on these pages was viewed but not fully transcribed in
this pass; retain its scans as the source before implementing reset.

## Printed page 44 — `Page_050.jpg`

Architecture: CMC8, selected observation only. Figure 4.4 and accompanying
text describe IR decoding and time-ordered MOP generation. The bottom of
the page introduces fig.4.5 as a Z80 comparison; its timing is not CMC8
source evidence. Other background examples here are not transcribed.

## Printed page 68 — `Page_074.jpg`, format a only

Architecture: CMC8; visually verified. The text explicitly identifies the
six flag instructions as starting with five zero bits (bits 7–3). Bits 2
and 1 select the flag (INT, LINK or ZERO), and bit 0 selects whether the
flag is set or cleared. Their precise mapping is provided by fig.5.1's
opcodes and is recorded in `docs/flag-instruction-timing.md`.
Other instruction-format explanations on this page have not been fully
transcribed in this pass.

### Flag timing implementation status — v006

The six flag instructions are now implemented provisionally using the
previously recorded next-fetch T2 interpretation. EIN has directly
documented timing and higher confidence; DIN, SEL, REL, SEZ and REZ retain
"likely / consistency-supported extrapolation" status. Trace-level tests
exercise that chosen model without establishing interrupt or branch
semantics. No new source evidence was added by these tests.

Figure 4.19's EIN T6 BR→AB transfer is also used for NOP in v006 under the
consistency principle. This supersedes the selected idle-T6 NOP tail only
in the new version; v005 remains available with the earlier interpretation.

## Printed page 40 — `Page_046.jpg`, indexed-addressing observations

CMC8, visually inspected. The text identifies R7 as the index/X register,
explains LSX as load from storage addressed by X, and states that MOP20
directly selects R7. MOP18 selects by N; MOP19 selects by A (IR bits 0–2).
Other material on this page is not fully transcribed in this pass.

## Indexed entries, printed pp.43, 67–68

Visually rechecked. Page 43 explicitly explains that LSX is one byte but
still takes three cycles to simplify the microprogram, like two-byte LRS.
Figure 5.1 (p.67) lists LRX=01001RRR, LSX=01011RRR, SRX=01101RRR and
SSX=01111RRR, all three-cycle, with blank flags and second-byte columns.
LRX/SRX address program memory; LSX/SSX address storage memory through X.
Page 68, format b, explicitly uses SSX as its one-byte example and says
RRR selects R(A).

## Printed page 75 — `Page_081.jpg`, selected fig.5.7 observations

CMC8 AND example, visually inspected. Figure 5.7's functional F1 row has
X→DI at T0, DI→DB at T1 and DB→BR at T5. This is a precedent for preparing
an X operand through the CPU's external data-bus path without enabling a
memory. The printed MOP row shows 20,21,23 at T0, 23 at T1 and 2 at T5;
held gate levels are not completely spelled out there. The functional and
numbered rows differ in placement of initial DB drive, so retain that
ambiguity rather than transcribing a complete held-level schedule as fact.
The remaining AND sequence and flag behavior have not been fully decoded
in this pass. Page 79 (`Page_085.jpg`) was also viewed while looking for
indexed sequencing; its shift/rotation material remains untranscribed.

### Indexed sequencing candidates

See `docs/indexed-addressing.md` and `experiments/indexed_address_routes.py`.
Two candidates preserve the documented one-byte/three-cycle effects:
H006-A transfers X through DI/DB into BR at F1T5, then into AB at F1T6;
H006-B transfers X through DI directly to AB at F1T1. Their precise indexed
MOP timing is extrapolated. H006-A is preferred for consistency with the
AND preparation and established load/store address-transfer slot. Neither
is established as the historical indexed microprogram.

**Working selection, project-owner decision (2026-10-25):** use H006-A
(the AND-style buffer route) while evidence and tests remain consistent.
Keep H006-B (direct X→DI→AB) as the unselected backup, with its distinct
timing preserved. This selection does not promote H006-A to documented fact.

### Indexed implementation status — v007

The selected H006-A buffer route is now integrated into LRX/LSX/SRX/SSX
in model v007. H006-B remains the unselected backup. Instruction semantics,
encodings and cycle counts are documented; the selected detailed control
schedule remains likely / consistency-supported extrapolation. Integration
tests do not promote its historical timing confidence. No new source pages
were decoded for this implementation.

## Instruction-reference research and control flow — v008

The authored [instruction catalogue](specification/instructions.json) now
records all 43 figure-5.1 families. Its source registry identifies each
visually checked scan by printed page, PDF page and image. The generated
[reference](docs/instruction-set.md) links those observations, unresolved
questions, source sequences and executable model sequences separately.
Whole-book OCR matches remain search leads, not visually verified evidence.

Additional selected material visually checked in this pass includes:

- pp.67–68: repertory and formats; INR is three cycles, as also confirmed
  by the delay-program example on pp.143–144.
- pp.70–71: JMP numbered sequence and JSR/RSR functional sequences. MOP31
  changes F1 to F2 at T1 without resetting T. JSR increments N, RSR
  decrements N; no automatic PG return stack is described.
- pp.72–73: branch extensions introduce MOP51–55 and additional H state.
  Figure 5.6's F1T4 MOP6 conflicts with its BR→R(N) functional operation,
  which would require MOP4. Preserve this as a candidate correction.
- pp.75–79: AND, INR/DCR and rotations. Literal and functional rows are
  retained separately. INR's zero-test placement differs between prose
  and figure; RRL's phase-control and added zero-insertion controls also
  need interpretation. These are not silently corrected into source fact.
- pp.89–91: JMP external timing and single-step context. Figure 6.7/p.90
  explicitly places the PC write at the beginning of F2T6 and the next
  target-address transfer into AB at the following F0T1. This agrees with
  v008's retained operand address in AB at instruction completion.
- pp.93–94: device polling example and explanation of ANI's immediate
  mask operation. pp.100–101 contain SCW timing; the p.100 prose has
  conflicting F1/F2 labels, retained in the catalogue for further checking.
- pp.143–144 and 151–155: application examples corroborate several
  encodings, effects and cycles, but also contain byte/mnemonic mismatches.
  Those local discrepancies remain annotated; figure 5.1 stays the
  baseline rather than copying application bytes uncritically.

Normalized source sequence transcriptions are stored in
[book-microprograms.json](specification/book-microprograms.json). They are
sparse functional/numbered source rows, not complete held-level executable
microcode. Earlier statements above that those selected portions were
untranscribed describe the earlier pass and are superseded by these records.

## Conditional branch investigation — v009

Printed pp.67, 70, 72–73 and 105–106 were visually rechecked for this
implementation. Figure 5.5 adds MOP51–55 and H/T circuitry omitted from the
original platform. The selector outputs feed an XOR with IR bit 3 into
H.D; the **inverted Q output** gates MOP22 with T6. Thus physical H.Q=0
corresponds to a taken branch. Figure 5.6's functional “H=1” taken wording
is retained as a logical-predicate notation discrepancy, not used to invert
the instruction semantics.

The prose and functional table on p.73 explicitly finish the second PC
increment in F1 before the target enters BR at T5. The numbered F1T4 MOP6
therefore conflicts with that transfer. v009 selects MOP4 instead, retaining
18+22 and preserving the printed row separately. This is a source-supported
working correction awaiting project-owner review, unlike the previously
established LRS MOP2 correction.

BB0's full functional sequence is documented. BB1 shares the circuit with
IR bit 3 selecting opposite polarity. BL/BZ/BT detailed two-cycle controls
are H008, a consistency-supported extrapolation: phase skip at F1T1,
condition sample F2T2, PC increment T3/T4, operand capture T5, conditional
target write T6. BL/BZ also conditionally update PG at T6; that gate is not
shown in figure 5.5. Complete decoding that confines H-driven writes to
branch execute is also a model assumption, not an additional drawn wire.

Page 72 calls T a test flip-flop but gives no separate capture edge. H009
makes the currently selected logical test level available when H samples
at T2; synchronization or earlier sampling remain alternatives. The model
records the selected observation without claiming a recovered T clock.
Page 106's opening prose calls BT actions subroutine jumps, whereas figure
5.1 calls them branches and provides no N increment. v009 keeps N and PG
unchanged for BT; the terminology conflict is retained in the catalogue.
The later 8048 example on p.106 is another architecture.

See [model-v009](docs/model-v009.md) for confidence, sequences and validation.
Successful L/Z flag-plus-branch programs support internal consistency of
the selected deferred flag model; they do not independently prove its
historical timing. Interrupt handling remains unimplemented.

### Errata review: BB0 correction accepted

The project owner has now accepted the figure-5.6 F1T4 MOP6→MOP4 correction
as an obvious error. It is recorded as E002 in [the working errata](docs/errata.md),
alongside the previously accepted LRS correction E001. The proposed cause
(confusion between the BR→DI and BR→AB arrows) is recorded separately as a
hypothesis about the author, not as established provenance. Earlier notes
calling E002 a candidate describe its status before this review.

### TEST input implementation preference and terminology review

Project-owner clarification: original TEST input pullups, pulldowns or
floating behavior remain unknown. Favor pullups in a future hardware
design as a convenience, without attributing them to the original CMC8.
The research model keeps unspecified inputs unknown; biased experiments
must supply their levels explicitly. The owner reads p.106's “subroutine
jump” wording as likely loose language, consistent with retaining ordinary
BT branch semantics and unchanged N. This does not resolve T sampling timing.

## Immediate load and copy — v010

Pages 68 and 153 were visually rechecked. Page 68 format c explicitly
places LRI's immediate data in its second byte. Figure 8.10 shows CPY R6→R7
in both the flowchart and the listing (octal 076). This pass adds no newly
located complete MOP table for either instruction.

H010 realizes LRI using the selected two-cycle phase skip, the established
operand-fetch/increment path, and BR→R(A) at F2T6. H011 realizes CPY using
the existing JCR-style register/DI/DB/BR route, changing the destination
selector to X at F2T6. Both are likely consistency-supported extrapolations;
full F1 execution or different buffer capture timing remain alternatives.
See [model-v010](docs/model-v010.md) for exact controls and confidence.

Normal register aliasing gives LRI-to-R(N) and CPY-with-N=7 the effect of
replacing the active PC; the tests verify actual destination fetches. These
are consequences of the selected datapath interpretation, not newly found
explicit book descriptions of those alias cases. Earlier packages remain
unchanged. All flags are preserved, consistent with figure 5.1.

## AND, INR and DCR — v011

Printed pp.38 and 75–77 were visually rechecked. Page 75 explicitly says
AND samples the ALU output at F2T3, setting Z for zero and clearing it
otherwise. Figure 5.7 writes the buffered result into X at T4. v011 uses
that sequence with reconstructed held controls; H012 follows functional
DB drive at F1T1, retaining the sparse MOP23-at-T0 discrepancy.

Figure 5.8 does not show INR capturing DB into BR during F1. v011 holds
R(A) on DI through the full preparation phase and into F2T3, rather than
inventing an extra BR capture or shortening the instruction. H013 selects
the detailed table's T3 arithmetic/Z slot over the preceding prose's T2.
The three-cycle count remains consistent with figure 5.1 and application
examples. The earlier catalogue phrase about an INR phase skip has been
replaced: no skip is selected, since full F1/F2 fit the documented count.

DCR follows the complement/increment/complement path in figure 5.8.
Page 77 explicitly says final result zero sets Z, and that the special
circuitry and related MOPs were omitted. H014 represents that omission with
a provisional final-DI zero test at F2T6. The model adds functional MOP32
there plus a named research input selection; neither is claimed as a
recovered physical control. An intermediate ALU all-ones detector at T3
remains an unselected alternative. Ordinary ALU-zero detection would give
incorrect DCR flags for 0→255 and 1→0.

See [model-v011](docs/model-v011.md) for schedules, confidence and tests,
including exhaustive AND datapath values and complete shortened delay-loop
programs using INR/DCR, BZ, JSR and RSR. Literal source tables remain
unchanged, and v010 is preserved.

## XRI, ANI, XOR and Z reassessment — v012

Printed pp.74, 94–95 and 153 were visually rechecked, and whole-book OCR
leads for logical operations and Z were searched again. The general flag
examples on p.74 explicitly discuss the 8080; they are not imported as
CMC8 circuitry. No complete dedicated XRI/ANI/XOR MOP tables were found.

Page 95's opening paragraph explicitly connects ANI's nonzero masked
accumulator to Z=0 and a repeated BZ0 polling loop. With bit3 low, the
masked result is zero and execution continues even if other source bits
were nonzero. Figure 8.10's XRI R7,#377 and zero branches likewise support
flags based on the transformed result. These observations corroborate the
result predicate, not a specific internal capture time.

H015 implements XOR as the existing AND sequence with only MOP9→MOP8.
H016 combines established immediate fetching with AND's ALU/Z T3 and result
write T4, changing the destination to R(A). Both remain likely consistency-
supported extrapolations. All three use the existing ALU-zero detector.

The selected DCR H014 DI test at T6 is unchanged. Direct DCR and the program
XRI #FF; INR; XRI #FF agree in result and Z for all 256 bytes in simulation.
The alternative intermediate all-ones predicate at T3 is also equivalent
for every byte. This checks consistency, not original hardware; the new
evidence cannot discriminate the detector location or timing. See the
[Z-flag investigation](docs/zero-flag.md) and [v012](docs/model-v012.md).

The p.95 output-port paragraph also calls its address 01, whereas figures
6.10/6.11 label the output 00 and the input 01. This was added as candidate
erratum E007; no instruction-model behavior was changed for that mismatch.

## Right shifts and rotation through Link — v013

Printed pp.77–79, 107 and 154 were visually rechecked. Figure 5.12 provides
RRL's detailed slots: phase skip at F1T1, shift and Link capture at F2T2,
BR→DI at T5, register write T6, reset T7. E003 selects MOP31 for the printed
F1T1 MOP30, matching the adjacent 2→F function and figure 4.2. The literal
row is unchanged; this remains a source-supported working correction rather
than a project-owner-established erratum.

H017 realizes the table's MOP7-without-B/arithmetic-selector path as DI
passthrough to the ALU output. Figure 5.11's MOP33 uses old Link for the
shifted-in bit and captures original ALU bit0 as new Link. Page 78 explicitly
describes a master/slave Link and warns that the gate drawings are only a
principle, with controls partly coded in CMC8. The model's simultaneous
capture is consistent with that description, without claiming electrical
edges within T2.

The zero-insertion gate is labeled 57 in figure 5.11 but 43 in the original
MOP list. v013 retains both as functional aliases and selects 43 in SHR;
it does not assert identical physical encoding or call the difference an
established error. H018 derives ROR/SHR from RRL's schedule by replacing
MOP33 with MOP13/MOP43, preserving both Link and Z. No dedicated complete
ROR/SHR MOP tables were located.

Page 107 states that eight RRLs emit the register LSB first on LOUT and that
setting Link from a test input before each RRL supports serial reception.
Tests exercise both descriptions and the full nine-bit rotation period.
Earlier UART/SCMP discussion is other-architecture context, not adopted as
CMC8 circuitry. The p.154 SHR/BB0 command-bit classification also supplies
an executable integration precedent. See [v013](docs/model-v013.md) for
sources, confidence and validation. v012 remains unchanged.

### E003 review: RRL phase-control typo accepted

The project owner has accepted MOP30→MOP31 at figure-5.12 F1T1 as a typo.
E003 is now an established project correction in the errata and catalogue.
The literal source transcription remains unchanged. Earlier references to
pending review describe its prior status; the implemented v013 controls
already use the accepted correction.

## EXR investigation — provisional v014 H019

Figure 5.1 and figure 4.1 were visually rechecked. Figure 5.1 documents
one-byte, three-cycle exchange of R(A) and X, with no flag effect. A fresh
OCR search for EXR, exchange and Swedish exchange-related words located no
additional instruction description. Manufacturing "utbyte" references are
about yield, not the instruction. This search is not proof that no other
visual occurrence exists.

The existing single-port/DI/BR model cannot perform a swap through pure
register↔BR copy paths alone. A restricted token-state experiment records
that constraint; it does not exclude all ALU algorithms or prove original
hardware. An unconditional three-XOR swap also loses data on self-alias.

H019 adds an explicitly provisional ALU input-A holding latch: save X in BR,
hold old R(A), write BR into R(A), restore the held value through ALU→BR,
then write BR into X. The selected full F1/F2 schedule fits the documented
three cycles and handles all register/PC/X aliases. The latch, named
capture/hold modes and exact timing are not established by the book. No new
numbered MOP is attributed to this hypothesis. It has lower confidence than
a timing extrapolation that uses only already documented paths.

See [v014](docs/model-v014.md) and
`python3 -m experiments.exchange_routes` for assumptions and reproducible
checks. v013 remains unchanged as the baseline without this extra storage.

### H019 review: EXR holding latch accepted as working architecture

The project owner accepts the ALU input holding latch as the working EXR
solution, recognizing that the book deliberately omits implementation detail
and that no better-supported alternative has been identified. H019 remains
an architecture hypothesis about the original CMC8; acceptance establishes
our selected investigation baseline, not historical proof. The code and
explicit trace-visible controls are unchanged by this review.

## SCS/SCW and acknowledgement waits — v015

Printed pp.56, 58–59, 86–87 and 97–101 were visually inspected in this pass.
Figure 6.18 corroborates figure 6.17 and p.100's later prose: PME rises
F1T2, STRCS strobes the control word F1T6, SCWR is sampled F2T4, and PME
falls F2T6 after acknowledgement. The earlier paragraph's F2T2/F2T6 labels
for enable/strobe are retained as candidate erratum E008, with F1 labels
selected in v015. The genuine F2T6 memory-disable event is not changed.

The control byte is supplied directly by program memory on DB to an external
STRCS-clocked latch. No DB→BR control-byte capture or AB target preload is
shown; BR holds PC+2, AB holds the control-byte address, and PME persists
through the wait. STRCS is a named model output because the supplied MOP
list does not number it. The external latch/response harness is separate
from LRD/SRD's ED device registers.

Page 100 specifies SCWR sampling on each T3→T4 transition and complete wait
cycles. Figure 6.18's two waits add 16 subdivisions. H021 realizes these
through the existing phase3 wait concept described for MEMR on p.56,
retaining PME and suppressing ordinary instruction actions, with repeated
MOP50 sampling at T4. Effective trace controls describe held memory output
and the wait controller, not a recovered F3 instruction PLA row. The
logical wait condition is modeled; the detailed physical /WAIT waveform
and generic MEMR/HALT/single-step waits are not yet implemented.

H020 derives SCS by removing SCWR sampling from the same three-cycle
send/strobe schedule. Figure 5.1 and p.98 establish its cycle count and
send-and-continue behavior; a separate full SCS timing table was not found.
Unknown or high SCWR therefore does not prevent SCS completing.

See [v015](docs/model-v015.md) for source confidence, exact controls,
external test-peripheral API and bounded/resumable host execution. All
43 repertory families are now executable in the research model; this does
not establish every historical timing interpretation or complete CPU
interrupt/reset/external-control behavior. v014 remains unchanged.

### E008 accepted; external latch clarified

The project owner accepts E008's F2→F1 enable/strobe phase-label correction
as a typo. It is now listed among established project corrections.

Figure 6.14's latch is an example of external receiving hardware, not a
required component of every CMC8 system. The CPU presents the control byte
with STRCS and optionally waits for SCWR; the external circuit may use that
interface in other ways. ControlPort's retained latch value is a chosen
example peripheral model, not mandatory CPU/system architecture.

## Interrupt integration — v016

Printed pp.62–65 were visually rechecked. Figure 4.20a separates the enabled,
asynchronous active-low INT→INTR set path from the INTR→INTA clock at
F0T0. Figure 4.20b supplies the eight-slot accepted-entry sequence: T0
acknowledges and clears INTE/INTR, T1 drives constant02, T2 increments N,
T4 writes02 to the new R(N), and T7 resets phase. No PG change, normal opcode
fetch or automatic data/flag stack is shown. The reset table adjacent to
it is separate and has not been implemented in this pass.

The selected controller lets an already latched request survive INT returning
high or DIN clearing INTE, following the detailed circuit rather than treating
the simplified INTE/raw-INT flowchart as an exhaustive gate description.
Acceptance samples pending INTR before entry's simultaneous mask/clear,
then settles the input gate again. EIN's deferred enable can likewise admit
a held request after the following instruction's T0 acceptance boundary
has passed. These are functional endpoint interpretations; near-edge races
and electrical pulse widths are not recovered from the diagram.

Tests now cover EIN plus a held INT, completion of the following instruction,
entry, handler work and EIN;RSR return. A continuously held request after
handler reenable is accepted only after RSR restores N. RSR alone retains
INTE disabled. Entry preserves global PG; returning does not invent a page
stack. Requests can latch during SCWR waits or EXR's partial exchange but
are serviced only after the selected instruction-completion boundary.

Integration also exposes an unresolved retained-IR case: entry does not
replace IR. The selected entry table overrides normal opcode effects, but
the following handler fetch can still see an old EIN at T2 (e.g. consecutive
EINs before acceptance). The model records that consequence and adds no
hidden consumed-effect latch. Exact INTA/opcode decoder precedence for
those combinations remains uncertain, despite the normal EIN;RSR case's
strong source support. See [v016](docs/model-v016.md) for the complete
assumptions, opt-in API, table and tests. v015 remains unchanged.

## Accepted application-listing corrections — E004–E007

The project owner accepted E004–E007 after reviewing the program context.
Figure 8.10 intends XRI R7,#377 at octal 012 (052→057) and BZ0,3 at
014 (340→343). Figure 8.9 places KEX at 3,363; the p.150 startup jump
to 3,017 points immediately beyond the keyboard routine. This adjacency
supports, but does not itself prove, page 3; branch 005 and mnemonic 014
also support it. Figure 8.12 intends SRD R7 at 052 (032→037), following
the read/increment of R7. On p.95 the output-port address 001 should be
00; input address 001 in the preceding paragraph is correct. See
[the working errata](docs/errata.md) for the retained printed fields and
evidence. These decisions require no simulator revision; the existing
keyboard test already uses the intended bytes.

## RESET — printed pp.64–65, figure 4.21 (v017)

Page64's RESET paragraph and figure4.21 on p.65 were visually checked.
The text states that active-low RESET reaches the PLA only when MOP47
is active, during T7; the following machine cycle is then the reset cycle.
Figure4.21b lists F0T0: 0→INTA and 0→PG; T1: 0→DI; T2: 0→N;
T4: DI→R(N), now R0; T7: 0→F. Other cells are blank. This is separate
from interrupt figure4.20 above it on the same page. The literal functional
row is saved as `fig4.21_reset` in specification/book-microprograms.json.

The supplied MOP list has no numbered INTA-clear operation. v017 uses
a visible named clear at T0, MOP42 for PG, MOP40 held T1–T4, MOP45
at T2, and MOP18/22 at T4. No other state clears are invented.
Selecting reset after any T7, including execute and SCWR waits, repeating
cycles for a held pin, and priority over the next interrupt check are
controller interpretations of the gate/prose. They remain distinguished
from the explicit table. INTE/INTR and IR preservation exposes pending
interrupt and retained-opcode consequences; complete decoder precedence
is not established. See [v017](docs/model-v017.md).

## RESET interrupt-initialization question reopened

The project owner questioned whether INTR preservation across RESET is an
omission in figure4.21 rather than actual hardware behavior. Rechecking
pp.62–65 gives no explicit RESET clear for INTR/INTE. However, figure4.20a's
asynchronous request-set gate is independent of the selected microprogram;
exclusive RESET/interrupt-entry sequences do not imply request capture is
inhibited during reset. An omitted INTR clear is plausible. Clearing both
INTR and INTE, or further reset gating, would also address a held-low INT;
INTR-only clearing would not prevent relatching with INTE=1. These are
retained alternatives, not an accepted erratum or an architecture change.
See the reopened question in [v017](docs/model-v017.md). Its tests continue
to characterize the literal-table baseline rather than establish the real
chip's reset distribution.

## Shared MEMR/HALT/SS waits — v018

Printed pp.58–61 and 88–91 were visually rechecked. Figure4.15 shows a
HALT latch set by F0T2 and asynchronously reset by high HALT. Its Q is
ORed with MOP29-gated raw MEMR into WAIT's T4-clocked D input. The WAIT
output gate masks the active-low output high during T4. Figure4.16's
caption explicitly describes a wait from beginning T4 through the following
T3; one such wait in each LRS phase gives six machine cycles for three
phases. Figure4.17 shows three HALT waits, held opcode address/PME and
high WAIT pulses each T4. Page60 explicitly resumes interrupted work at T4.

Figure6.6/p.89 and p.88 describe SS only on the HALT-low branch: SS high
sets SSE; SS low with SSE=1 clears SSE and permits one instruction; held-low
SS with SSE=0 waits at the next fetch. Page90 specifies SS low during a
later T3; figure6.8/p.91 illustrates the sequence. Page91 explicitly omits
the detailed SSE circuit. The 8080 discussion is comparison context, not
CMC8 circuitry. MEMR is expanded as memory ready on p.56.

v018 adds the documented HALT latch, retains SSE, and implements T4→F3→
original-T4 continuation with external enables held. H022 extends read
checks consistently where sparse selected tables omit MOP29. H023 selects
SSE controls at fetch-context T3 and retains a step grant through MEMR waits.
These controller choices are distinct from the printed circuitry. The
memory harness supplies delayed data independently of the externally driven
MEMR pin. See [v018](docs/model-v018.md) for sources, APIs and limits.

The project owner's subsequent RESET/INTR interpretation is retained:
clearing INTA ends an old acknowledgement, while a preserved request can be
acknowledged after reset. No additional reset clear was selected or shown
necessary by that behavior; the previously recorded alternatives remain
available if new evidence distinguishes them.

## Package pinout investigation — PIN001

The owner supplied TEKS0043130.jpg and TEKS0043130 (1).jpg, showing an
opened 40-pin package, and correlated its die with the cover/page35 layout:
for that layout orientation the package notch points left. Page34 fig3.4,
page35 fig3.5, the cover and page114 fig7.6 were visually compared. A
clockwise inventory starting at the upper-left corner contains 40 apparent
perimeter pads. Figure3.5 explicitly labels AB7…AB0, VSS, DB7…DB3 and VDD.
The three repeating lower-right data-driver pads plausibly continue as
DB2, DB1 and DB0; these are pattern identifications, not printed labels.

The owner's connector-order suggestion gives a strong conditional match:
reverse pad order DB0…DB7,VSS,[unlabeled],AB0…AB7 equals connector
a13…a30, with LINK at a22 identifying a candidate LOUT pad in the gap.
The owner also counted exactly eleven intervening pads from VDD to the
DB0 candidate, matching connector a1→a13. VDD and VSS are twenty positions
apart. Assuming a1…a31 follows CPU numbering gives one cyclic alignment
matching all fifteen explicit die labels; the next-best alignment matches
only two. This is conditional consistency, not independent pinout proof.

PIN001 proposes VDD1; SME2,EDE3,MEMR4,PME5,SS6,HALT7,INTA8,INT9;
PG1=10,PG0=11,DBDIR12; DB0…DB7=13…20; VSS21; LOUT22;
AB0…AB7=23…30; RESET31,STRCS32,CL33,WRITE34,SCWR35;
TEST3…TEST0=36…39; WAIT40. Pin numbers are standard top-view DIP numbers
with notch left. Individual control assignments remain less supported than
the explicitly labeled bus/supply order. Connector a32 is INHIBIT, not
STRCS; b32 exposes STRCS, while b3…b11 groups WAIT, TEST, SCWR, WRITE
and two board clock connections. The latter do not imply two CPU clocks.

The connector is a 64-contact Midahs board interface; its ordering need not
be the chip ordering. Noncrossing visible bonds also do not expose hidden
carrier routes to the external leads. These assumptions and the unverified
absolute numbering remain explicit. See [the investigation](docs/pinout-investigation.md),
its pad inventory and proposed package diagram. No CPU model change was made.

Additional owner observation: in the colour package photograph, the seventh
right-side die wire from the bottom (third in the separated upper-half group)
lands on the sixth carrier finger counted from the top. The matching
figure3.5 pad is VDD. A symmetric split into the two 20-pin banks makes
this a candidate pin1 landing in the notch-right photo. This supplies a
bond-based VDD1 anchor independent of connector ordering, while retaining
the carrier/symmetry assumption. The enlarged crop is consistent with the
mid-side landing; the detailed count remains attributed to the owner, and
buried lead routing is not claimed independently traced. Corner fingers
must be included consistently in such counts.

Second owner-traced package anchor: sixth carrier finger from the bottom
on the left side of the notch-right colour photograph reaches the upper
of a close die-pad pair, followed after a gap by another close pair. With
the figure3.5 layout rotated 180 degrees, this matches VSS, its neighbor
(candidate LOUT), then the AB0/AB1 pair. The carrier split makes this
candidate pin21, supporting the VSS assignment independently of connector
row a21. Both supply ends now have owner-traced physical support under
the orientation/carrier assumptions.

The owner also noted an apparently disconnected bond at candidate pin20
(DB7). The enlarged left-side crop shows a loose-looking curved wire; no
electrical continuity, die-health or repairability conclusion is claimed.
The mapping and sample-condition observations are recorded separately in
specification/pinout-hypothesis.json and the pinout investigation.

## Traffic application and FPGA control study

Figures8.3/p.141 and8.6/pp.146–147 were visually rechecked. All75 bytes
through octal112 are preserved in specification/traffic-program.json. ED4
main lamps use bits0/1/2 (red/yellow/green); side lamps use bits5/6/7. The
044→046→041→201→301→041→044 octal sequence is retained, including the
example's green+yellow overlap. T1/T3 requests initiate the light cycle.
Candidate E009 records octal172's incorrect “dec76” annotation (decimal122
is intended, agreeing with p.144); E010 records the T1/T2 comment beside
actual T1/T3 branches. No machine byte is corrected for these comments.
The exact selected delay routine takes156,776 machine cycles, or10.033664s
at the p.144 Midahs subdivision duration8µs, excluding the caller's JSR.
The external board harness and shortened/full fixtures remain distinct.

Printed pp.46–48 were visually rechecked. The book contrasts ROM control
with shared AND/OR functions, describes CMC8's five-input NAND instruction
decode and OR combinations, then distinguishes phase gates near the PLA
from distributed timing gates near the datapath (fig4.8). A functional RTL
export therefore need not reproduce the original physical PLA or routing.
The selected v018 base control truth function, including interrupt/reset
modes and explicit research sidebands, is exported as335 shared products.
All32,768 binary inputs agree; all9,822 defined entries agree with the
existing sequencer under quiet inputs and an untaken branch condition.
Dynamic branch, wait, SSE and asynchronous controller behavior remain
outside this base export. Generated VHDL/Verilog has not been compiled or
synthesized because the corresponding tools are absent. See
[the traffic harness](docs/traffic-harness.md) and
[the control study](docs/pla-control-study.md).

The literal traffic program completed11,288,752 subdivisions and564,443 CPU
events, returning to polling with ED4=044 octal and N=0. The serviced light
interval was90.306624s, including nine real delay calls and instruction
overhead. Seven committed ED4 writes and all exact intervals/counts were
checked independently; specification/traffic-validation.json preserves the
result and docs/figures/traffic-validation.svg displays it. No source byte,
delay loop, instruction semantics or numbered model was replaced.

Midahs pp.126–133 were consulted for a functional front-panel extension.
Figure7.13/p.127 was visually checked: low ED6 bits0/1/2 enable the left,
middle and right ED0 display digits; ED1/ED2 remain on. Figure7.15/p.130
provides the12 key codes, and figures7.16/7.17 on pp.130–131 distinguish
the actual board keyboard wiring from a data-sheet example. The fixture
injects observed byte codes and idleFF explicitly, rather than claiming
a complete74C922 electrical/debounce model. Read/write ED0–2, ED3 switches,
ED4 lamps, ED5 keyboard and ED6 digit enables are tested with book snippets.
The corrected figure8.10 keyboard routine also waits for press/release and
returns its captured code through actual page3 JMP/JSR/RSR execution.
KEX board remapping and a full monitor remain separate.
