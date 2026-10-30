# CMC8 compact instruction list

[Study guide](README.md) · [Instructions](instructions.md) · [MOPs](mops.md) · [Timing](timing.md) · [Datapath](processor.svg)


All 43 families / 239 valid encodings. Encoding bits are binary; opcode bases are octal. `r` selects R0–R7, `p` selects page 0–3, `t` selects TEST0–3. `A` is an 8-bit address byte, `P` a port byte, `I` an immediate byte; X = R7. PC = R(N). PM and SM use the current PG, except explicit page-changing jumps/branches. Flags lists only flags changed. Cycles include fetch, exclude waits.

| Form | Bits | Octal base | Bytes | Cycles | Flags | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| [LRM Rr,A](timing.md#lrm) | `01000rrr` | 100+r | 2 | 3 | — | PM A TO Rr |
| [LRS Rr,A](timing.md#lrs) | `01010rrr` | 120+r | 2 | 3 | — | SM A TO Rr |
| [LRX Rr](timing.md#lrx) | `01001rrr` | 110+r | 1 | 3 | — | PM X TO Rr |
| [LSX Rr](timing.md#lsx) | `01011rrr` | 130+r | 1 | 3 | — | SM X TO Rr |
| [LRD Rr,P](timing.md#lrd) | `00010rrr` | 020+r | 2 | 3 | — | PORT P TO Rr |
| [SRM Rr,A](timing.md#srm) | `01100rrr` | 140+r | 2 | 3 | — | Rr TO PM A |
| [SRS Rr,A](timing.md#srs) | `01110rrr` | 160+r | 2 | 3 | — | Rr TO SM A |
| [SRX Rr](timing.md#srx) | `01101rrr` | 150+r | 1 | 3 | — | Rr TO PM X |
| [SSX Rr](timing.md#ssx) | `01111rrr` | 170+r | 1 | 3 | — | Rr TO SM X |
| [SRD Rr,P](timing.md#srd) | `00011rrr` | 030+r | 2 | 3 | — | Rr TO PORT P |
| [BB0 Rr,A](timing.md#bb0) | `11010rrr` | 320+r | 2 | 3 | — | IF Rr BIT0 CLEAR |
| [BB1 Rr,A](timing.md#bb1) | `11011rrr` | 330+r | 2 | 3 | — | IF Rr BIT0 SET |
| [BL0 p,A](timing.md#bl0) | `111001pp` | 344+p | 2 | 2 | — | IF L CLEAR |
| [BL1 p,A](timing.md#bl1) | `111011pp` | 354+p | 2 | 2 | — | IF L SET |
| [BZ0 p,A](timing.md#bz0) | `111000pp` | 340+p | 2 | 2 | — | IF Z CLEAR |
| [BZ1 p,A](timing.md#bz1) | `111010pp` | 350+p | 2 | 2 | — | IF Z SET |
| [BT0 t,A](timing.md#bt0) | `110000tt` | 300+t | 2 | 2 | — | IF TEST t LOW |
| [BT1 t,A](timing.md#bt1) | `110010tt` | 310+t | 2 | 2 | — | IF TEST t HIGH |
| [JMP p,A](timing.md#jmp) | `111100pp` | 360+p | 2 | 2 | — | JUMP PAGE p |
| [JCR Rr](timing.md#jcr) | `11111rrr` | 370+r | 1 | 2 | — | JUMP TO Rr |
| [LRI Rr,#I](timing.md#lri) | `00100rrr` | 040+r | 2 | 2 | — | I TO Rr |
| [XRI Rr,#I](timing.md#xri) | `00101rrr` | 050+r | 2 | 3 | Z | Rr XOR I TO Rr |
| [ANI Rr,#I](timing.md#ani) | `00110rrr` | 060+r | 2 | 3 | Z | Rr AND I TO Rr |
| [CPY Rr](timing.md#cpy) | `00111rrr` | 070+r | 1 | 2 | — | Rr TO X |
| [INR Rr](timing.md#inr) | `10000rrr` | 200+r | 1 | 3 | Z | INCREMENT Rr |
| [ROR Rr](timing.md#ror) | `10001rrr` | 210+r | 1 | 2 | — | ROTATE RIGHT |
| [SHR Rr](timing.md#shr) | `10010rrr` | 220+r | 1 | 2 | — | SHIFT RIGHT ZERO |
| [RRL Rr](timing.md#rrl) | `10011rrr` | 230+r | 1 | 2 | L | RIGHT THROUGH L |
| [DCR Rr](timing.md#dcr) | `10100rrr` | 240+r | 1 | 3 | Z | DECREMENT Rr |
| [XOR Rr](timing.md#xor) | `10101rrr` | 250+r | 1 | 3 | Z | Rr XOR X TO X |
| [AND Rr](timing.md#and) | `10110rrr` | 260+r | 1 | 3 | Z | Rr AND X TO X |
| [EXR Rr](timing.md#exr) | `10111rrr` | 270+r | 1 | 3 | — | EXCHANGE Rr X |
| [SCW #I](timing.md#scw) | `00001000` | 010 | 2 | 3 | — | CONTROL THEN WAIT |
| [SCS #I](timing.md#scs) | `00001001` | 011 | 2 | 3 | — | SEND CONTROL |
| [JSR A](timing.md#jsr) | `00001100` | 014 | 2 | 3 | — | CALL NEXT PC REG |
| [RSR](timing.md#rsr) | `00001111` | 017 | 1 | 2 | — | RETURN PREV PC |
| [NOP](timing.md#nop) | `00000000` | 000 | 1 | 1 | — | FETCH ONLY |
| [EIN](timing.md#ein) | `00000011` | 003 | 1 | 1 | INTE | ENABLE IRQ |
| [DIN](timing.md#din) | `00000010` | 002 | 1 | 1 | INTE | DISABLE IRQ |
| [SEL](timing.md#sel) | `00000101` | 005 | 1 | 1 | L | SET L |
| [REL](timing.md#rel) | `00000100` | 004 | 1 | 1 | L | CLEAR L |
| [SEZ](timing.md#sez) | `00000111` | 007 | 1 | 1 | Z | SET Z |
| [REZ](timing.md#rez) | `00000110` | 006 | 1 | 1 | Z | CLEAR Z |

RRL rotates right through L; ROR wraps bit 0 into bit 7; SHR inserts zero. Conditional branches replace PC only when their condition is satisfied. BL/BZ taken branches also install page p; BT/BB retain PG. JSR increments N and installs its target in the new PC register; RSR decrements N. Neither changes PG. EXR exchanges Rr and X without changing flags.

EIN/DIN/SEL/REL/SEZ/REZ apply their flag strobe at T2 of the following fetch. See [timing conventions](timing.md) before interpreting instruction boundaries. Detailed evidence and uncertainties: [existing catalogue](../instruction-set.md).
