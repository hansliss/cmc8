# Browser traffic demo

A static, entirely client-side traffic scene controlled by the book's literal
CMC8 program. No Python runtime, JavaScript packages or build step is needed
in the browser. Serve the repository directory:

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000/demos/traffic/>. Loading modules and the default HEX
requires HTTP rather than opening index.html directly. The demo directory can
also be copied by itself to any static web host; cpu.test.mjs is only needed
for repository development tests.

Cars have reproducible random arrival times and desired speeds. Main-road
approaches retain intervals of 3–12 simulated seconds each. Side-road
approaches each use 120–180 seconds (150 seconds on average), giving a combined
side-road arrival rate of one car every 75 simulated seconds on average.
Initial side-road arrivals use the same interval range. This lighter demand
reduces consecutive service cycles without modifying the original program.
The two side
approaches drive T1 and T3 when a vehicle reaches the detection zone. ED4 bits
0–2 and 5–7 directly drive red/yellow/green for the main and side roads.
Yellow stops approaching vehicles; vehicles already past the stop point clear
the junction. Vehicles are illustrative straight-through traffic with simple
queue spacing, not a road engineering model. Restart resets the random seed.

The book program is the default. Restore book program reloads it; Load Intel
HEX accepts the assembler's absolute data/EOF format and resets execution.
Missing memory cells are filled with NOP, overlapping records and addresses
outside 0–1023 are rejected, and address zero must be present. Selected files
are read locally and are not uploaded. To rebuild the default from source:

```sh
cmake -S assembler -B assembler/build
cmake --build assembler/build
./assembler/build/cmc8asm examples/traffic.asm -o demos/traffic/traffic.hex
```

## Main-road green under repeated demand

The original program has no minimum main-road green interval. After restoring
ED4=044 octal, it immediately polls T1/T3 again. With T1 held high, it writes
046 (main green plus yellow) just 640 microseconds later. New side-road cars
can therefore trigger consecutive service cycles. This behavior is present in
the book's machine code; the assembler does not remove a delay.

The illustrative animation currently stops approaching cars whenever yellow
is lit, even when green is also lit. Combined with repeated demand, this can
leave the main-road queue almost stationary. The source's ten-second main
green-plus-yellow phase still executes. A minimum-green policy would require
an explicitly modified program, or a different documented interpretation of
how vehicles respond to the combined lamps.

## Execution model and scope

cpu.mjs is a separate instruction-level demo core, leaving the numbered
signaling models unchanged. It implements NOP, LRI, LRM, SRD (ED4 only), INR,
DCR, JSR, RSR, BT0/BT1, BZ0/BZ1 and JMP. These cover the traffic program, not
the full instruction set. Unsupported instructions or output ports stop the
demo with an error. Interrupts, waits, external memory writes and the Midahs
monitor are outside this first version.

Instruction costs use the established 64-microsecond machine cycle. The
initial RESET cycle is counted; registers start at explicitly supplied zero
values. JSR selects the next register as PC and RSR restores the previous
selection. Branches preserve the page-local operand wrap. The lamp write time
is recorded at execute T5, matching the research fixture, while the animation
observes changes at instruction boundaries (within 192 microseconds).
The CPU executes every delay-loop instruction; there are no scripted light
sequences or skipped delays.

The animation advances in small shared simulated-time steps, with up to one
instruction of timing overshoot per step. Speed is a simulation multiplier,
not a guaranteed wall-clock rate. Long frame gaps are capped to avoid a burst
of catch-up work after a background tab. Vehicles and CPU pause together.
A Web Worker is unnecessary for this small instruction core unless profiling
on target browsers shows otherwise. CPU write history is bounded by the UI.

## Validation

```sh
node --test demos/traffic/cpu.test.mjs
python3 -m unittest tests.test_traffic_demo
```

Checks compare every bundled source byte against the independent book
transcription and the lamp sequence and service intervals against the
recorded v018 signaling run. Both sensor inputs, idle polling, a demand pulse,
register-based call/return, page wrapping, invalid instructions and malformed
HEX are covered. The browser animation itself still needs visual verification
in a browser; none is installed in the development environment.
