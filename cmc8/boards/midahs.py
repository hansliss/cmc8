"""Midahs-style logical keyboard/display/port fixture from printed pp.126–133.

python3 -m cmc8.boards.midahs GO 0 7 +
The demonstration runs the p.129 ED5→ED2 program, not a recreated KEX monitor.
"""
import argparse

from cmc8.versions.v018 import InstructionSimulator, InterruptInput, ModelError, ResetInput, RunInputs, State
from .harness import BoardHarness, BytePort, PortMemory

# Figure7.15's observed low nibbles; high nibble is F in this board fixture.
KEY_CODES = {str(i):2*i for i in range(8)} | {'GO':1,'AD':3,'DA':5,'+':7}


def octal(value, width=3):
    return '?'*width if value is None else f'{value:0{width}o}'


class MidahsPanel(BoardHarness):
    def __init__(self, cpu, **options):
        super().__init__(cpu, **options)
        self.held_key = None
        self.last_row = None

    @property
    def ports(self):
        return self.cpu.memory.ports

    def step(self):
        row = super().step()
        self.last_row = row
        return row

    def press_key(self, key):
        key = str(key).upper()
        if key not in KEY_CODES:
            raise ModelError(f'Unknown keypad key: {key}')
        if self.held_key is not None:
            raise ModelError('Release the held key before pressing another')
        self.ports[5].drive(0xF0 | KEY_CODES[key])
        self.held_key = key

    def release_key(self):
        # The KEX polling examples require FF when no key is presented.
        # This fixture supplies that bus-level value explicitly; it does
        # not simulate analog pullups, matrix scanning or the 74C922 internals.
        self.ports[5].drive(0xFF)
        self.held_key = None

    def set_switches(self, value):
        self.ports[3].drive(value)

    def snapshot(self):
        state = self.cpu.state
        page = octal(self.ports[0].value)
        enables = self.ports[6].value
        if enables is None:
            page = '???'
        else:
            # Fig7.13: bit0 enables leftmost page digit, bit2 rightmost.
            page = ''.join(digit if enables & (1<<i) else ' '
                           for i,digit in enumerate(page))
        bus_address = (None if state.pg is None or state.ab is None else
                       (state.pg<<8)|state.ab)
        db = None if self.last_row is None else self.last_row.end.signals.db
        lamps = self.ports[4].value
        return {'page':page, 'address':octal(self.ports[1].value),
                'data':octal(self.ports[2].value), 'bus_address':octal(bus_address,4),
                'bus_data':octal(db), 'timing':octal(self.last_row.timing if self.last_row is not None else state.timing,1),
                'lamps':None if lamps is None else tuple(bool(lamps & (1<<i)) for i in range(8)),
                'keyboard':octal(self.ports[5].value), 'held_key':self.held_key}


def make_panel(program, *, switches=None, trace_limit=64):
    ports = {0:BytePort('page display ED0'), 1:BytePort('address display ED1'),
             2:BytePort('data display ED2'),
             3:BytePort('switches ED3',switches,writable=False),
             4:BytePort('lamps ED4',readable=False),
             5:BytePort('keyboard ED5',0xFF,writable=False),
             6:BytePort('digit enables ED6',readable=False)}
    cells = dict(enumerate(program)) if not isinstance(program,dict) else dict(program)
    memory = PortMemory(program=cells,ports=ports,program_readonly_pages={3})
    cpu = InstructionSimulator(State(inte=0,intr=0),memory,
                               reset=ResetInput(1),reset_sampled=True,
                               interrupts=InterruptInput(1),run_inputs=RunInputs(memr=0,halt=1,ss=1),
                               test_inputs=(0,0,0,0))
    return MidahsPanel(cpu,trace_limit=trace_limit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys',nargs='*',default=['GO','0','7','+'])
    args = parser.parse_args()
    # Literal p.129 keyboard test: LRD R3,ED5; SRD R3,ED2; JMP0,000.
    board = make_panel([0o023,0o005,0o033,0o002,0o360,0o000],switches=0)
    for key in args.keys:
        board.press_key(key)
        before = len(board.writes)
        board.run_until(lambda b:len(b.writes)>before,max_slots=256)
        print(f'Key {key:>2}: ED2={board.snapshot()["data"]}')
        board.release_key()
        before = len(board.writes)
        board.run_until(lambda b:len(b.writes)>before,max_slots=256)
        print(f'Release: ED2={board.snapshot()["data"]}')


if __name__ == '__main__':
    main()
