# Architecture model v007

Predecessor: [v006](model-v006.md), preserved unchanged. This complete
numbered package implements LRX, LSX, SRX and SSX using selected hypothesis
H006-A, the AND-style X→DI→DB→BR→AB path. Their exact internal timing remains
**likely / consistency-supported extrapolation**, not established source fact.

## Run and inspect

```sh
python3 -m cmc8 --model v007
python3 -m cmc8 --model v007 --json
python3 -m unittest discover -s tests -v
```

The demo runs LRX R3; SRX R3; SSX R3; LSX R4 on page 2, with X=80.
All four instructions are single bytes at addresses 220–223. They transfer
A6 from program[280] through R3 to program/storage memory, then into R4.
PC ends at 24 after 96 subdivisions. All numbers are hexadecimal.

Read `cmc8/versions/v007/sequences.py` for the explicit F1 controls and
`instructions.py` for bus resolution and capture checks. No new datapath
connections, pending-effect storage or direct instruction-level assignments
were added. Indexed loads/stores preserve v006's deferred flag controls.

## Evidence and selected sequence

| Source | Support |
| --- | --- |
| p.40, `Page_046.jpg` | X=R7 and MOP20 selects it |
| p.43, `Page_049.jpg` | LSX is one byte, three cycles to simplify the microprogram |
| p.67, fig.5.1, `Page_073.jpg` | All four encodings, memory spaces, three-cycle duration and no flag changes |
| p.68, `Page_074.jpg`, format b | SSX source register comes from opcode bits 0–2 |
| p.75, fig.5.7, `Page_081.jpg` | AND's functional F1 sequence prepares X through DI/DB into BR at T5 |

The [investigation](indexed-addressing.md) preserves the source details,
held-control assumptions and competing route. The project owner selected
H006-A on 2026-10-25 and authorized this implementation. No additional
indexed timing table has been found since that investigation.

F0 is unchanged, fetching the opcode and incrementing PC once. F1 uses:

| Slot | MOPs | Effect |
| --- | --- | --- |
| T0 | 20,21 | X drives DI |
| T1–T4 | 20,21,23 | X drives DI and DB |
| T5 | 20,21,23,2 | CPU-driven DB captured into BR |
| T6, loads | 6 | BR→AB |
| T6, stores | 6,19,21 | BR→AB while source R(A) drives DI |
| T7, loads | none | Hold address |
| T7, stores | 19,21,23 | Drive store data onto DB |

There is no PME/SME/EDE assertion, memory-ready sampling or second PC
increment in F1. Its DB activity is loopback, not an external-memory fetch.
The explicit held levels borrow fig.5.7's functional path; they are not a
literal transcription of that figure's sparse numbered row.

F2 reuses LRM for LRX, LRS for LSX, SRM for SRX and SRS for SSX. Loads
capture memory data into BR at F2T5 and write R(A) at T6. Stores complete
on WRITE falling at F2T5 in the existing memory harness. All four reset
the phase at F2T7. Program/storage addresses remain PG+AB.

Opcodes are LRX=48–4F, LSX=58–5F, SRX=68–6F and SSX=78–7F (hex).
These instructions use the address in X directly, with no displacement
addition or automatic X increment. If X aliases PC (N=7), the normal fetch
increment naturally changes it before the indexed address is read.

## Bus-validity correction

v006's sequencer checked whether DB was valid using only the external
memory response. That rejects a legitimate DB→BR capture when the CPU
itself supplies DB via MOP23, even though the datapath already resolves
that circuit correctly. v007 checks the resolved DB value before capture.
This admits driven loopback while still rejecting unknown X and missing or
late external data. CPU output continues to make the memory adapter release
DB, preventing fictitious external contention.

## Preserved backup

H006-B, X→DI→AB at F1T1, remains the unselected backup in
`experiments/indexed_address_routes.py`. That experiment deliberately uses
v006's manual datapath to preserve the original investigation. v007 has no
silent fallback or runtime switch to the backup. If evidence contradicts
the buffer route, revisit the recorded choice in a subsequent model.

## Validation and limits

Tests run all four instructions across four pages, every N/A pairing and
byte boundary values, including loading X itself, storing X, X as PC and
R(A) as PC. They verify the actual F1 loopback capture, F1T6 address timing,
absence of F1 external reads, one-byte instruction streams, final memory
control windows, PC wraparound, unchanged flags and timely-data checks.
Unknown X produces an atomic failed slot that can be retried. A preceding
EIN updates INTE once before indexed execution. Previously supported
instructions are compared against v006's full state and control traces.

These are tests of the selected reconstruction, not new historical timing
evidence. The earlier always-ready assumption, simplified peripherals,
endpoint capture model, provisional flag timing, and other electrical and
ALU limitations remain. JMP, JSR, RSR, conditional branches and interrupt
handling remain unimplemented and retain their place in the validation plan.
