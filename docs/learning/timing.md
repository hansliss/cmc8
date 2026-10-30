# CMC8 instruction MOP timing

[Study guide](README.md) · [Instructions](instructions.md) · [MOPs](mops.md) · [Timing](timing.md) · [Datapath](processor.svg)


## Reading the tables

These are expanded **v018 working-model** tables, including derived schedules; they are not all printed microcode. Each cell lists controls held during that subdivision; — means no listed control. **Italic entries** belong to the shared F0 fetch (T0–T5). F0T6/T7 are instruction-dependent, so they are not italicized. The inherited duplicate PME in the LRS transcription is shown only once.

IR captures the new opcode at the end of F0T5. Earlier F0 controls are shared sequencing; the old IR still selects a preceding flag instruction at F0T2. Thus a table groups fetch with its newly decoded instruction for reading, but does not imply all its cells are decoded from that instruction. Deferred flag strobes are described separately because they belong to the preceding instruction.

MOP31 at F1T1 changes phase to F2 without restarting T: the next cell is **F2T2**. Cells F1T2–T7 and F2T0–T1 are unreachable in these two-cycle schedules and marked ×. Repeated controls are held levels, not repeated independent transfers. Data state is captured from start-of-slot signals; IR additionally captures at slot end. Controls in one cell act together, not left-to-right.

### Shared overlays and waits

- With interrupt integration, add *28 INTR→INTA* at F0T0; a pending request selects the separate interrupt-entry cycle.

- With reset integration, add 47 RESET? at every executed T7, including wait and special cycles.

- With execution control, every external read that will capture a byte gets 29 MEMR? at T4 (H022). Additions omitted by the base table are marked `[H022]` below. This also covers SCS/SCW F1 control-byte reads.

- Fetch-context T3 may additionally assert 48 0→SSE or 49 1→SSE, according to HALT/SS/SSE (H023). These are conditional controller overlays, not unconditional entries in every table.

- A failed T4 memory/HALT test suppresses that cell’s CPU write, holds the external enable, and enters an eight-slot F3 continuation. F3 holds the enable and retests at T4; on release the suspended T4 controls complete before T5. SCW F3 instead holds PME throughout and samples 50 SCWR? each T4.

## Instruction tables

### LRM

