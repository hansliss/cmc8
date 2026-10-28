# Emulator, panel and artwork

## Instruction execution and monitor

`core/midahs.c` ports the instruction-level behavior of `demos/shared/cpu.mjs`
and the board wiring from `demos/midahs/board.mjs` into portable C. Ordinary
instruction results and machine-cycle costs follow the established model.
JSR/RSR change the selected PC register; no host stack replaces that mechanism.
The board has four pages of program and storage memory and ports ED0–ED6.

`generated/programs.h` preserves the browser's assembled monitor and SWITCHES
HEX bytes. The monitor is a **reconstruction**, not the original KEX ROM dump.
Its keyboard routine includes the accepted figure-8.10 corrections. All command
recognition, address/data entry, writes, display updates and GO are executed
by the CPU. The UI only operates keyboard/switch inputs or the KEX board button.

The inherited functional KEX hypothesis remaps data accesses according to ED6
and the selected ED0 page field; opcode/operand fetches stay in physical program
memory so the page-3 monitor can run. Program page 3 rejects writes. GO builds
the book's page-2 jump stub at octal 316/317, clears KEX with SCS and jumps through
it. The user must reserve those two bytes. KEX functionally installs RESET plus
the injected JMP3,363 entry outcome and releases the keyboard, preserving RAM
and external latches. The reconstructed startup selects program address zero.

Startup RAM, registers and external latches are explicit demo zeros; the idle
keyboard is FF. Unpopulated inputs read FF, and display/output-latch readback is
permitted as in the browser fixture. These are functional conveniences rather
than electrical measurements. Invalid instructions or writes to unsupported
ports/ROM stop with a sidebar error. SCW now uses the interactive SCWR input. B/KEX recovers without erasing RAM.

There are no MOP traces, analog keyboard debounce, display multiplexing or
external PROM overlays. L/Z flag instruction effects remain represented at boundaries; EIN/DIN take
effect at the following ordinary fetch, after its interrupt-acceptance check. The added pin controls are functional approximations,
not a port of the complete v018 edge sequencer.

## Clock pulses, waits and pin controls

The high-rate scheduler distributes 125,000 virtual T pulses per second across
60 host ticks. Each ordinary instruction reserves eight pulses per documented
machine cycle and commits register/port effects at its end. LOW supplies eight
pulses per second; MANUAL supplies none until CL is pressed. The chosen low
frequency is for visibility, not a recovered oscillator specification. The T
readout counts virtual pulses modulo eight; it does not expose MOP phase timing.
If a wait becomes ready during a reserved clock group, the implementation
reserves any additional cycles required before committing a longer instruction.

Pin changes are settled at functional event boundaries, not the original
T2/T3/T4 capture edges. In particular, reads, writes and control strobes are not
broken into independently timed MOP transfers. A change during an in-flight
instruction can defer or replace that pending atomic event and can add latency.
This is suitable for interactive instruction-level experiments but not signal
race or bus-timing research; use Python v018 for those questions.

- RESET low clears N, PG, R0 and INTA in separate one-cycle reset events. Other
  registers, RAM, flags and pending INTR survive. Reset aborts SCW waits and can
  recover a stopped opcode/ROM error. KEX button entry remains the functional
  reset-plus-injected-jump action, preserving physical switch levels.
- INT low with INTE set latches INTR. Entry is a one-cycle event that disables
  INTE, clears INTR, increments N and writes 002 to the new PC register without
  changing PG. INTA is cleared at the next ordinary boundary. No host stack or
  automatic handler is invented. EIN therefore does not skip its following
  instruction when INT is already low.
- MEMR high stalls before an instruction executes. No fetch/PC update is
  committed while blocked. This approximates the source's internal read waits.
- HALT low blocks instructions. SS high arms SSE; SS low consumes that arm to
  grant one instruction. A held low SS does not repeat, and a grant survives a
  MEMR wait. Interrupt/reset entry and pending SCW completion are separate events.
- SCW emits its SCS-style control once, then, if SCWR is high, holds a pending
  acknowledgement wait without consuming another opcode or repeating the strobe.
  Low SCWR completes that wait. SCS never waits. Reset escapes a pending SCW.
- WP silently inhibits program-memory writes, including the monitor's GO stub;
  it does not protect storage/I/O. The sidebar reports a blocked write. Page 3
  remains read-only regardless of WP.

The input defaults are RESET/INT/HALT/SS high, MEMR/SCWR low, TEST inputs low,
WP off and HIGH clock. These are explicit demo board settings, not power-on
claims. Select restores them; KEX preserves them. Debugger Start pauses automatic
clocking, but explicit CL pulses remain possible in MANUAL mode.

