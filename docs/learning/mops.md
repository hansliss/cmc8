# CMC8 MOP list

[Study guide](README.md) · [Instructions](instructions.md) · [MOPs](mops.md) · [Timing](timing.md) · [Datapath](processor.svg)


Numbers 1–50 come from figure 4.2 (printed p.38), 51–55 from the branch circuit (p.72), and 57 from the shift circuit (p.79). No MOP56 has been identified; no number is invented for it. These are functional controls, not a claim that each is one physical wire. Short names describe the selected v018 interpretation.

| MOP | Short name | Explanation |
| --- | --- | --- |
| 1 | DB→IR | DB → IR |
| 2 | DB→BR | DB → BR |
| 3 | BR→B | BR → ALU input B |
| 4 | BR→DI | BR → DI |
| 5 | ~BR→DI | complement BR → DI |
| 6 | BR→AB | BR → AB |
| 7 | DI→A | DI → ALU input A |
| 8 | A XOR B | DI XOR BR in ALU |
| 9 | A AND B | DI AND BR in ALU |
| 10 | A+1 | DI + 1 in ALU |
| 11 | SHR | shift one step right in MUX |
| 12 | MUX→BR | Capture the ALU result after the shift/insert MUX in BR. |
| 13 | A0→MUX7 | Wrap ALU result bit 0 into MUX bit 7 (ROR). |
| 14 | DI→AB | DI → AB |
| 15 | IR[1:0]→PG | IR bits 0–1 → PG |
| 16 | N+1 | N + 1 → N |
| 17 | N−1 | N - 1 → N |
| 18 | select PC | Select R(N), the current program counter. |
| 19 | select Rr | Select the register addressed by IR[2:0]. |
| 20 | select X | Select R7, also called X. |
| 21 | R→DI | register → DI |
| 22 | DI→R | DI → register |
| 23 | DI→DB | DI → DB (DBDIR) |
| 24 | PME | PME asserted |
| 25 | SME | SME asserted |
| 26 | EDE | EDE asserted |
| 27 | WRITE | WRITE asserted |
| 28 | INTR→INTA | At F0T0 clock pending INTR into INTA; raw /INT sets INTR separately when enabled. |
| 29 | MEMR? | At T4 test memory wait; shared fetch continuation also observes HALT/single-step. |
| 30 | 0→F | 0 → phase |
| 31 | 2→F | 2 → phase |
| 32 | Z←zero | Set Z when the ALU result is zero; DCR instead uses the final DI value (H014). |
| 33 | L↔shift | Insert old L into MUX bit 7 and capture ALU bit 0 as new L (RRL). |
| 34 | 1→L | 1 → L |
| 35 | 0→L | 0 → L |
| 36 | 1→Z | 1 → Z |
| 37 | 0→Z | 0 → Z |
| 38 | 1→INTE | 1 → INTE |
| 39 | 0→INTE | 0 → INTE |
| 40 | 0→DI | 0 → DI |
| 41 | 2→DI | 2 → DI |
| 42 | 0→PG | 0 → PG |
| 43 | 0→MUX7 | 0 → MUX bit 7 |
| 44 | 0→PC | Clear the selected current PC register; reset sequence instead uses 40/18/22. |
| 45 | 0→N | 0 → N |
| 46 | 0→INTR | 0 → INTR |
| 47 | RESET? | Sample active-low RESET at T7; select a separate reset cycle. |
| 48 | 0→SSE | Clear single-step enable after accepting a step (selected H023 timing). |
| 49 | 1→SSE | Rearm single-step enable after SS release (selected H023 timing). |
| 50 | SCWR? | Sample /SCWR at T4; high repeats the control-word wait cycle. |
| 51 | Z→cond | Z → branch condition input |
| 52 | L→cond | L → branch condition input |
| 53 | TEST→cond | Select TEST[IR[1:0]] and present it through T to the condition circuit. |
| 54 | DI0→cond | DI bit 0 → branch condition input |
| 55 | cond XOR IR3→H | At T2 latch condition XOR IR bit 3. H=0 permits the branch write at T6. |
| 57 | 0→MUX7 | Figure 5.11 label for zero insertion; functional alias of 43 in this model. |

A and B here mean ALU inputs, not address bytes or register selectors. MOP11 shifts the ALU output through the MUX; MOP12 captures that MUX output in BR. MOP3 and MOP7 enable the two ALU operands; MOP8/9/10 choose the operation. MOP7 alone allows A to pass through. MOP5 complements BR before driving DI.

## Named controls without identified MOP numbers

| Control | Meaning |
| --- | --- |
| EXR A.capture | Capture DI into the added ALU input-A latch at F2T0 (H019). |
| EXR A.held | Select the held A value instead of live DI at F2T5 (H019). |
| DCR zero=DI | Use final DI for MOP32 at F2T6 (H014; omitted zero circuitry). |
| STRCS | Control-byte strobe at SCS/SCW F1T6; an external receiver may use a latch. |
| clear INTA | Reset-cycle T0 acknowledgement clear. |
| IRQ set gate | INTE and active-low INT set pending INTR asynchronously. |
| HALT observation | Internal HALT latch and SSE handshake govern fetch continuation; H023 reconstructs omitted timing. |

The external control-byte receiver is not the added internal EXR latch. See [the diagram](processor.svg) and [v018](../model-v018.md).
