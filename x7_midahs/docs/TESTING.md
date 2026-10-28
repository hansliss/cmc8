# Checks and console smoke test

## Native build

```sh
cmake -S x7_midahs -B x7_midahs/build-host -DX7_HOST_TESTS=ON
cmake --build x7_midahs/build-host -j
ctest --test-dir x7_midahs/build-host --output-on-failure
```

Ten tests compile the production C sources, with assertions and ASan/UBSan.
LeakSanitizer is disabled for ptrace environments, matching the SDK.

- Monitor integration exercises press/release, one action per held key, all three
  memory spaces, four-digit addresses, data entry, cross-page GO, ROM protection,
  KEX recovery, and manually entering then executing the entire SWITCHES program.
- Panel tests operate actual controls: GO through A, navigation to switches,
  lamps tracking input, KEX return, reachability of every control, held-key focus
  locking, quick-tap retention, pause and rendering buffer guards for all 34 controls.
- Hardware-control tests exercise each TEST branch, WP vs storage writes, RESET
  preservation, IRQ vector/return behavior, HALT/SS one-shot grants, MEMR-retained
  grants, SCW waiting without repeated strobes, clock modes, manual pulse counts
  and slow-clock keyboard retention.
- Help tests cover opening/paging/exit, frozen CPU/virtual clock, preservation of
  debugger pause and user RAM, exit-button isolation and framebuffer guards on
  both pages.
- Asset tests cover successful short reads, RGB565 decoding, absent/truncated/
  oversized resources, read errors, impossible read counts and close failure.
- Eight platform-boundary scenarios use this app's real shell and SDK framebuffer/
  volume implementations: normal exit, startup failures, malformed raw input,
  silent operation, display-stop retention, and presentation under sustained load.

The full research repository offers three additional checks:

```sh
python3 x7_midahs/tools/export_programs.py --check
python3 x7_midahs/tools/export_reference.py --check --coverage x7_midahs/build-host/midahs-host
python3 x7_midahs/tools/verify_cpu.py x7_midahs/build-host/midahs-host
```

The program exporter checks the bundled bytes against the web HEX images. The CPU check compares
462 ordinary instruction result/cycle cases with signaling v018, including PC
register aliases and page wrapping. Deferred flag instructions and external control handshakes are outside that
single-instruction comparison; dedicated control tests cover those functional
paths, and monitor integration exercises SCS's KEX convention. The reference check validates the generated card and executes all 256 opcode
bytes through production C: 239 must work with the catalogue cycle count, and
17 must fault. Normal builds need neither the research package
nor the book files.

Produce a frame with the actual production renderer:

```sh
x7_midahs/build-host/midahs-host /tmp/midahs.ppm
```

Optional arguments are the raw photo path, selected control index (0–33), and
help page (0 or 1). Supplying a help page renders that reference screen.
The standard PPM image needs no host image library. `preview.png` is a PNG
conversion of a production-rendered frame, not a mockup.

## Target and isolation

```sh
cmake -S x7_midahs -B x7_midahs/build
cmake --build x7_midahs/build -j
```

The freestanding MIPS ELF passes the SDK checks for O32 layout, entry, load window,
BSS, unresolved symbols and 289 trap encodings. A source-only copy of this app plus
the SDK is sufficient; its normal builds use committed monitor data and artwork.
Optional asset conversion needs Pillow; building/installing does not.

## Hardware smoke test

1. Copy all of `build/card/` contents, including `res/midahs/panel.rgb565`, onto a
   compatible console's SD card. Launch Midahs from Card Launcher.
2. Check the photo, crisp keypad overlays, sidebar numbers and cyan pointer.
   Initially GO is selected and data reads 023. Check the photo at actual screen
   size: layout/contrast cannot be established by an emulator screenshot alone.
3. Tap A: the status becomes USER. Left selects KEX; continue across the new board controls to the ED3 switches.
   Up/Down choose bits and A toggles them; the left ED4 lamps should follow ED3.
4. Hold a keypad key and confirm moving the D-pad cannot retarget it. Release A;
   commands should act once. Try quick taps and direction repeat.
5. Press B: KEX AD returns, with switches/lamps retained. Navigate to + and read
   the bytes `023 003 033 004 360 000`. Try DA and an octal memory edit, then GO.
6. Select CLOCK and cycle HIGH/MANUAL/LOW. In MANUAL, tap CL and check T0–T7
   advances once per press; registers change only when an instruction finishes.
   LOW should advance eight pulses per second. Return to HIGH afterward.
7. Try MEMR high/low, HALT low and SS high→low, and RESET low/up. Check status
   labels and recovery. Toggle TEST inputs with a program using BT0/BT1. For INT,
   use a prepared handler and EIN. SCWR should only stall a program using SCW.
   WP must prevent PM edits but not SM/I/O; turn it off before using GO.
8. Check Start pause, Select restoring the default program, volume overlays while
   paused, and holding Home to exit. Confirm the launcher and another app work.
9. Open the instruction card with either shoulder. Both pages should be legible,
   lowercase selector fields visible, and CPU progress frozen. Page with L/R;
   B should return without entering KEX. Test volume while reading the card.
10. If necessary, inspect `/mnt/card/midahs-error.txt`; rebuild with
   `-DX7_DEBUG_LOG=ON` for bounded startup/cleanup logs.

Actual pointer feel, physical button mapping, legibility and firmware compatibility
still require this device check. The original X7 SDK is not modified.
