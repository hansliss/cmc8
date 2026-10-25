# Research handoff: catalogue and v008

Current platform: [v018](model-v018.md) retains all 43 instruction families,
interrupt and RESET integration, and adds shared MEMR/HALT/single-step waits.
Research assumptions remain explicit. The sections below retain the original
v008 handoff as a record of that pass.

Start with the [instruction reference](instruction-set.md), then
[the v008 model guide](model-v008.md). All earlier numbered models remain
available. The simulator still uses only Python's standard library.

## Completed

- Catalogued all 43 figure-5.1 families and 239 encoded variants, with
  lengths, cycles, flags, semantics, reviewed source links, questions and
  classified findings. Exactly 21 families / 101 opcode bytes are now
  supported by v008; 22 families remain unimplemented.
- Searched OCR across all 226 PDF pages and retained per-instruction
  snippets with scan links. These are explicitly unreviewed leads: OCR
  misses, false matches and other-architecture examples remain possible.
  This is not a claim that every occurrence has been visually checked.
- Preserved eleven normalized source-sequence records separately from
  executable model tables. Conflicts and candidate corrections remain
  visible rather than being merged into a single purported truth.
- Added JMP, JCR, JSR and RSR in complete model v008. JMP/RSR/JCR take two
  cycles, JSR three. MOP31 implements the documented mid-cycle phase skip.
  JCR's detailed schedule is likely extrapolation; the other three have
  dedicated functional or numbered source sequences.
- Tested nested calls, register aliases, page transitions, target fetching,
  wrapping, phase timing, deferred EIN followed by RSR, and regressions
  against v007. Interrupt acceptance itself remains future work.

## Useful findings

The book directly supplies more microprogram material than a purely inferred
approach would need: JMP/JSR/RSR, branch-bit testing, AND, INR/DCR, RRL and
SCW now have source rows in their catalogue entries. Fig.5.1 really does
specify INR as three cycles. The branch description expands the original
figure-4.1 platform with H and additional MOPs, so implementing branches
will require an explicit new architecture version.

Figure 6.7 corroborates the JMP address-buffer timing independently of the
chapter-5 MOP table. RSR has an F1/F2 label discrepancy between figures
4.19 and 5.4; v008 selects the latter's explicit phase-skip account. No
page stack was added to JSR/RSR, and RSR alone does not enable interrupts.

## Suggested next work

First review [JMP](instructions/JMP.md), [JCR](instructions/JCR.md),
[JSR](instructions/JSR.md), [RSR](instructions/RSR.md) and
v008 trace. CPY and LRI appear useful small additions for constructing
programs. Branches are needed to test L/Z behavior meaningfully; implement
the documented branch extensions explicitly before broader flag tests.
Interrupt acceptance then needs its own source-backed sequence and test,
including the delayed EIN effect. WAIT/SCW/SCS are a separate timing task.

To maintain the reference, edit `specification/instructions.json` and
`specification/book-microprograms.json`, then run:

```sh
python3 -m tools.build_instruction_reference
python3 -m tools.build_instruction_reference --check
python3 -m unittest discover -s tests
python3 -m cmc8 --model v008
```

OCR re-extraction additionally uses the installed `pdftotext` command;
normal simulation and reference generation require no additional libraries.
