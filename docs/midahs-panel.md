# Midahs-style functional front panel

[The panel fixture](../cmc8/boards/midahs.py) extends the
[board harness](traffic-harness.md) with the book's keyboard, display
registers, switches and lamps. Programs still run through the unchanged
v018 processor. The fixture is a scriptable logical front panel, with a
small keyboard demonstration:

```sh
python3 -m cmc8.boards.midahs GO 0 7 +
python3 -m unittest tests.test_midahs_panel
```

The demonstration runs the six-byte program on
[p.129](../bookpages/Page_135.jpg): LRD R3,ED5; SRD R3,ED2; JMP0,000.
Pressing GO displays361 octal; pressing0 displays360; pressing7 displays376;
pressing+ displays367. Releasing a key presents377 in this fixture.

## Peripheral map

| Port | Function | Modeled behavior |
| --- | --- | --- |
| ED0 | Page display register | Byte read/write; octal display digits individually enabled by ED6 |
| ED1 | Address display register | Byte read/write; three octal digits |
| ED2 | Data display register | Byte read/write; three octal digits |
| ED3 | Input switches | External byte input; CPU writes rejected |
| ED4 | Output lamps | Eight latched output bits; no assumed reset value |
| ED5 | Keyboard | Functional key-code input; CPU writes rejected |
| ED6 | Digit enables | Output latch; low three bits enable ED0's digits |

[Figure7.13, p.127](../bookpages/Page_133.jpg) places bit0 at the leftmost
page-display digit, bit1 at the middle and bit2 at the rightmost. Thus007
enables all three, while004 enables only the rightmost. ED1 and ED2 remain
visible. The other ED6 bits are retained but not assigned additional display
functions. [Pages128–129](../bookpages/Page_134.jpg) demonstrate both writes
to display registers and readback/copying between them.

`press_key()`, `release_key()` and `set_switches()` supply external stimulus.
Only one key is held at a time in this fixture. The key table follows
[figure7.15, p.130](../bookpages/Page_136.jpg), with digits0…7 and
GO/AD/DA/+. KEX is a separate board function, not an ordinary keypad entry.

The observed key values have a high nibble of F and the low-nibble codes
shown by the book. Idle FF is supplied explicitly to support the documented
keyboard-polling sequence. It is not a simulation of floating bus voltage,
74C922 matrix scanning, debounce, rollover or analog pullups. The book's
keyboard circuit and data-sheet comparison are on
[pp.130–131](../bookpages/Page_137.jpg).

## Observation and initial conditions

`snapshot()` returns the three latched display groups, the bus-address and
bus-data observations, the last observed timing subdivision and the eight
lamp bits. Together these expose the nine register-display digits and eight
bus/timing digits corresponding to the book's17-digit panel description.
Unknown visible values appear as question marks; a disabled page digit is
a space. This is functional display state, not a simulation of488Hz display
multiplexing or segment currents.

The fixture supplies the same stated reset and quiet-IRQ setup as the
traffic application. Display latches, lamps and input switches are not
silently cleared by CPU reset. The keyboard's idle value is an explicit
fixture setting. Program page3 is read-only, following the book's PROM page;
its contents must be supplied by the experiment.

All timed execution passes through board stepping, so output changes are
observed at committed bus writes. This is important for display-copy and
keyboard tests: the fixture does not inspect the intended instruction and
supply its expected result directly to CPU registers.

## Checked examples and scope

Seven tests check:

- The p.126 ED3→ED4 switch/lamp loop with changing input values.
- The p.129 ED5→ED2 keyboard/display loop for all twelve pictured keys.
- The ED2→ED1 bidirectional display-register copy.
- All three ED0 digit-enable positions, with ED1/ED2 unaffected.
- Unknown peripheral state across CPU reset and invalid key handling.
- The figure8.10 press/release polling subroutine on page3, using the
  accepted E004/E005 corrections. Real JMP/JSR/RSR execution reaches and
  returns from the routine; a held key does not complete the call early.

The monitor's complete KEX program, KEX-specific memory-mode remapping,
external PROM-card overlays, special KEX/reset/SCWR circuitry and an
interactive graphical faceplate remain separate work. The processor's own
HALT/SS/RESET/INT interfaces are available through the attached CPU object.

Validation for this pass: **343 tests pass** across the full suite. The
46 generated instruction-reference artifacts are current. Numbered CPU
models remain unchanged.