LRM Rr,A · 3 cycles · [source notes and confidence](../instructions/LRM.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 6 BR→AB | — |
| F2 | — | — | 24 PME | 24 PME | 29 MEMR?<br>24 PME | 2 DB→BR<br>24 PME | 4 BR→DI<br>22 DI→R<br>19 select Rr | 30 0→F |

### LRS

LRS Rr,A · 3 cycles · [source notes and confidence](../instructions/LRS.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 6 BR→AB | — |
| F2 | — | — | 25 SME | 25 SME | 29 MEMR?<br>25 SME | 2 DB→BR<br>25 SME | 4 BR→DI<br>22 DI→R<br>19 select Rr | 30 0→F |

### LRX

LRX Rr · 3 cycles · [source notes and confidence](../instructions/LRX.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | 6 BR→AB | — |
| F2 | — | — | 24 PME | 24 PME | 29 MEMR?<br>24 PME | 2 DB→BR<br>24 PME | 4 BR→DI<br>22 DI→R<br>19 select Rr | 30 0→F |

### LSX

LSX Rr · 3 cycles · [source notes and confidence](../instructions/LSX.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | 6 BR→AB | — |
| F2 | — | — | 25 SME | 25 SME | 29 MEMR?<br>25 SME | 2 DB→BR<br>25 SME | 4 BR→DI<br>22 DI→R<br>19 select Rr | 30 0→F |

### LRD

LRD Rr,P · 3 cycles · [source notes and confidence](../instructions/LRD.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 6 BR→AB | — |
| F2 | — | — | 26 EDE | 26 EDE | 29 MEMR?<br>26 EDE | 2 DB→BR<br>26 EDE | 4 BR→DI<br>22 DI→R<br>19 select Rr | 30 0→F |

### SRM

SRM Rr,A · 3 cycles · [source notes and confidence](../instructions/SRM.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 6 BR→AB<br>19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB |
| F2 | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME | — | 30 0→F |

### SRS

SRS Rr,A · 3 cycles · [source notes and confidence](../instructions/SRS.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 6 BR→AB<br>19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB |
| F2 | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME | — | 30 0→F |

### SRX

SRX Rr · 3 cycles · [source notes and confidence](../instructions/SRX.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | 6 BR→AB<br>19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB |
| F2 | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>24 PME | — | 30 0→F |

### SSX

SSX Rr · 3 cycles · [source notes and confidence](../instructions/SSX.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | 6 BR→AB<br>19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB |
| F2 | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>25 SME | — | 30 0→F |

### SRD

SRD Rr,P · 3 cycles · [source notes and confidence](../instructions/SRD.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 6 BR→AB<br>19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB |
| F2 | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>26 EDE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>26 EDE<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>26 EDE<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>26 EDE<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>26 EDE<br>27 WRITE | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>26 EDE | — | 30 0→F |

### BB0

BB0 Rr,A · 3 cycles · [source notes and confidence](../instructions/BB0.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | — | — |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>54 DI0→cond | 19 select Rr<br>21 R→DI<br>54 DI0→cond<br>55 cond XOR IR3→H | — | — | — | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R | 30 0→F |

### BB1

BB1 Rr,A · 3 cycles · [source notes and confidence](../instructions/BB1.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | — | — |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>54 DI0→cond | 19 select Rr<br>21 R→DI<br>54 DI0→cond<br>55 cond XOR IR3→H | — | — | — | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R | 30 0→F |

### BL0

BL0 p,A · 2 cycles · [source notes and confidence](../instructions/BL0.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME<br>52 L→cond<br>55 cond XOR IR3→H | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R<br>if H=0: 15 IR[1:0]→PG | 30 0→F |

### BL1

BL1 p,A · 2 cycles · [source notes and confidence](../instructions/BL1.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME<br>52 L→cond<br>55 cond XOR IR3→H | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R<br>if H=0: 15 IR[1:0]→PG | 30 0→F |

### BZ0

BZ0 p,A · 2 cycles · [source notes and confidence](../instructions/BZ0.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME<br>51 Z→cond<br>55 cond XOR IR3→H | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R<br>if H=0: 15 IR[1:0]→PG | 30 0→F |

### BZ1

BZ1 p,A · 2 cycles · [source notes and confidence](../instructions/BZ1.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME<br>51 Z→cond<br>55 cond XOR IR3→H | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R<br>if H=0: 15 IR[1:0]→PG | 30 0→F |

### BT0

BT0 t,A · 2 cycles · [source notes and confidence](../instructions/BT0.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME<br>53 TEST→cond<br>55 cond XOR IR3→H | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R | 30 0→F |

### BT1

BT1 t,A · 2 cycles · [source notes and confidence](../instructions/BT1.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME<br>53 TEST→cond<br>55 cond XOR IR3→H | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>if H=0: 22 DI→R | 30 0→F |

### JMP

JMP p,A · 2 cycles · [source notes and confidence](../instructions/JMP.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | — | 31 2→F | × | × | × | × | × | × |
| F2 | × | × | 24 PME | 24 PME | 24 PME<br>29 MEMR? [H022] | 2 DB→BR<br>24 PME | 4 BR→DI<br>18 select PC<br>15 IR[1:0]→PG<br>22 DI→R | 30 0→F |

### JCR

JCR Rr · 2 cycles · [source notes and confidence](../instructions/JCR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | 4 BR→DI<br>18 select PC<br>22 DI→R | 30 0→F |

### LRI

LRI Rr,#I · 2 cycles · [source notes and confidence](../instructions/LRI.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | 4 BR→DI<br>19 select Rr<br>22 DI→R | 30 0→F |

### XRI

XRI Rr,#I · 3 cycles · [source notes and confidence](../instructions/XRI.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | — | — |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>3 BR→B<br>7 DI→A<br>8 A XOR B<br>32 Z←zero<br>12 MUX→BR | 4 BR→DI<br>22 DI→R<br>19 select Rr | — | — | 30 0→F |

### ANI

ANI Rr,#I · 3 cycles · [source notes and confidence](../instructions/ANI.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | — | — |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>3 BR→B<br>7 DI→A<br>9 A AND B<br>32 Z←zero<br>12 MUX→BR | 4 BR→DI<br>22 DI→R<br>19 select Rr | — | — | 30 0→F |

### CPY

CPY Rr · 2 cycles · [source notes and confidence](../instructions/CPY.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | 4 BR→DI<br>20 select X<br>22 DI→R | 30 0→F |

### INR

INR Rr · 3 cycles · [source notes and confidence](../instructions/INR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>10 A+1<br>7 DI→A<br>12 MUX→BR<br>32 Z←zero | — | — | 4 BR→DI<br>19 select Rr<br>22 DI→R | 30 0→F |

### ROR

ROR Rr · 2 cycles · [source notes and confidence](../instructions/ROR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 19 select Rr<br>21 R→DI<br>7 DI→A<br>11 SHR<br>12 MUX→BR<br>13 A0→MUX7 | — | — | 4 BR→DI | 19 select Rr<br>22 DI→R<br>4 BR→DI | 30 0→F |

### SHR

SHR Rr · 2 cycles · [source notes and confidence](../instructions/SHR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 19 select Rr<br>21 R→DI<br>7 DI→A<br>11 SHR<br>12 MUX→BR<br>43 0→MUX7 | — | — | 4 BR→DI | 19 select Rr<br>22 DI→R<br>4 BR→DI | 30 0→F |

### RRL

RRL Rr · 2 cycles · [source notes and confidence](../instructions/RRL.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>31 2→F | × | × | × | × | × | × |
| F2 | × | × | 19 select Rr<br>21 R→DI<br>7 DI→A<br>11 SHR<br>12 MUX→BR<br>33 L↔shift | — | — | 4 BR→DI | 19 select Rr<br>22 DI→R<br>4 BR→DI | 30 0→F |

### DCR

DCR Rr · 3 cycles · [source notes and confidence](../instructions/DCR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB | 19 select Rr<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | — | — |
| F2 | 5 ~BR→DI | 5 ~BR→DI | 5 ~BR→DI | 5 ~BR→DI<br>10 A+1<br>7 DI→A<br>12 MUX→BR | — | — | 5 ~BR→DI<br>19 select Rr<br>22 DI→R<br>32 Z←zero<br>zero=DI [H014] | 30 0→F |

### XOR

XOR Rr · 3 cycles · [source notes and confidence](../instructions/XOR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | — | — |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>3 BR→B<br>7 DI→A<br>8 A XOR B<br>32 Z←zero<br>12 MUX→BR | 4 BR→DI<br>22 DI→R<br>20 select X | — | — | 30 0→F |

### AND

AND Rr · 3 cycles · [source notes and confidence](../instructions/AND.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | — | — |
| F2 | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI | 19 select Rr<br>21 R→DI<br>3 BR→B<br>7 DI→A<br>9 A AND B<br>32 Z←zero<br>12 MUX→BR | 4 BR→DI<br>22 DI→R<br>20 select X | — | — | 30 0→F |

### EXR

EXR Rr · 3 cycles · [source notes and confidence](../instructions/EXR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 20 select X<br>21 R→DI | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB | 20 select X<br>21 R→DI<br>23 DI→DB<br>2 DB→BR | — | — |
| F2 | 19 select Rr<br>21 R→DI<br>7 DI→A<br>A.capture [H019] | — | — | — | 4 BR→DI<br>19 select Rr<br>22 DI→R | 12 MUX→BR<br>A.held [H019] | 4 BR→DI<br>20 select X<br>22 DI→R | 30 0→F |

### SCW

SCW #I · 3 cycles · [source notes and confidence](../instructions/SCW.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 24 PME | 24 PME<br>STRCS (unnumbered) | 24 PME |
| F2 | 24 PME | 24 PME | 24 PME | 24 PME | 24 PME<br>50 SCWR? | 24 PME | — | 30 0→F |

### SCS

SCS #I · 3 cycles · [source notes and confidence](../instructions/SCS.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>22 DI→R<br>24 PME<br>29 MEMR? [H022] | 24 PME | 24 PME<br>STRCS (unnumbered) | 24 PME |
| F2 | 24 PME | 24 PME | 24 PME | 24 PME | 24 PME | 24 PME | — | 30 0→F |

### JSR

JSR A · 3 cycles · [source notes and confidence](../instructions/JSR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI | 18 select PC<br>21 R→DI<br>24 PME | 18 select PC<br>21 R→DI<br>7 DI→A<br>10 A+1<br>24 PME<br>12 MUX→BR | 4 BR→DI<br>18 select PC<br>29 MEMR?<br>22 DI→R<br>24 PME | 2 DB→BR<br>24 PME | — | — |
| F2 | — | — | 16 N+1 | — | — | — | 4 BR→DI<br>18 select PC<br>22 DI→R | 30 0→F |

### RSR

RSR · 2 cycles · [source notes and confidence](../instructions/RSR.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | — |
| F1 | — | 31 2→F | × | × | × | × | × | × |
| F2 | × | × | 17 N−1 | — | — | — | — | 30 0→F |

### NOP

NOP · 1 cycles · [source notes and confidence](../instructions/NOP.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

### EIN

EIN · 1 cycles · [source notes and confidence](../instructions/EIN.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

**Deferred effect:** 38 1→INTE at **following F0T2**, alongside that fetch’s italic controls. Confidence: high; documented timing; derived decoder.

### DIN

DIN · 1 cycles · [source notes and confidence](../instructions/DIN.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

**Deferred effect:** 39 0→INTE at **following F0T2**, alongside that fetch’s italic controls. Confidence: likely; consistency-supported extrapolation.

### SEL

SEL · 1 cycles · [source notes and confidence](../instructions/SEL.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

**Deferred effect:** 34 1→L at **following F0T2**, alongside that fetch’s italic controls. Confidence: likely; consistency-supported extrapolation.

### REL

REL · 1 cycles · [source notes and confidence](../instructions/REL.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

**Deferred effect:** 35 0→L at **following F0T2**, alongside that fetch’s italic controls. Confidence: likely; consistency-supported extrapolation.

### SEZ

SEZ · 1 cycles · [source notes and confidence](../instructions/SEZ.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

**Deferred effect:** 36 1→Z at **following F0T2**, alongside that fetch’s italic controls. Confidence: likely; consistency-supported extrapolation.

### REZ

REZ · 1 cycles · [source notes and confidence](../instructions/REZ.md)

| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | *18 select PC*<br>*21 R→DI* | *18 select PC*<br>*21 R→DI*<br>*14 DI→AB* | *18 select PC*<br>*21 R→DI*<br>*24 PME* | *18 select PC*<br>*21 R→DI*<br>*7 DI→A*<br>*10 A+1*<br>*24 PME*<br>*12 MUX→BR* | *4 BR→DI*<br>*18 select PC*<br>*29 MEMR?*<br>*22 DI→R*<br>*24 PME* | *1 DB→IR*<br>*24 PME* | 6 BR→AB | 30 0→F |

**Deferred effect:** 37 0→Z at **following F0T2**, alongside that fetch’s italic controls. Confidence: likely; consistency-supported extrapolation.

## Separate entry cycles

These cycles have no opcode and are not standard fetches. PG is unchanged by interrupt entry. Reset clears PG/N/current PC and INTA as shown; it does not clear INTR or unlisted flags.

### Interrupt entry

| T | Controls |
| --- | --- |
| T0 | 28 INTR→INTA<br>39 0→INTE<br>46 0→INTR |
| T1 | 41 2→DI |
| T2 | 41 2→DI<br>16 N+1 |
| T3 | 41 2→DI |
| T4 | 41 2→DI<br>18 select PC<br>22 DI→R |
| T5 | — |
| T6 | — |
| T7 | 30 0→F |
### Reset

| T | Controls |
| --- | --- |
| T0 | 42 0→PG<br>clear INTA (unnumbered) |
| T1 | 40 0→DI |
| T2 | 40 0→DI<br>45 0→N |
| T3 | 40 0→DI |
| T4 | 40 0→DI<br>18 select PC<br>22 DI→R |
| T5 | — |
| T6 | — |
| T7 | 30 0→F |
