"""Peripheral observation and complete-program checks through the v018 datapath."""
import unittest

from cmc8.boards.harness import BoardHarness, BytePort, PortMemory
from cmc8.boards.traffic import cycle_report, delay_cycles, lamp_state, make_board, run_cycle, source_program
from cmc8.versions.v018 import InstructionSimulator, ModelError, State
from tools.render_traffic_report import validate


class PortHarnessTests(unittest.TestCase):
    def test_input_read_and_output_write_are_observed_at_the_bus(self):
        inp = BytePort('switches', 0xA6, writable=False)
        out = BytePort('lamps', readable=False)
        state = State(n=0, pg=0, ir=0)
        state.registers[0] = 0
        memory = PortMemory(program={0:0x13,1:1,2:0x1B,3:2}, ports={1:inp,2:out})
        board = BoardHarness(InstructionSimulator(state,memory), trace_limit=4)
        board.run_event()
        self.assertEqual(board.cpu.state.registers[3],0xA6)
        self.assertEqual(board.writes,[])
        board.run_event()
        self.assertEqual(out.value,0xA6)
        self.assertEqual([(w.address,w.value,w.subdivision) for w in board.writes],[(2,0xA6,45)])
        self.assertEqual(board.writes[0].time_ns,45*8000)
        self.assertLessEqual(len(board.cpu.trace),4)
        self.assertLessEqual(len(board.cpu.cpu.trace),8)
        self.assertEqual(board.subdivisions,48)

    def test_rejected_port_write_has_no_peripheral_side_effect(self):
        port = BytePort('read-only switches',0x69,writable=False)
        state=State(n=0,pg=0,ir=0)
        state.registers[0],state.registers[3]=0,0xA6
        board=BoardHarness(InstructionSimulator(state,PortMemory(program={0:0x1B,1:1},ports={1:port})))
        for _ in range(21): board.step()
        with self.assertRaises(ModelError): board.step()
        self.assertEqual(port.value,0x69)
        self.assertEqual(board.writes,[])
        self.assertEqual(board.subdivisions,21)
        self.assertEqual(board.cpu.state.timing,5)

    def test_unknown_input_is_not_assumed_zero(self):
        state=State(n=0,pg=0,ir=0)
        state.registers[0]=0
        board=BoardHarness(InstructionSimulator(state,PortMemory(program={0:0x13,1:1},ports={1:BytePort('unknown')})))
        for _ in range(21):board.step()
        with self.assertRaises(ModelError):board.step()
        board.cpu.memory.ports[1].drive(0x69)
        board.run_event()
        self.assertEqual(board.cpu.state.registers[3],0x69)


class TrafficProgramTests(unittest.TestCase):
    def test_literal_source_and_explicit_shortened_fixture_are_separate(self):
        source=source_program()
        self.assertEqual(len(source['cells']),0o113)
        self.assertEqual(make_board().cpu.memory.program[0o103],0o172)
        fast=make_board(delay_count=1)
        self.assertEqual(fast.cpu.memory.program[0o103],1)
        self.assertEqual(source_program(),source)
        self.assertEqual(make_board().cpu.memory.program_readonly_pages,frozenset({0}))

    def test_complete_light_cycle_for_both_side_road_sensors(self):
        expected=[0o044,0o046,0o041,0o201,0o301,0o041,0o044]
        for sensor in (1,3):
            with self.subTest(sensor=sensor):
                board=run_cycle(delay_count=1,sensor=sensor,trace_limit=8)
                self.assertEqual([w.value for w in board.writes],expected)
                self.assertEqual(board.cpu.state.n,0)
                self.assertEqual(board.cpu.memory.ports[4].value,0o044)
                self.assertLessEqual(len(board.cpu.trace),8)
                # One, two, three, two, one delay calls between lamp writes.
                # LRM+SRD adds six cycles between each pair; JSR adds three per call.
                unit=delay_cycles(1)+3
                for i,repeats in enumerate((1,2,3,2,1),start=1):
                    interval=board.writes[i+1].subdivision-board.writes[i].subdivision
                    self.assertEqual(interval,8*(repeats*unit+6))
                validate(cycle_report(board, delay_count=1, sensor=sensor))
                for event in board.writes:
                    lights=lamp_state(event.value)
                    self.assertFalse('green' in lights['main'] and 'green' in lights['side'])

    def test_delay_routine_is_executed_and_cycle_count_matches_independent_arithmetic(self):
        board=make_board(delay_count=1,trace_limit=0)
        board.run_event()  # RESET.
        # Enter the real subroutine with R1 as PC and a known return point in R0.
        board.cpu.state.n=1
        board.cpu.state.registers[0]=0o004
        board.cpu.state.registers[1]=0o100
        begin=board.subdivisions
        board.run_until(lambda b:b.boundary and b.cpu.state.n==0,max_slots=20_000)
        self.assertEqual(board.subdivisions-begin,8*delay_cycles(1))
        self.assertEqual(board.cpu.state.registers[3:5],[0,0])
        self.assertEqual(board.cpu.state.registers[0],0o004)
        self.assertEqual(board.cpu.trace,[])
        self.assertEqual(delay_cycles(0o172)*64_000,10_033_664_000)


if __name__=='__main__':unittest.main()
