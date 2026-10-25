"""Exhaustive binary decoder equivalence and comparison with the sequencer."""
import json
from pathlib import Path
import unittest

from cmc8.versions.v018 import (InstructionSimulator, InterruptInput, Memory,
                                 ResetInput, RunInputs, State)
from cmc8.versions.v018.sequences import ALU_A_MODES, CONTROL_STROBES, ZERO_SOURCES, decode
from tools.build_control_pla import OUTPUTS, evaluate_terms, reference_word

ROOT = Path(__file__).resolve().parents[1]


class ControlPLATests(unittest.TestCase):
    def test_all_binary_inputs_match_the_exported_truth_function(self):
        report = json.loads((ROOT/'specification/control-pla.json').read_text())
        self.assertEqual(report['output_bits'], OUTPUTS)
        for key in range(32768):
            actual = evaluate_terms(key, report['terms'])
            expected = reference_word(key)
            if actual != expected:
                self.fail(f'Control mismatch for key {key:04X}: {actual:X} != {expected:X}')

    def test_defined_rows_match_the_existing_sequencer_with_quiet_inputs(self):
        cpu = InstructionSimulator(
            State(n=0,pg=0,ir=0,halt=0,h=1,sse=1), Memory(),
            interrupts=InterruptInput(1), reset=ResetInput(1),
            run_inputs=RunInputs(memr=0,halt=1,ss=1))
        checked = 0
        for key in range(32768):
            word = reference_word(key)
            if not word:
                continue
            mode, ir = key >> 13, (key >> 5) & 255
            phase, timing = (key >> 3) & 3, key & 7
            cpu.state.ir, cpu.state.phase, cpu.state.timing = ir, phase, timing
            if mode == 1:
                name = 'INTERRUPT'
            elif mode == 2:
                name = 'RESET'
            else:
                try:
                    name = decode(ir)
                except ValueError:
                    name = None  # Common early fetch does not decode old IR.
            cpu.instruction = name
            controls = cpu._controls(phase,timing)
            controls, _, _, _, _ = cpu._execution_controls(phase,timing,controls)
            actual = sum(1 << (mop-1) for mop in set(controls))
            self.assertEqual(word & ((1<<57)-1), actual, f'key={key:04X}')
            expected_named = {
                'STRCS':(name,phase,timing) in CONTROL_STROBES,
                'ZERO_DI':ZERO_SOURCES.get((name,phase,timing)) == 'di',
                'ALU_A_CAPTURE':ALU_A_MODES.get((name,phase,timing)) == 'capture',
                'ALU_A_HELD':ALU_A_MODES.get((name,phase,timing)) == 'held',
                'CLEAR_INTA':mode == 2 and timing == 0,
            }
            for field, expected in expected_named.items():
                self.assertEqual(bool(word & (1 << OUTPUTS.index(field))),expected)
            checked += 1
        self.assertEqual(checked,9822)

    def test_dynamic_branch_and_wait_controls_are_not_misrepresented_as_static(self):
        branch = reference_word((0xE0<<5) | (2<<3) | 6)
        self.assertFalse(branch & (1 << 21))  # MOP22 belongs to the H overlay.
        self.assertFalse(branch & (1 << 14))  # Conditional PG write is also dynamic.
        self.assertEqual(reference_word((0x53<<5) | (3<<3) | 4),0)
        normal_ein_effect = reference_word((3<<5) | 2)
        reset_t2 = reference_word((2<<13) | (3<<5) | 2)
        self.assertTrue(normal_ein_effect & (1 << 37))
        self.assertFalse(reset_t2 & (1 << 37))


if __name__ == '__main__':
    unittest.main()
