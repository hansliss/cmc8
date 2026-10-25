"""Run the standalone JavaScript demo core's independent timing checks."""
from pathlib import Path
import shutil
import subprocess
import unittest


class TrafficDemoTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is needed for browser-core checks')
    def test_browser_cpu(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(['node', '--test', 'demos/traffic/cpu.test.mjs'],
                                cwd=root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
