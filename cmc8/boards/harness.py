"""Small board-level fixture with explicit I/O ports and bounded CPU tracing.

Peripheral changes happen after a successful CPU slot. Input reads are pure;
failed CPU writes never leave a peripheral event behind. The clock advances
in integer subdivisions, independent of the host computer's execution speed.
"""
from dataclasses import dataclass

from cmc8.versions.v018 import InstructionLimit, Memory, ModelError


@dataclass
class BytePort:
    name: str
    value: int | None = None
    readable: bool = True
    writable: bool = True

    def drive(self, value):
        if value is not None and (type(value) is not int or not 0 <= value <= 255):
            raise ModelError('Port value must be a byte or None')
        self.value = value

    def __post_init__(self):
        self.drive(self.value)


class PortMemory(Memory):
    """Memory plus named byte ports; side effects are committed by the board."""

    def __init__(self, *, ports=None, **memory):
        super().__init__(**memory)
        self.ports = {} if ports is None else dict(ports)
        if any(type(a) is not int or not 0 <= a <= 255 for a in self.ports):
            raise ModelError('Port addresses must be bytes')

    def read(self, space, address, elapsed):
        if space == 'devices' and address in self.ports:
            port = self.ports[address]
            return port.value if port.readable and elapsed >= self.device_delay else None
        return super().read(space, address, elapsed)

    def write(self, space, address, value):
        if space == 'devices' and address in self.ports and not self.ports[address].writable:
            raise ModelError(f'Port {address:02X} is read-only')
        super().write(space, address, value)


@dataclass(frozen=True)
class PortWrite:
    subdivision: int
    time_ns: int
    address: int
    value: int
    name: str


class BoardHarness:
    def __init__(self, cpu, *, subdivision_ns=8000, trace_limit=64):
        if type(subdivision_ns) is not int or subdivision_ns <= 0:
            raise ValueError('subdivision_ns must be a positive integer')
        if type(trace_limit) is not int or trace_limit < 0:
            raise ValueError('trace_limit must be a nonnegative integer')
        if not isinstance(cpu.memory, PortMemory) or cpu.trace:
            raise ValueError('Start a fresh CPU with PortMemory')
        self.cpu = cpu
        self.subdivision_ns = subdivision_ns
        self.trace_limit = trace_limit
        self.subdivisions = 0
        self.completed_events = 0
        self.writes: list[PortWrite] = []

    @property
    def time_ns(self):
        return self.subdivisions*self.subdivision_ns

    @property
    def boundary(self):
        return (self.cpu.state.phase, self.cpu.state.timing) == (0, 0)

    def step(self):
        row = self.cpu.step()
        write = row.memory_write
        if write is not None and write.space == 'devices':
            port = self.cpu.memory.ports.get(write.address)
            if port is not None:
                port.drive(write.value)
            self.writes.append(PortWrite(self.subdivisions, self.time_ns, write.address,
                                         write.value, port.name if port else 'unnamed'))
        self.subdivisions += 1
        if self.boundary:
            self.completed_events += 1
        # Slot counters in the CPU remain absolute. Trimming observation
        # lists does not skip work, replace microcode or change virtual time.
        keep = self.trace_limit
        if keep:
            del self.cpu.trace[:-keep]
            del self.cpu.cpu.trace[:-2*keep]
        else:
            self.cpu.trace.clear()
            self.cpu.cpu.trace.clear()
        return row

    def run_until(self, predicate, *, max_slots):
        if type(max_slots) is not int or max_slots < 0:
            raise ValueError('max_slots must be a nonnegative integer')
        for _ in range(max_slots):
            if predicate(self):
                return
            self.step()
        if not predicate(self):
            raise InstructionLimit(f'Board did not meet its stop condition in {max_slots} subdivisions')

    def run_event(self, *, max_slots=1024):
        """Run one CPU boundary event through the peripheral observer."""
        before = self.completed_events
        self.run_until(lambda b: b.completed_events > before, max_slots=max_slots)
