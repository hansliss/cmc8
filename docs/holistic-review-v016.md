# Holistic review of v016

Review baseline: [v016](model-v016.md), 2026-10-25. No architecture revision
or changes to numbered simulator packages result from this review.

The complete instruction model remains internally consistent under the
checks below. No new contradiction or instruction-result defect was found.
This supports using v016 as the research baseline; it does not establish
that its inferred internal timing matches the original chip.

## Scope and method

Reviewed the current datapath evaluator, endpoint captures, decoder, MOP
tables, sequencer, memory/device harness, control strobe and acknowledgement
handling, interrupt integration, earlier investigation notes and tests.
This was a whole-implementation consistency review, not a new visual
transcription of every book figure.

The existing 273 tests pass. Many are detailed source-landmark, arithmetic,
application and error-handling checks, but many execute historical versions.
Version-to-version trace comparisons help detect regressions; they cannot
independently discover a mistake inherited by both versions.

Added [three current-model checks](../tests/test_holistic.py) using a direct
instruction-level reference which imports neither MOP schedules nor the
datapath evaluator. Its expected results use the independent catalogue's
encodings, lengths and cycle counts, plus the selected instruction semantics.
All three pass:

| Check | Cases | What it challenges |
| --- | ---: | --- |
| Every encoding, every PC selector, PC at 00/FE/FF | 5,736 | Results, register aliases, page/PC state, wrapping operands, flags, cycle totals, memory writes and control strobes |
| Each of six deferred flag opcodes before every encoding | 1,434 pairs | Effect during the next fetch, computational overwrite, branch consumption, successive flag instructions and the third fetch |
| Request arriving during each encoding's fetch | 239 | Complete the instruction before entry, preserve its result and page, then install 002 in the next PC register |

Values in this review are hexadecimal unless otherwise stated. The first
check uses deterministic varied data, flags, pins and pages, not exhaustive
combinations of all machine states. The pair check uses ordinary PC register
R0 with an FF→00 operand wrap. The interrupt check injects a pulse after
F0T2 with interrupts initially enabled; it does not enumerate every possible
arrival subdivision. Existing interrupt tests additionally cover late arrival,
EXR's partial exchange, SCWR waits and retained-IR corner cases.

The reference can share a mistaken semantic interpretation with the
simulator. It challenges the implementation of that interpretation, not its
historical truth. Exact inferred internal slots remain source/research claims.

## Structural similarities that hold up

- **One fetch mechanism:** ordinary instructions fetch through the same
  early F0 controls. PC advances within its byte, independently of PG.
  Operand fetches continue on the source page before a transfer changes PG.
- **One memory-transfer family:** LRS/SRS, LRM/SRM and LRD/SRD substitute
  the external enable while retaining the data paths. Indexed forms replace
  operand fetching with X buffering. I/O uses AB without PG.
- **Buffered register transfers:** JCR and CPY share a register→DB→BR
  preparation; their destination selectors differ. Indexed addressing and
  register logic share the X preparation. No extra register port is hidden.
- **One branch condition circuit:** polarity comes from the opcode and H's
  XOR/inverted-output relationship. The sampled decision controls writeback.
  BZ/BL change PG only when taken; BT's low bits select a pin instead.
- **One register-based return mechanism:** JSR and interrupt entry increment
  N; RSR decrements it. Neither mechanism creates a memory stack or saves PG.
- **Consistent flag consumers:** arithmetic/logical operations update Z from
  their final result; shifts preserve Z. RRL consumes old L and records the
  shifted-out bit. Deferred flag opcodes compose with those operations.
- **Separate external protocols:** ordinary device reads/writes use EDE and
  WRITE. SCS/SCW send a control byte directly from program memory with STRCS;
  only SCW waits for SCWR. The example external latch is a harness choice.

## Oddities and remaining uncertainty

| Area | Selected behavior | Assessment |
| --- | --- | --- |
| EXR | Explicit extra ALU input-A holding latch and named capture/held controls | The substantial additional storage hypothesis, accepted as H019; not demonstrated by figure 4.1 |
| DCR zero detection | Test final DI at writeback using a named zero-source override | The book explicitly omits this circuitry; final-result semantics are supported, but detector path and timing remain H014 |
| Deferred flag instructions | Old IR controls the next fetch at T2 | EIN has direct timing support; the other five follow the consistency principle. Ordinary combinations pass; interrupt precedence remains less certain |
| Interrupted flag instruction | Entry suppresses opcode effects; retained IR can assert one during the handler fetch | A visible prediction of the selected decoder model, including possible EIN reenable; no new suppression state is justified by this review |
| PG during interrupt entry | Preserve current page; vector to 002 there | Strong interpretation: the adjacent reset table explicitly changes PG while interrupt entry does not. Handler page changes require a return convention |
| Register aliases | Active PC and X remain ordinary register-bank locations | Fetch/operand increments can change a source before execute. Calls/interrupts overwrite the next PC register and N wraps modulo eight. These consequences are consistent, not protected by extra hardware |
| Branch TEST inputs | Selected level reaches H at T2 | Functional behavior is modeled; exact physical sampling and original pin bias remain unknown |
| Phase skipping and waits | F1T1 can select F2 without restarting T; SCWR uses complete eight-slot F3 loops | Phase skip has direct source support; detailed SCWR controller realization remains H021 |
| Capture endpoints | Most destinations capture at subdivision start; IR has start/end transparency samples | A deliberate discrete-time abstraction. These endpoints are not a recovered physical clocking scheme |

The latch is therefore the standout *storage* addition, but it is not the
only implementation choice beyond the printed diagrams. DCR's detector,
held control levels, decoder overlays and endpoint ordering also need to
remain visible when translating this model into hardware.

The executable control description consists of the numbered MOP tables
**plus** deferred flag decoding, conditional branch writes/page selection,
`ZERO_SOURCES`, `ALU_A_MODES`, `CONTROL_STROBES`, interrupt selection and
the wait/phase controller. Exporting only `SEQUENCES` would lose behavior.
These exceptions are explicit and localized, but a future hardware decoder
must account for all of them.

## Coverage limits and follow-up priorities

All 43 instruction families / 239 defined encodings execute, including
ordinary I/O and control-word signalling. This is a complete instruction
research model with interrupt handling, rather than a complete pin-compatible
processor model. The following work remains:

1. **Reset:** implement the documented reset sequence and establish which
   storage is initialized, what remains unknown, and how reset interacts
   with a partial instruction, pending interrupt or wait. Experiments
   currently supply initial state explicitly.
2. **Generic MEMR waits, HALT and single-step:** integrate their controller
   behavior with fetch, execute, interrupts and SCWR. Current ordinary
   accesses require `ready=True`; a configured read delay can make data
   unavailable but does not insert wait states. MOP29 placement differs
   among the present schedules, so a generic stall must not be inferred
   simply by freezing every instruction whenever a memory enable is high.
3. **Hardware-facing timing:** distinguish logical assertions from physical
   pin polarities, edge widths, bus turnaround, setup/hold and input
   synchronization. The model does not recover propagation or metastability.
4. **Source discrimination:** retain alternative EXR implementations, DCR
   detector choices and interrupt/retained-IR decoder interpretations until
   another source or hardware experiment can distinguish them. More passing
   semantic tests alone cannot select the historical circuit.

The next implementation milestone should be reset and external execution
control, rather than revising a working instruction family without new
evidence. A later complete application can provide broader software-level
integration coverage; it will still be a consistency test of the selected
architecture. Preserve v016 and introduce a numbered successor when the
simulated architecture or controller changes.
