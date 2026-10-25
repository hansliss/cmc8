"""Build the instruction reference and OCR cross-references from authored data.

Run: python3 -m tools.build_instruction_reference [--check]
Edit specification/instructions.json, not the generated Markdown pages.
"""
import argparse
import importlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def load_data():
    catalogue = json.loads((ROOT / 'specification/instructions.json').read_text())
    cache = ROOT / 'specification/ocr-pages.json'
    pages = json.loads(cache.read_text())['pages'] if cache.exists() else None
    return catalogue, pages


def validate(catalogue, *, require_scans=False):
    entries = catalogue['instructions']
    if len(entries) != 43 or len({e['mnemonic'] for e in entries}) != 43:
        raise ValueError('Expected the 43 distinct figure-5.1 families')
    encodings = {}
    for entry in entries:
        pattern = entry['pattern']
        if len(pattern) != 8 or set(pattern) - set('01RPT'):
            raise ValueError(f'Invalid pattern for {entry["mnemonic"]}')
        mask = int(''.join('1' if bit in '01' else '0' for bit in pattern), 2)
        value = int(''.join(bit if bit in '01' else '0' for bit in pattern), 2)
        if (mask, value) != (entry['mask'], entry['value']):
            raise ValueError(f'Pattern/mask mismatch: {entry["mnemonic"]}')
        for opcode in range(256):
            if opcode & mask == value:
                if opcode in encodings:
                    raise ValueError(f'Overlapping opcode {opcode:02X}')
                encodings[opcode] = entry['mnemonic']
        for reference in entry['references']:
            if reference['source'] not in catalogue['sources']:
                raise ValueError(f'Unknown source in {entry["mnemonic"]}')
        for finding in entry['findings']:
            for source in finding.get('sources', []):
                if source not in catalogue['sources']:
                    raise ValueError(f'Unknown finding source in {entry["mnemonic"]}')
    if len(encodings) != 239:
        raise ValueError('Expected 239 distinct encoded instruction variants')
    for source in catalogue['sources'].values():
        if not re.fullmatch(r'bookpages/Page_[0-9]{3}\.jpg', source['image']):
            raise ValueError(f'Invalid scan reference: {source["image"]}')
        if require_scans and not (ROOT / source['image']).exists():
            raise ValueError(f'Missing scan: {source["image"]}')
    return encodings


def collect_mentions(catalogue, pages):
    if pages is None:
        # A source checkout retains focused search leads, not the full-book OCR.
        # Re-indexing those leads requires the optional local PDF/OCR inputs.
        saved = json.loads((ROOT / 'specification/instruction-mentions.json').read_text())['mentions']
        return {entry['mnemonic']: saved[entry['mnemonic']]
                for entry in catalogue['instructions']}
    mentions = {}
    for entry in catalogue['instructions']:
        terms = '|'.join(entry['ocr_patterns'])
        pattern = re.compile(r'(?<![A-Za-z0-9])(?:' + terms + r')(?![A-Za-z0-9])', re.I)
        hits = []
        for page in pages:
            lines = page['text'].splitlines()
            for number, line in enumerate(lines):
                if pattern.search(line):
                    context = ' '.join(' '.join(lines[max(0,number-1):number+2]).split())
                    hits.append(dict(pdf_page=page['pdf_page'],
                                     printed_page_candidate=page['printed_page_candidate'],
                                     image=page['image'], ocr_line=number+1,
                                     snippet=context, review='unreviewed OCR lead'))
        mentions[entry['mnemonic']] = hits
    return mentions


def source_link(source, prefix):
    return f'[{source["printed_page"]}: {source["title"]}]({prefix}{source["image"]})'


def escape(text):
    return text.replace('|', r'\|').replace('\n', ' ')


def cycle_text(entry):
    return str(entry['base_cycles']) + ('+ waits' if entry['variable_wait'] else '')


