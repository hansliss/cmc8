# Architecture model v005

Predecessor: [v004](model-v004.md), preserved unchanged. This complete
numbered package adds NOP (00) and variable instruction lengths. It requires
only Python's standard library.

```sh
python3 -m cmc8 --model v005
python3 -m cmc8 --model v005 --json
python3 -m unittest discover -s tests -v
```

The eight-subdivision demonstration executes NOP at program address 1FF.
PC advances from FF to 00, PG remains 1, and R3 remains A6. Numbers are
hexadecimal. No operand byte is needed in memory.

## Evidence and chosen controls

Printed p.67, figure 5.1 (`Page_073.jpg`) lists NOP as `00000000`, one
cycle, no operation and no affected flags. Printed p.51, section 3.2
(`Page_057.jpg`) explicitly says instruction fetch is common through T5,
and one-cycle instructions execute during F0T6/T7. Thus NOP fetches its
opcode and increments R(N), then returns to the next fetch without F1/F2.

Hypothesis H004 uses the existing fetch controls through T5:

| Slot | MOPs | Function |
| --- | --- | --- |
| F0T0 | 18,21 | R(N) drives DI |
| F0T1 | 18,21,14 | DI → AB |
| F0T2 | 18,21,24 | PME asserted |
| F0T3 | 18,21,7,10,24,12 | PC+1 → BR |
| F0T4 | 4,18,29,22,24 | BR → R(N); ready check |
| F0T5 | 1,24 | DB → IR; final value retained at end of T5 |
| F0T6 | none | PME released; no additional transfer |
| F0T7 | 30 | Phase reset to F0 for the next instruction |

The executable table retains the inherited repeated 24 in the printed
fetch row; it asserts PME only once. MOP29 retains the explicit always-ready
assumption. IR and BR therefore change during NOP, as required for fetch
and increment, even though it has no additional programmer-visible effect.

No full NOP MOP table has been found in these inspected pages. **T6 idle
and MOP30 at T7 are derived choices, not directly documented NOP signals.**
The minimal tail leaves AB at the fetched opcode address until the next
fetch's T1. An alternative is to retain MOP6 at T6 and preload AB from BR,
as in LRS. That would preserve NOP's architectural result but change AB's
external timing. This alternative remains recorded here; v005 chooses the
minimal tail pending further timing evidence.

## Sequencer change

Decode happens at the start of F0T6, using the IR value captured at the end
of T5, before choosing that slot's instruction-specific controls. All
supported instructions share fetch only through T5.

At T7, a captured MOP30 phase reset wins over ordinary phase advancement.
`run_instruction()` steps until the next F0T0 instead of always running 24
subdivisions. NOP returns eight records; all six load/store instructions
still return 24. There is no direct PC update or special instruction-level
shortcut: the increment still runs through the MOP-driven datapath.

Only exact opcode 00 is decoded as NOP. Neighboring unimplemented opcodes
are not treated as NOP. An absent opcode remains unknown and causes a
capture error, rather than defaulting to zero.

## Validation and limits

Tests cover every N selector, all pages, boundary PC values and wraparound,
unchanged other registers/flags and all external data spaces, the fetch
control window, consecutive NOPs and mixed NOP/LRS/SRS programs. A delayed
opcode tests IR's end-of-T5 deadline. The six prior instruction families are
compared against preserved v004 state and slot traces on every page.

The existing always-ready, peripheral-adapter, timing, ALU and electrical
limitations remain. In particular, this is not new evidence about WAIT,
interrupts, HALT, reset, handshakes or the original silicon's NOP tail.
