# Processor port and presentation

## MOP execution

`core/cpu.c` evaluates DI, the selected register, DB, ALU and MUX from old state
and the active numbered controls. It then commits leading-edge captures
simultaneously. IR alone also samples the trailing endpoint, matching the
research simulator's transparent F0T5 latch model. Register writes are enabled
only by MOP22 and take their values from DI; opcode decoding only selects a
micro-operation table. Light values are never supplied by an expected timeline.

`generated/tables.h` contains the v018 held-level tables for NOP, LRM, SRD, LRI,
INR, DCR, JSR, RSR, BT0/BT1, BZ0/BZ1 and JMP, and the figure-4.21 RESET cycle.
The same generated header preserves all 75 literal traffic-program bytes.
`tools/export_model.py` exports these from the research sources; it does not
translate instructions into precomputed effects. Normal builds use the checked-in
header, so the book files and Python processor are not runtime/build inputs.

The port includes the physical H interpretation (zero means taken), conditional
MOP22/MOP15 at F2T6, and MOP31 phase skipping while T continues. It inherits the
selected H014 DCR DI zero detector. WRITE data/address remain stable through the
strobe and ED4 changes only when WRITE falls. Literal delay instructions all
execute. Missing program bytes and undriven signals are -1, displayed as `---`.
Unknown power-on registers remain unknown until the actual reset/MOP captures
initialize them. The table-based PC/N return mechanism is not replaced by a C
call stack. On a CPU fault the app stops CPU/vehicle progress until restart.

This fixture has released RESET, quiet INT, ready memory, no SCWR device and
no HALT/single-step request circuit. It shows the applicable MOP28/MOP29/MOP47
controls but does not implement their alternative interrupt/wait/reset paths.
INTE/INTR are implicitly quiet board conditions rather than unknown requests.
The UI pause/step buttons are debugger controls, not physical CMC8 SS wiring.
Startup executes the eight-subdivision RESET cycle before fetching address zero.
No EXR, undocumented ALU latch, general storage space or device read path is
required by this literal program. Only the selected transfer/ALU functions are
implemented; this must not be described as a complete hardware CMC8 emulator.

## Inspector

F/T and the instruction name identify the **last executed slot**. Register
values are its captured state, while DI/DB/ALU/MUX show the trailing-endpoint
combinational values. An undriven bus does not retain the last byte for display.
The selected register is highlighted and active MOP cells are lit yellow.
MOPs not implemented by the selected traffic subset remain dim in the overview.
MOP56 is unassigned in the source list and is never asserted.

X chooses which completed boundary refreshes the inspector snapshot: PHASE
captures each phase transition (including F1T1→F2T2) and each T7→T0 wrap; INSTR
captures only returns to F0T0. F/T still identifies the last executed slot in
that snapshot, so an instruction snapshot normally shows the preceding F2T7,
not the upcoming fetch's controls. A single-slot step overrides the snapshot
with that precise slot, regardless of the selected automatic mode.

Many boundaries pass between presentations. The screen shows the latest
qualifying snapshot at up to 30 Hz, rather than attempting a physical redraw
for every processor phase. A/B stepping makes individual captures inspectable.
The live traffic scene uses its own fixed-rate clock rather than the held
inspector snapshot. The left SEC readout is traffic time; CPU SEC at the bottom
of the processor panel is current CPU time. The renderer uses the SDK's built-in
5×7 font and CPU RGB565 drawing, not GPU MMIO or external artwork.

## Independent processor and traffic clocks

A CPU subdivision is 8 microseconds: 125,000 slots per CPU second. The default
rate is 1×, not an unthrottled host benchmark. Y selects 1×, 4×, 16× and ½×.
Internally these are 2, 8, 32 and 1 half-speed units. The fixed-tick accumulator
uses a common denominator of 120, preserving fractional slots across speed
changes. Sixty host ticks execute exactly 62,500, 125,000, 500,000 or 2,000,000
subdivisions at the corresponding rate. Every slot still uses the MOP engine.

Traffic is deliberately a visualization with a separate clock. Every 60 host
ticks produce 100 ten-millisecond traffic updates, independently of the CPU
multiplier. Car positions, arrivals and the left SEC readout use that traffic
clock. Speeds are 14–26 pixels per traffic second, twice the previous range.
Cars still obey the current ED4 outputs; their positions drive actual T1/T3
inputs for the next CPU work batch. Manual demand is sampled before actions
and ticks, including while paused. Changing CPU speed changes light durations
relative to traffic, an intentional presentation choice rather than a claim
about physical elapsed time in the original Midahs system.

Pause freezes both clocks; manual slot/instruction stepping advances only the
CPU. X changes only inspector snapshots. If the host cannot sustain a requested
CPU rate, normal scheduling constraints still apply; the shared host scheduler
bounds catch-up and checks its work budget between ticks. The header shows the
requested CPU multiplier, not measured host performance. Compare CPU SEC against
the traffic SEC readout to observe the relative clock rates.

The app deliberately replaces the SDK's backlog-dependent draw gate with its
same 30 Hz presentation cadence regardless of simulation debt. The old gate
could defer all rendering indefinitely under sustained load, which explains
the reported frozen screen at 4×/16×. Input, volume overlays and inspector frames
now retain presentation opportunities even when simulation falls behind.

The 32-bit slot/time counter wraps after about 9.5 simulated hours. The scene's
fractional clocks and arrival countdowns keep working; the CPU SEC counter and
stored write timestamp wrap with it. Traffic milliseconds wrap independently
after about 49.7 days of unpaused traffic time. This is a demo observation
limit, not a processor reset.

## Platform provenance

`app/platform.c` is an app-local adaptation of the SDK shell. Changes are limited
to the portable scene/actions interface, app identity and removal of the example's
local settings/tone actions. Audio initialization is compiled off. CRT, O32
assertions, linker layout, library order, framebuffer acquisition/ownership,
raw input, Start/Select filtering, volume handling and cleanup are retained.
The draw scheduling exception is explained above.
SDK components are compiled directly from the separately supplied SDK directory.
The host firmware boundary fixture is adapted from its platform tests.

No SDK sources or APIs are changed. The SD resource namespace is
`/mnt/card/res/cmc8-traffic/`; this version has no resource files or local config.
The SDK's diagnostic paths remain `/mnt/card/cmc8-traffic-error.txt` and optional
`/mnt/card/cmc8-traffic-log.txt` (`-DX7_DEBUG_LOG=ON`). Shared volume is always
`/mnt/card/res/clauncher/volume.cfg`, never supplied in the card package.
