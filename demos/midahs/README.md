# Interactive Midahs

A browser faceplate backed by a CMC8 instruction emulator and a **reconstructed
monitor written in CMC8 assembly**. This is not a recovered KEX ROM image.
There are no browser dependencies or build steps to run the supplied images.

From the repository directory:

```sh
python3 -m http.server 8000
```

Open <http://localhost:8000/demos/midahs/>. HTTP is needed for modules and HEX
loading. To distribute it separately, retain `demos/midahs/` and its sibling
`demos/shared/`. No server-side CPU or uploaded user programs are involved.

## First experiment

1. The monitor starts at program page 0, address 000. The data display reads
   `023`, the first opcode of the default switches-to-lamps program.
2. Press **GO**, then toggle the switches. ED4's eight lamps follow ED3.
3. Press **KEX** to return to the monitor. The user image and lamps survive.
4. Press **+** to examine successive bytes: the first six are
   `023 003 033 004 360 000`.

To enter that program yourself, select `0 0 0 0` in AD mode, press DA and
enter `0 2 3`. Press + then enter `0 0 3`, and continue with the remaining
bytes. Writes occur on each digit's release. Press AD, enter `0 0 0 0`,
then GO. This exercises actual monitor code, memory writes and CPU execution.

## Panel behavior

- The keypad has octal digits, GO, AD, DA and +. KEX is a separate board button.
- AD entry uses four digits: page 0–3, then an eight-bit octal offset. Another
  group of four replaces the address. Page input is masked to two bits;
  byte entry wraps modulo 256, like the underlying register operations.
- DA entry groups three octal digits, replacing the selected byte. + advances
  the offset, refreshes the data display and resets digit entry. It does not
  carry into the next page. DA remains selected after +.
- AD selects address mode. A second consecutive AD cycles P → S → E → P.
  The enabled position in the left display identifies the selected space.
  The selected page is replicated into its three octal display fields so it
  remains visible when switching spaces. E addresses are eight-bit ports.
- GO always selects program memory. It constructs a jump at page 2,
  offsets 316/317 octal, then clears KEX and jumps through that stub.
  Those two RAM locations are reserved and overwritten by GO.
- KEX interrupts user execution and starts the monitor again. This monitor
  initializes its examination address to page 0, offset 000. It does not
  clear user RAM, storage memory, switches or lamps.
- Pause and Step instruction operate at instruction boundaries. These are
  emulator controls, not a recreation of the physical single-step circuit.
  CPU register/flag displays are inspection aids rather than extra Midahs I/O.

Digits 0–7, Enter, A, D, + and Escape provide the equivalent keyboard controls.
Key repeat is ignored; a key is held until release, and monitor commands take
effect on release. A window losing focus releases the held key. Pausing while
entering a key requires resuming or stepping the CPU for it to process that key.

Load user Intel HEX replaces user program pages 0–2 and starts KEX. It rejects
page-3 data, even zero-filled ROM records, and requires an explicit byte at
reset address zero. Sparse holes are NOP. Restore switches demo starts a fresh
board with the bundled six-byte example. Files stay in the browser.

## Evidence and reconstruction choices

The functional ports, key codes and digit enables follow the existing
[Python panel fixture](../../docs/midahs-panel.md), based on printed pp.126–133.
The monitor's user-visible commands are described on pp.136–138. Figure 8.10
supplies the keyboard polling routine, including waiting for release; the
accepted XRI and page corrections are retained, along with its padding NOP.
Figure 8.9 reserves the page-2 jump stub, and KEX enters at 3,363 octal.

`monitor.asm` implements missing routines rather than guessing original ROM
bytes. Four-digit address grouping, rolling byte assembly, repeated-AD state,
initial address clearing and error recovery are explicit reconstruction choices.
The original monitor may organize these details differently.

The book states on p.150 that ED6 selects memory access during KEX, but omits
the complete circuitry. This board uses the following **functional hypothesis**:
KEX remaps data reads/writes from either memory space according to ED6 and ED0;
instruction and operand fetches remain physical program memory. ED0's selected
octal field supplies the page, restricted to its low two bits. E selects ports.
Normal user accesses use PG and the instruction's usual memory-space selector.
This supports the documented examination functions while keeping page 3 executable.

KEX button entry directly installs the result of RESET plus the documented
injected JMP3,363 sequence; it does not simulate individual injected bus cycles.
SCS words in octal 200–277 set/clear KEX from bit 0, following the book's 2X0/2X1
control convention. SCW is rejected because its external handshake is absent.
No interrupt entry, external waits, analog debounce, display multiplexing,
PROM-card overlays or physical HALT/single-step circuits are modeled here.

Power-on RAM, latches, switches and CPU registers receive explicit demo zero
values; the keyboard idles at FF. This is not an assertion about uninitialized
hardware. Unpopulated input ports supply FF; writes to absent/input-only ports
stop with an error. Page 3 rejects program writes. KEX recovers from errors.
The board permits display/output-latch readback as a functional convenience.

## Sources and validation

- `monitor.asm` / `monitor.hex`: readable reconstructed monitor and assembled ROM.
- `switches.asm` / `switches.hex`: book switch/lamp example, default user program.
- `board.mjs`: KEX, memory mapping, ports, keyboard and ROM protection.
- `app.mjs` / `index.html`: faceplate and browser controls.
- `../shared/cpu.mjs`: instruction-level core shared with traffic.

Rebuild the HEX files from the repository root:

```sh
cmake -S assembler -B assembler/build
cmake --build assembler/build
./assembler/build/cmc8asm demos/midahs/monitor.asm -o demos/midahs/monitor.hex
./assembler/build/cmc8asm demos/midahs/switches.asm -o demos/midahs/switches.hex
```

Run `node demos/midahs/board.test.mjs` and
`node demos/midahs/ui.test.mjs`, or
`python3 -m unittest tests.test_midahs_demo tests.test_browser_cpu tests.test_traffic_demo`.
Tests exercise monitor startup, press/release, all memory spaces, address and
data entry, GO across pages, KEX return, ROM protection, image consistency,
and the default program. A separate differential check compares functional
results and cycle costs of the ordinary instruction encodings against v018,
including PC/register aliases and page wrapping. The traffic timing regression
remains unchanged. An additional DOM-adapter test exercises the actual UI event handlers and
display updates. The UI still needs visual checking in a real browser;
this development environment has no browser installed.
