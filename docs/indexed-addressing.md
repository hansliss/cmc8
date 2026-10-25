# Indexed load/store investigation

Status: documented instruction semantics; two executable candidate schedules.
No numbered architecture or opcode decoder has been changed by this analysis.

## Working selection

Project-owner decision, 2026-10-25: select **H006-A**, the AND-style
X→DI→DB→BR→AB route, for the next indexed-instruction implementation.
Continue using it while it remains consistent with the evidence and tests.
Its precise indexed timing remains likely / consistency-supported
extrapolation, not established source fact.

Retain **H006-B**, X→DI→AB, as the unselected backup. Reassess the choice
if new source evidence or an experiment contradicts H006-A; do not switch
routes silently. Both schedules remain executable in the experiment below.

## What the book supplies

| Printed page | Source | Evidence |
| --- | --- | --- |
| 40 | `Page_046.jpg` | X is R7; MOP20 selects it directly; LSX reads storage addressed by X |
| 43 | `Page_049.jpg` | LSX is one byte yet takes three cycles, explicitly to simplify the microprogram |
| 67 | fig.5.1, `Page_073.jpg` | LRX/LSX/SRX/SSX encodings, memory spaces and three-cycle duration |
| 68 | format b, `Page_074.jpg` | SSX is one byte; its low three bits select the source register R(A) |
| 75 | fig.5.7, `Page_081.jpg` | AND prepares its X operand using X→DI, DI→DB, DB→BR during F1 |

These pages were visually checked. OCR searches for indexed mnemonics also
found usage examples in the KEX program but no complete indexed MOP table.
This is not a claim that every diagram in the book has been exhaustively
checked. The semantics and cycle count are covered explicitly; the precise
indexed MOP sequence still requires reconstruction.

| Instruction | Opcode pattern | Target memory | Operation |
| --- | --- | --- | --- |
| LRX | 01001RRR (48–4F) | program | M[X]→R(A) |
| LSX | 01011RRR (58–5F) | storage | M[X]→R(A) |
| SRX | 01101RRR (68–6F) | program | R(A)→M[X] |
| SSX | 01111RRR (78–7F) | storage | R(A)→M[X] |

The parenthesized ranges are hexadecimal. Addressing is register-indirect
through X, not an addition of X to an immediate displacement. The existing
PG+AB interpretation supplies the page. F0 increments PC once; F1 must not
perform a second increment or consume an operand byte.

## Preferred candidate H006-A: reuse the buffer timing

Figure 5.7 supplies a useful precedent in a different CMC8 instruction:
its functional F1 row transfers X→DI at T0, DI→DB at T1 and DB→BR at T5.
Reuse that preparation, then retain the direct-address load/store model's
BR→AB at F1T6 and its complete F2 transfer.

| F1 slot | Candidate controls | Effect |
| --- | --- | --- |
| T0 | 20,21 | X drives DI |
| T1–T4 | 20,21,23 | X drives DI and CPU drives DB |
| T5 | 20,21,23,2 | DB→BR captures X |
| T6, loads | 6 | BR→AB |
| T6, stores | 6,19,21 | BR→AB while R(A) drives DI |
| T7, loads | none | Hold address |
| T7, stores | 19,21,23 | Begin output-data drive as in SRS/SRM |

No PME, SME or memory-ready check is needed in this F1 candidate. DB is
CPU-driven loopback, not a response from memory. Existing circuitry already
connects DI→DB and DB→BR, so this requires no new datapath connection or
unspecified ALU pass-through function. F2 then uses the corresponding
LRM/LRS/SRM/SRS phase unchanged.

This is **consistency-supported extrapolation**, not a transcription of
indexed timing. The held controls in the table are explicit reconstruction
choices: fig.5.7's printed MOP row is sparse and also shows MOP23 at T0,
whereas its functional row puts DI→DB at T1. Do not treat it as an exact
complete control-level table for this candidate. The candidate borrows its
functional path and capture slot, retaining the drive until capture.

## Alternative H006-B: direct address loading

Use MOP20+21 to put X on DI at F1T0, keep them and assert MOP14 at F1T1
to capture DI into AB. Leave the remaining F1 slots idle, except for store
source selection at T6 and output drive at T7. Reuse F2 as above.

This is also consistent with fig.4.1 and the documented instruction effects.
It changes AB earlier, avoids the DB loopback and does not load X into BR.
No inspected indexed timing diagram distinguishes these alternatives.
H006-A is preferred under the project's consistency principle because it
reuses documented X→BR preparation and the established F1T6 address-transfer
slot. This is a preference between candidates, not proof of historical timing.

## Executable experiments

```sh
python3 -m experiments.indexed_address_routes
```

The experiment uses the preserved v006 **manual datapath** rather than
adding opcodes to the instruction sequencer. It checks both candidates for
all four instructions, pages and N/A register pairings: 2048 cases. It uses
ideal memory and explicit captures, checks no F1 memory read occurs, and
checks the address, transfer result and PC increment. This is a functional
consistency experiment, not a timing conformance test.

Alias cases matter: if N=7, fetch increments X because X is then the PC;
F1 reads that updated register. If A=7, loads overwrite X only after AB has
captured the address, and stores write X's address value as their data.
If A=N, a load replaces the PC; a store uses the PC already advanced by one.

Before integrating H006-A into a new numbered instruction simulator, fix
its required-data check: v006's sequencer currently validates DB→BR against
only the external response. It must instead validate resolved DB, which
may legitimately be CPU-driven via MOP23. The underlying datapath already
supports this path. Also preserve the earlier unselected address route and
its distinct AB/DB timing in the investigation record.

## Implementation update

[v007](model-v007.md) now integrates selected H006-A into the instruction
sequencer and decodes all four indexed families. It validates resolved DB
for CPU-driven captures and retains the documented confidence level.
H006-B and the original manual experiment remain unchanged as the backup
and investigation baseline. The earlier statements about unimplemented
opcodes describe the investigation before v007.
