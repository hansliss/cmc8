"""Independent structural checks of the figure-5.1 transcription and reference."""
from collections import Counter
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

import tools.build_instruction_reference as reference

from tools.build_instruction_reference import build, load_data, ROOT, validate
from cmc8.versions.v016.sequences import decode, SEQUENCES


class CatalogueTests(unittest.TestCase):
    def test_all_encodings_and_cycle_totals(self):
        catalogue, _ = load_data()
        encodings = validate(catalogue)
        self.assertEqual(len(encodings), 239)
        self.assertEqual(Counter(e['base_cycles'] for e in catalogue['instructions']), {1:7, 2:14, 3:22})
        self.assertEqual(encodings[0xF3], 'JMP')
        self.assertEqual(encodings[0xFF], 'JCR')
        self.assertEqual(encodings[0x0C], 'JSR')
        self.assertEqual(encodings[0x0F], 'RSR')

    def test_simulator_decoder_agrees_with_independent_catalogue(self):
        catalogue, _ = load_data()
        encodings = validate(catalogue)
        supported = 0
        for opcode in range(256):
            if encodings.get(opcode) in SEQUENCES:
                self.assertEqual(decode(opcode), encodings[opcode])
                supported += 1
            else:
                with self.assertRaises(ValueError):
                    decode(opcode)
        self.assertEqual(supported, 239)

    def test_generated_reference_is_current(self):
        for relative, expected in build(*load_data()).items():
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_text(), expected)

    def test_reference_build_without_local_book_files(self):
        expected = build(*load_data())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'specification').mkdir()
            for name in ('instructions.json', 'instruction-mentions.json', 'book-microprograms.json'):
                (root / 'specification' / name).write_text((ROOT / 'specification' / name).read_text())
            with patch.object(reference, 'ROOT', root):
                catalogue, pages = load_data()
                self.assertIsNone(pages)
                self.assertEqual(build(catalogue, pages), expected)
                with self.assertRaisesRegex(ValueError, 'Missing scan'):
                    validate(catalogue, require_scans=True)

    def test_every_entry_has_baseline_and_a_search_record(self):
        catalogue, pages = load_data()
        if pages is not None:
            self.assertEqual(len(pages), 226)
        for entry in catalogue['instructions']:
            self.assertEqual(entry['references'][0]['source'], 'repertory')
            self.assertTrue(entry['ocr_patterns'])
            self.assertTrue((ROOT / f'docs/instructions/{entry["mnemonic"]}.md').exists())


if __name__ == '__main__':
    unittest.main()
