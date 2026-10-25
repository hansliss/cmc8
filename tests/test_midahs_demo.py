"""Interactive monitor integration and reproducible bundled machine-code images."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from tests import test_macro_assembler as assembler_tests

ROOT = Path(__file__).resolve().parents[1]


class MidahsDemoTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is needed for browser checks')
    def test_monitor_keyboard_memory_and_user_execution(self):
        for script in ('board.test.mjs', 'ui.test.mjs'):
            with self.subTest(script=script):
                result = subprocess.run(['node', f'demos/midahs/{script}'], cwd=ROOT,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which('cmake') and shutil.which('cc'), 'CMake/C compiler required')
    def test_bundled_images_match_assembly(self):
        # Reuse the existing strict CMake builder without duplicating its build recipe.
        assembler_tests.MacroAssemblerTests.setUpClass()
        self.addCleanup(assembler_tests.MacroAssemblerTests.tearDownClass)
        with tempfile.TemporaryDirectory() as directory:
            for name in ('monitor', 'switches'):
                output = Path(directory) / f'{name}.hex'
                result = subprocess.run([str(assembler_tests.MacroAssemblerTests.executable),
                                         str(ROOT / f'demos/midahs/{name}.asm'), '-o', str(output)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(assembler_tests.read_ihex(output.read_text()),
                                 assembler_tests.read_ihex((ROOT / f'demos/midahs/{name}.hex').read_text()))
