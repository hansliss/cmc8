# Validation and console smoke test

## Native production-source checks

```sh
cmake -S x7_traffic -B x7_traffic/build-host -DX7_HOST_TESTS=ON
cmake --build x7_traffic/build-host -j
ctest --test-dir x7_traffic/build-host --output-on-failure
```

Nine native tests run production CPU, scene, renderer, platform shell,
framebuffer ownership and shared-volume code with ASan/UBSan enabled by default.
LeakSanitizer is disabled for ptrace environments, following the SDK.

The traffic test executes the complete literal program for both T1 and T3,
including all nine delay-routine calls, and checks all seven ED4 writes against
the independent v018 record. For T1 these occur at subdivisions
53, 261, 1254541, 3763053, 7525797, 10034309 and 11288589. The run, including the
same initial/final idle polling, completes at subdivision 11288752.
T3 adds the expected 16 slots for the first unsuccessful T1 branch.
It also checks pause, slot/instruction stepping, a second of exact clocking,
vehicle sensors/red stopping, restart and renderer buffer guards. Additional
checks verify phase boundaries (including MOP31), F0T0-only instruction snapshots,
manual slot inspection and identical CPU/world timing in both display modes.
Speed checks cover exact ½×/1×/4×/16× slot counts, fractional preservation across
rate changes, Y while paused, single-slot stepping independent of speed, reset
to 1×, and identical CPU state at equal CPU times. Separate checks require
identical unobstructed car motion and arrival schedules at equal host times
across all CPU speeds, fixed traffic milliseconds, the doubled speed range,
and no traffic advance during pause or manual CPU stepping.

Eight firmware-mock scenarios check normal app exit, GUI load failure,
framebuffer allocation failure, raw-input setup failure, silent operation even
without libsound, malformed input, retained display storage on stop failure, and sustained overload that previously
starved all rendering.
Shared volume works and is saved even while paused; no example settings or
sound output is created. These tests do not emulate console firmware execution.

## Optional research oracle

From the full research repository (not needed on the console or normal builds):

```sh
python3 x7_traffic/tools/export_model.py --check
python3 x7_traffic/tools/verify_model.py x7_traffic/build-host/traffic-host
```

The second command compares 16,000 **consecutive T subdivisions** with the Python
v018 board: asserted MOPs, registers, phase/timing, leading and trailing wire
values, unknowns and ED4. It includes sensor assertion/release, reset, initial
loads/stores, branching, the delay arithmetic and DCR's selected zero detector.
Full-cycle native checks independently cover the later light writes and returns.

Render the actual production renderer on the host:

```sh
x7_traffic/build-host/traffic-host /tmp/traffic.ppm 1800
```

The last argument is the number of 60 Hz host ticks (1800 = 30 simulated seconds).
The result is a standard PPM image; no image library is required. `docs/preview.png`
is a PNG conversion of such a frame, not a separate mockup or different renderer.

## Cross-build and device test

```sh
cmake -S x7_traffic -B x7_traffic/build
cmake --build x7_traffic/build -j
```

The target ELF passes the SDK's automatic post-link checks. No host/Linux libc
startup or compiler runtime helpers are linked; the freestanding SDK helpers
supply memcpy/memset. A source-only app+SDK copy is also buildable independently
of the Python research package.

The following still needs real hardware:

1. Copy `build/card/` contents onto a compatible console's card, preserving
   existing apps/settings. Launch CMC8 MOP Traffic from Card Launcher.
2. Confirm the 480×272 layout is legible, colors are correct, main road starts
   green, and the first side-road cars eventually request the documented cycle.
3. Start pauses both worlds. Tap A repeatedly: F/T, MOP cells and captured
   registers advance one slot at a time. B reaches an instruction boundary.
4. Resume and press X to switch PHASE / INSTR snapshots. Confirm the screen
   keeps updating in both modes, CPU time advances at the same rate, and volume
   remains responsive. Compare simulated SEC with wall time. Pause and use A
   in both modes to inspect exact slots; B should finish at F0T0.
   Y cycles 1× → 4× → 16× → ½× → 1×. Confirm CPU SEC changes pace while
   traffic motion, arrivals and the left SEC clock retain the same rate.
   Lights should change faster/slower relative to cars, and display updates
   should continue at higher CPU rates. Cars should visibly move twice as fast
   as in the earlier build.
   The multiplier is requested speed; achieved rates still need device testing.
5. Hold Up/Down to assert T1/T3. Release and confirm normal demand behavior.
   Select restarts the scene. Keep occasional real input during longer tests;
   the stock firmware may have an inactivity timeout.
6. While paused, test physical volume buttons and overlay. Hold Home to exit;
   ensure the launcher and another app still work. Recheck shared volume there.
7. If startup fails, inspect `/mnt/card/cmc8-traffic-error.txt`. For additional
   bounded startup/cleanup logging rebuild with `-DX7_DEBUG_LOG=ON`.

Device timing, panel appearance, inactivity behavior and firmware compatibility
cannot be established by the native tests or successful ELF validation.
