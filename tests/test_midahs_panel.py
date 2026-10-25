"""Book port-test snippets and the functional front-panel boundary."""
import unittest

from cmc8.boards.midahs import KEY_CODES, make_panel
from cmc8.versions.v018 import ModelError


class MidahsPanelTests(unittest.TestCase):
    def test_p126_switches_to_lamps_program(self):
        board = make_panel([0o023,3,0o033,4,0o360,0],switches=0o245)
        board.run_until(lambda b:len(b.writes)==1,max_slots=128)
        self.assertEqual(board.ports[4].value,0o245)
        self.assertEqual(board.snapshot()['lamps'],(True,False,True,False,False,True,False,True))
        board.set_switches(0o132)
        board.run_until(lambda b:len(b.writes)==2,max_slots=128)
        self.assertEqual(board.ports[4].value,0o132)

    def test_p129_keyboard_to_data_display_program_for_every_printed_key(self):
        for key,nibble in KEY_CODES.items():
            with self.subTest(key=key):
                board=make_panel([0o023,5,0o033,2,0o360,0],switches=0)
                board.press_key(key)
                board.run_until(lambda b:len(b.writes)==1,max_slots=128)
                self.assertEqual(board.snapshot()['data'],f'{0xF0|nibble:03o}')
                board.release_key()
                board.run_until(lambda b:len(b.writes)==2,max_slots=128)
                self.assertEqual(board.snapshot()['data'],'377')

    def test_p129_bidirectional_display_register_copy(self):
        board=make_panel([0o023,2,0o033,1,0o360,0],switches=0)
        board.ports[2].drive(0o347)
        board.run_until(lambda b:len(b.writes)==1,max_slots=128)
        self.assertEqual(board.snapshot()['address'],'347')
        self.assertEqual(board.snapshot()['data'],'347')

    def test_fig713_enable_bits_gate_only_the_corresponding_page_digits(self):
        for mask,text in [(0,'   '),(1,'3  '),(2,' 7 '),(4,'  7'),(7,'377')]:
            board=make_panel([0o023,3,0o033,6,0o360,0],switches=mask)
            board.ports[0].drive(0o377)
            board.ports[1].drive(0o123)
            board.ports[2].drive(0o245)
            board.run_until(lambda b:len(b.writes)==1,max_slots=128)
            self.assertEqual(board.snapshot()['page'],text)
            self.assertEqual(board.snapshot()['address'],'123')
            self.assertEqual(board.snapshot()['data'],'245')

    def test_ports_and_display_do_not_acquire_unlisted_reset_values(self):
        board=make_panel([0],switches=None)
        board.run_event()  # CPU RESET only.
        self.assertEqual(board.snapshot()['data'],'???')
        self.assertEqual(board.snapshot()['page'],'???')
        self.assertIsNone(board.snapshot()['lamps'])
        self.assertIsNone(board.ports[3].value)
        self.assertEqual(board.snapshot()['keyboard'],'377')  # Explicit idle fixture.

    def test_keyboard_validation_preserves_the_held_key(self):
        board=make_panel([0],switches=0)
        with self.assertRaises(ModelError):board.press_key('KEX')
        board.press_key('GO')
        with self.assertRaises(ModelError):board.press_key('7')
        self.assertEqual(board.held_key,'GO')
        self.assertEqual(board.ports[5].value,0o361)
        board.release_key()
        board.press_key('7')
        self.assertEqual(board.ports[5].value,0o376)

    def test_fig810_polling_subroutine_accepts_a_key_only_after_release(self):
        # Accepted E004/E005 corrections; page3 placement follows the KEX
        # context. Boot jumps there normally, rather than changing PG/N
        # in the middle of execution to make the test work.
        program = {
            0:0xF3,1:0x40, 0x340:0x0C,0x341:0,0x342:0,
            0x300:0x16,0x301:5,0x302:0x3E,0x303:0x2F,0x304:255,
            0x305:0xEB,0x306:0,0x307:0,
            0x308:0x17,0x309:5,0x30A:0x2F,0x30B:255,
            0x30C:0xE3,0x30D:8,0x30E:0x0F,
        }
        board=make_panel(program,switches=0)
        for _ in range(7):board.run_event()  # RESET, JMP, JSR, four idle-loop instructions.
        self.assertEqual((board.cpu.state.n,board.cpu.state.registers[1]),(1,0))
        board.press_key('GO')
        for _ in range(4):board.run_event()
        self.assertEqual(board.cpu.state.registers[6],0o361)
        board.run_until(lambda b:b.boundary and b.cpu.state.registers[1]==8,max_slots=256)
        for _ in range(3):board.run_event()
        self.assertEqual((board.cpu.state.n,board.cpu.state.registers[1]),(1,8))
        board.release_key()
        board.run_until(lambda b:b.boundary and b.cpu.state.n==0,max_slots=256)
        self.assertEqual(board.cpu.state.registers[0],0x42)
        self.assertEqual(board.cpu.state.registers[6],0o361)
        self.assertEqual(board.cpu.state.pg,3)


if __name__ == '__main__':
    unittest.main()