def build(catalogue, pages):
    encodings = validate(catalogue)
    model_name = catalogue['model']
    sequences = importlib.import_module(f'cmc8.versions.{model_name}.sequences')
    mentions = collect_mentions(catalogue, pages)
    book_sequences = json.loads((ROOT / 'specification/book-microprograms.json').read_text())['records']
    for record in book_sequences:
        if record['source'] not in catalogue['sources']:
            raise ValueError(f'Unknown microprogram source: {record["id"]}')
        for phase, slots in record['rows'].items():
            if len(slots) != 8:
                raise ValueError(f'Expected eight timing slots: {record["id"]} {phase}')
    outputs = {}
    lead_document = dict(authority='Search leads only; not visual evidence or an exhaustive occurrence claim',
                         patterns_source='specification/instructions.json', mentions=mentions)
    outputs['specification/instruction-mentions.json'] = json.dumps(lead_document, ensure_ascii=False, indent=2)+'\n'
    overview = [
        '# CMC8 instruction reference', '',
        'Generated from [the authored catalogue](../specification/instructions.json). '
        'Baseline: [figure 5.1, printed p.67](../bookpages/Page_073.jpg).', '',
        '[Working book errata](errata.md) collects established corrections and '
        'candidate discrepancies without altering the source transcriptions.', '',
        f'All **43 mnemonic families / {len(encodings)} encoded variants** are catalogued. '
        'Zeros are normalized to `0`; spacing is normalized. The printed image remains the authority. '
        'Cycle counts exclude optional memory waits; SCW explicitly adds acknowledgement waits.', '',
        'The transcription reproduces the book’s distribution: seven one-cycle, fourteen two-cycle '
        'and twenty-two three-cycle families. A visually checked source is evidence for its stated '
        'observation, not certification of every line on that page.', '',
        f'MOP tables below reflect **{model_name}**, not a claim of original silicon truth. '
        'Documented summaries, working extrapolations and unresolved questions are separate in each entry. '
        'The inherited flag timing and indexed route retain their provisional status.', '',
        '[Searchable OCR mentions](instruction-mentions.md) cover all 226 PDF pages. '
        'Search results may miss damaged OCR or include other architectures; they are leads, not facts. '
        'Printed-page coordinates use PDF p+7 (1-based) / image Page_(p+6).jpg, checked at multiple anchors.', '',
        '| Instruction | Encoding | Bytes | Cycles | Flags | Implemented | Key sources |',
        '| --- | --- | --- | --- | --- | --- | --- |',
    ]
    leads = ['# Instruction OCR search leads', '',
             'Generated from all 226 PDF pages. These snippets are unreviewed OCR, including comparison '
             'architectures and possible false matches. They are navigation aids, not evidence. '
             'Use the curated references in [the instruction reference](instruction-set.md) for verified observations.', '']
    if getattr(sequences, 'ALU_A_MODES', {}):
        overview[-2:-2] = [
            '**EXR is especially provisional:** its executable candidate adds an undocumented '
            'ALU input holding latch. This is an architecture hypothesis, not merely inferred '
            'slot timing. See [v014](model-v014.md).', '',
        ]
    if hasattr(sequences, 'INTERRUPT_ENTRY'):
        overview[-2:-2] = [
            '[Interrupt integration](model-v016.md) adds a separate eight-slot entry cycle '
            'and asynchronous INTR observations when explicitly enabled. This is not another '
            'opcode family and does not change the 43-family count.', '',
        ]
    if hasattr(sequences, 'RESET_CYCLE'):
        overview[-2:-2] = [
            '[Reset integration](model-v017.md) implements the figure-4.21 reset cycle '
            'selected by active-low RESET at T7. It is separate from the opcode repertoire; '
            'reset does not silently initialize unlisted flags or registers.', '',
        ]
    if model_name == 'v018':
        overview[-2:-2] = [
            '[Shared execution control](model-v018.md) integrates MEMR, HALT and single-step '
            'with eight-subdivision wait continuations. Read-check coverage and the omitted '
            'SSE circuitry retain explicit H022/H023 interpretations.', '',
        ]
    for entry in catalogue['instructions']:
        name = entry['mnemonic']
        implemented = name in sequences.SEQUENCES
        supporting = [r for r in entry['references'] if r['source'] != 'repertory']
        keys = ', '.join(map(str, sorted({catalogue['sources'][r['source']]['printed_page'] for r in supporting})))
        overview.append(f'| [{name}](instructions/{name}.md) | `{entry["pattern"]}` | '
                        f'{entry["length_bytes"]} | {cycle_text(entry)} | {",".join(entry["flags"]) or "—"} | '
                        f'{model_name if implemented else "not yet"} | {keys or "67 only; see OCR leads"} |')
        article = [f'# {name}', '', '[All instructions](../instruction-set.md)', '',
                   f'**Encoding:** `{entry["pattern"]}`; **bytes:** {entry["length_bytes"]}; '
                   f'**cycles:** {cycle_text(entry)}; **flag column:** {",".join(entry["flags"]) or "blank"}.', '',
                   f'**Book summary ({entry["semantics_status"]}):** {entry["summary"]}', '',
                   '## Reviewed sources', '', '| Printed page / figure | What to look for |', '| --- | --- |']
        for reference in entry['references']:
            source = catalogue['sources'][reference['source']]
            article.append(f'| {source_link(source,"../../")} | {escape(reference["comment"])} '
                           f'{escape(source["comment"])} PDF page {source["pdf_page"]}. |')
        relevant_book = [record for record in book_sequences if name in record['instructions']]
        if relevant_book:
            article += ['', '## Book microprograms (source transcription)', '',
                        'These are functional/sparse printed tables, **not executable held-level controls**. '
                        'An empty cell is an empty printed cell, not proof every gate is released.']
            for record in relevant_book:
                article += ['', '### '+record['title'], '',
                            source_link(catalogue['sources'][record['source']], '../../'), '',
                            '| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |',
                            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
                for phase, slots in record['rows'].items():
                    article.append('| '+phase+' | '+' | '.join(escape(slot) or '—' for slot in slots)+' |')
                article += ['', *['- '+note for note in record['notes']]]
                if record['numbered_rows']:
                    article += ['', 'Literal numbered row (conditional overlays may be described in the notes):', '',
                                '| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |',
                                '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
                    for phase, slots in record['numbered_rows'].items():
                        article.append('| '+phase+' | '+' | '.join(','.join(map(str,slot)) or '—' for slot in slots)+' |')
        article += ['', '## Working findings and assumptions', '']
        if entry['findings']:
            for finding in entry['findings']:
                source_pages = ', '.join(str(catalogue['sources'][key]['printed_page']) for key in finding['sources'])
                article.append(f'- **{finding["classification"]}; {finding["status"]}:** '
                               f'{finding["statement"]}'+(f' Sources: pp. {source_pages}.' if source_pages else ''))
        else:
            article.append('No additional working interpretation has been entered beyond the reviewed summaries.')
        article += ['', '## Open questions', '']
        article += ['- '+q for q in entry['questions']] or ['No instruction-specific question recorded; absence of a question is not completeness of evidence.']
        article += ['', '## Executable control table', '']
        if implemented:
            article += [f'Implemented in [{model_name} sequences](../../cmc8/versions/{model_name}/sequences.py). '
                        'Numbers are MOPs, held over the indicated subdivision. Blank cells assert no listed controls. '
                        'Runtime overlays (notably deferred flag updates) are additional to this base table.', '',
                        '| Phase | T0 | T1 | T2 | T3 | T4 | T5 | T6 | T7 |',
                        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
            for phase, slots in enumerate(sequences.SEQUENCES[name]):
                article.append('| F'+str(phase)+' | '+' | '.join(','.join(map(str,slot)) or '—' for slot in slots)+' |')
            article += ['', 'A phase write (MOP31) can change F1 to F2 while T continues. Unreached '
                        'table cells consume no time. The trace is the source for actually executed slot labels.']
            if name in ('EIN','DIN','SEL','REL','SEZ','REZ'):
                article += ['', 'The instruction’s own flag change occurs at **F0T2 of the next fetch**, '
                            'selected by retained IR. Returning from `run_instruction()` does not force '
                            'that deferred effect early. See [flag timing](../flag-instruction-timing.md).']
            if name in getattr(sequences, 'BRANCHES', ()):
                article += ['', 'The table shows static controls. At **F2T6**, the branch circuit '
                            'adds MOP22 only when sampled physical H.Q=0 (Q-bar=1). '
                            + ('For this page branch it also adds MOP15 only when taken. '
                               if name in sequences.PAGE_BRANCHES else 'N and PG remain unchanged. ')
                            + 'The actual overlay appears in trace `mops` and `branch_taken`. '
                            'H samples at F2T2; static MOP22 at F1/F2T4 advances the operand PC '
                            'regardless of outcome. See [v009 interpretation](../model-v009.md).']
            for (instruction, phase, timing), source in getattr(sequences, 'ZERO_SOURCES', {}).items():
                if instruction == name:
                    article += ['', f'**Additional research control at F{phase}T{timing}:** '
                                f'`zero_source="{source}"` selects the value tested by the modeled MOP32. '
                                'This represents the omitted DCR flag circuitry; neither this source '
                                'selection nor the added MOP32 slot is a literal printed control. '
                                'Trace evaluations record `zero_source` and `zero_value`. '
                                'See [v011 interpretation](../model-v011.md).']
            modes = [(phase, timing, mode) for (instruction, phase, timing), mode
                     in getattr(sequences, 'ALU_A_MODES', {}).items() if instruction == name]
            if modes:
                article += ['', '**Architecture hypothesis H019:** this candidate needs an '
                            'undocumented ALU input holding latch. Static MOPs alone do not '
                            'reproduce it. The named research controls are:', '',
                            '| Slot | Additional control |', '| --- | --- |']
                article += [f'| F{phase}T{timing} | `alu_a_mode="{mode}"` |'
                            for phase, timing, mode in modes]
                article += ['', 'Trace state `alu_a` and evaluation fields `alu_a_mode` / '
                            '`alu_a_value` expose this assumption. See '
                            '[v014](../model-v014.md); successful simulation does not establish the latch.']
            strobes = [(phase, timing) for instruction, phase, timing
                       in sorted(getattr(sequences, 'CONTROL_STROBES', ())) if instruction == name]
            if strobes:
                article += ['', '**Named external output:** STRCS is high at '
                            + ', '.join(f'F{phase}T{timing}' for phase, timing in strobes)
                            + '. It has no assigned MOP number in these source tables. '
                            'Program memory supplies the control byte on DB; the CPU does not '
                            'reload it through BR. Figure 6.14’s external latch is an example '
                            'receiver, modeled by the peripheral harness rather than required by the CPU. '
                            + ('MOP50 at T4 samples active-low SCWR; high inserts eight-slot '
                               'wait cycles with PME held, then T4 is sampled again. '
                               if name == 'SCW' else 'SCS does not sample SCWR. ')
                            + 'See [v015 timing and API](../model-v015.md).']
            if name in {'EIN', 'DIN', 'RSR'} and hasattr(sequences, 'INTERRUPT_ENTRY'):
                article += ['', '[v016 interrupt integration](../model-v016.md) tests this '
                            'instruction with request latching and F0T0 acceptance. The separate '
                            'entry cycle has no opcode and is not included in this instruction’s '
                            'own cycle count. Retained-IR/interrupt decoder edge cases remain explicit.']
        else:
            article.append('Not implemented. No invented MOP table is presented as book evidence.')
        hits = mentions[name]
        page_numbers = sorted({h['printed_page_candidate'] for h in hits if h['printed_page_candidate'] is not None})
        article += ['', '## OCR cross-references', '',
                    f'{len(hits)} candidate line matches on proposed printed pages: '+(', '.join(map(str,page_numbers)) or 'none')+'.', '',
                    f'[All snippets and scan links](../instruction-mentions.md#{name.lower()}). '
                    'These are unreviewed leads and may include other-architecture examples.']
        outputs[f'docs/instructions/{name}.md'] = '\n'.join(article)+'\n'
        leads += [f'## {name}', '', f'Patterns: `{", ".join(entry["ocr_patterns"])}`. '
                  'A pattern alias is a search heuristic, not a claimed alternative mnemonic.', '',
                  '| Printed page candidate / PDF | OCR context |', '| --- | --- |']
        for hit in hits:
            label = f'{hit["printed_page_candidate"] or "front/back"} / PDF {hit["pdf_page"]}'
            link = f'[{label}](../{hit["image"]})' if hit['image'] else label
            leads.append(f'| {link} | {escape(hit["snippet"])} |')
        if not hits:
            leads.append('| — | No OCR hit; this does not establish absence from the book. |')
        leads += ['']
    overview += ['', '## Maintaining this reference', '',
                 'Edit `specification/instructions.json` for the catalogue and '
                 '`specification/book-microprograms.json` for source sequence transcriptions, '
                 'then run `python3 -m tools.build_instruction_reference`. '
                 '`--check` verifies generated files are current. To re-extract OCR, run '
                 '`python3 -m tools.index_book` (requires the installed `pdftotext` executable). '
                 'The simulator and reference renderer otherwise use only Python’s standard library.', '',
                 'Machine-readable OCR leads are in `specification/instruction-mentions.json`; '
                 'the page-separated OCR cache is `specification/ocr-pages.json`. Source comments and '
                 'findings are authored; search hits and displayed MOP tables are generated.']
    outputs['docs/instruction-set.md'] = '\n'.join(overview)+'\n'
    outputs['docs/instruction-mentions.md'] = '\n'.join(leads)+'\n'
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--check-scans', action='store_true',
                        help='also require the optional local page scans')
    args = parser.parse_args()
    catalogue, pages = load_data()
    if args.check_scans:
        validate(catalogue, require_scans=True)
    outputs = build(catalogue, pages)
    stale = []
    for relative, text in outputs.items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text() != text:
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    if stale:
        raise SystemExit('Stale generated files: '+', '.join(stale))
    print(f'{"Checked" if args.check else "Built"} {len(outputs)} reference artifacts')


if __name__ == '__main__':
    main()