## Keyboard interaction

A press is forwarded as the book's keyboard code and retained until A release,
with at least two host ticks for short taps. During KEX it also waits for an
actual ED5 read, preventing slow/manual clocking from losing a press. Once A is
released, navigation remains possible so you can reach CL while the key is pending.
Only a physically held key locks pointer movement. Programs that do not read the
keyboard do not latch the UI forever. Raw transitions retain their original order.
Start/Select retain the SDK's 50 ms qualification and volume is filtered first.
KEX remains a board action rather than a keypad code.

## Photographic presentation

`resources/panel-source.jpg` is a copy of the owner's 391×272 perspective-corrected
scaled photograph from `Midahs_panel/`. No geometry is derived from the provisional
SVG as a verified mechanical dimension. The photo occupies its native size,
leaving 89 pixels for a readable sidebar. Overlay coordinates are presentation
choices manually aligned to that photograph, not measurements of a real panel.

`panel.rgb565` is the same photo converted to packed little-endian RGB565. The
normal build ships it without requiring a decoder or Pillow. Optional regeneration:

```sh
python3 x7_midahs/tools/convert_photo.py       # Requires Pillow on the host only.
python3 x7_midahs/tools/convert_photo.py --check
```

The device loader bounds all reads, accepts short reads, checks EOF and close,
and exposes the photo only after the complete expected image succeeds. A missing,
truncated or oversized resource leaves the fallback view. Rendering decodes byte
pairs explicitly, so host/target endian assumptions do not leak into the image.

ED0/ED1/ED2 overlay digits and ED3/ED4 states come from the actual board latches.
The top PG/ADR and bottom DATA miniature windows show the next instruction
address/byte, derived at instruction boundaries. They are not sampled physical
address/data bus signals. The sidebar is the authoritative readable duplicate
of the small register digits and selected control. No additional CPU inspector
or MOP visualization is included.

## Other physical controls visible in the photograph

The round item immediately beneath KEX is the KEX pushbutton (printed pp.133–135,
figure 7.19). A separate KEX-active lamp is described on p.136; it is not that
button. The demo draws the button neutrally and reports monitor state in the
sidebar rather than coloring the button as a status lamp.

All of the following controls are now selectable and functional:

- TT0–TT3: four direct TEST inputs for BT0/BT1.
- CL pushbutton and H/manual/L clock selector, described on p.118.
- RESET, INT, MEMR, HALT, SS and SCWR: the six remaining CPU switches, giving
  seven switches including the clock selector (pp.114/118).
- WP: program-memory write protection, explicitly identified on p.115.

Their functional approximations are listed above. The editable display positions
and overlaid levers remain presentation coordinates, not mechanical measurements.

## Reference card and opcode coverage

The two reference screens use `generated/reference.h`, exported from the authored
instruction catalogue by `tools/export_reference.py`. Every family has an operand
form, bit pattern, octal base/selector, changed flags, bytes, base cycles and a
short description. Lowercase r/p/t glyphs distinguish selector bits from literals.
Normal builds do not read the catalogue or require the OCR/book inputs.

Shoulder buttons open/page the card. CPU pulses and auto-navigation are frozen
while it is open. Closing the card preserves debugger pause and does not forward
B, A, Start or Select to their ordinary actions. Shared volume and Home handling
remain in the platform shell, outside the help gate. A held keypad is released
when entering help; any already-read key is processed when execution resumes.

All 43 families, covering 239 encoded bytes, have production implementations.
The host `--opcodes` fixture checks one execution of every byte with ready memory,
SCWR low and ordinary input conditions, and compares base cycle costs with the
catalogue. Unassigned bytes must fault. Existing differential/monitor/control
tests verify results and functional board paths beyond this decoding check.

## Platform

The app-local shell retains the X7 SDK's startup, ABI, framebuffer ownership,
raw-input mode, volume path and cleanup. It follows the traffic app's non-starving
presentation policy. Changes for this app add resource loading and forwarding
individual raw transitions to the keypad before their batch ends. No SDK sources
are modified. The app is silent; sound initialization is disabled. No shared
volume defaults or example settings are staged.

All resource access uses `/mnt/card/res/midahs/`. Optional logs and fatal startup
errors use the SDK's generated `/mnt/card/midahs-log.txt` and `midahs-error.txt`
paths. Shared volume remains `/mnt/card/res/clauncher/volume.cfg`.
