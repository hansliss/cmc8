"""Small, inspectable LRM/LRS/SRM/SRS sequencer and external memory test harness.

No instruction semantics are assigned directly to registers: all CPU data
movement goes through the numbered MOP tables and datapath simulator.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field

from .model import MODEL_VERSION, ModelError, Simulator, State, Trace, evaluate
from .sequences import LRS, PRINTED_LRS, SEQUENCES, decode


@dataclass
class Memory:
    """Separate program and storage memories for experiments, not MIDAHS wiring.

    Both address spaces use (PG << 8) | AB, following printed pp.41–43.
    Program writes are allowed unless their page is explicitly read-only.
    Missing cells return unknown. Delays count whole subdivisions since enable.
    A delay of 4 reaches end-of-T5 from T2 but misses start-of-T5.
    """

    program: dict[int, int] = field(default_factory=dict)
    storage: dict[int, int] = field(default_factory=dict)
    program_delay: int = 0
    storage_delay: int = 0
    program_readonly_pages: frozenset[int] = field(default_factory=frozenset)

    def __post_init__(self):
        for name, cells, limit in [("program", self.program, 1024),
                                   ("storage", self.storage, 1024)]:
            for address, value in cells.items():
                if type(address) is not int or not 0 <= address < limit:
                    raise ModelError(f"Invalid {name} address: {address}")
                if type(value) is not int or not 0 <= value < 256:
                    raise ModelError(f"Invalid {name} byte: {value}")
        self.program_readonly_pages = frozenset(self.program_readonly_pages)
        for page in self.program_readonly_pages:
            if type(page) is not int or not 0 <= page < 4:
                raise ModelError(f"Invalid read-only program page: {page}")
        for delay in (self.program_delay, self.storage_delay):
            if type(delay) is not int or delay < 0:
                raise ModelError("Memory delays must be nonnegative whole subdivisions")

    def read(self, space, address, elapsed):
        delay = self.program_delay if space == "program" else self.storage_delay
        cells = self.program if space == "program" else self.storage
        return cells.get(address) if elapsed >= delay else None


    def write(self, space, address, value):
        """Commit a completed write; ROM configuration belongs to the harness."""
        if space == "program":
            if address >> 8 in self.program_readonly_pages:
                raise ModelError(f"Program page {address >> 8} is read-only")
            self.program[address] = value
        else:
            self.storage[address] = value


@dataclass(frozen=True)
class MemoryWrite:
    space: str
    address: int
    value: int


@dataclass
class SlotTrace:
    version: str
    interpretation: str
    instruction: str
    phase: int
    timing: int
    mops: tuple[int, ...]
    start: Trace
    end: Trace
    memory_write: MemoryWrite | None

    def to_dict(self):
        return asdict(self)


class InstructionSimulator:
    """Step one subdivision or execute one LRM/LRS/SRM/SRS instruction.

    All memory-ready checks require ready=True. Waiting, interrupts and HALT
    remain outside this version. The state must start at an instruction boundary.
    """

    def __init__(self, state: State, memory: Memory, *, interpretation="text", ready=True):
        if interpretation not in {"text", "printed"}:
            raise ModelError("interpretation must be 'text' or 'printed'")
        if ready is not True:
            raise ModelError("Only the explicitly always-ready experiment is implemented")
        self.cpu = Simulator(state)
        if state.phase not in {None, 0} or state.timing not in {None, 0}:
            raise ModelError("Start the sequencer at F0T0")
        self.cpu.state.phase = 0
        self.cpu.state.timing = 0
        self.memory = memory
        self.interpretation = interpretation
        self.trace: list[SlotTrace] = []
        self.instruction = None
        self._enable_key = None
        self._enabled_since = 0
        self._slots = 0
        self._pending_write = None
        self._write_high = False

    @property
    def state(self):
        return self.cpu.state

    def _controls(self, phase, timing):
        if phase == 0:
            return LRS[0][timing]
        if self.instruction == "LRS" and self.interpretation == "printed":
            return PRINTED_LRS[phase][timing]
        return SEQUENCES[self.instruction][phase][timing]

    def _memory_space(self, mops):
        """PME and SME select separate memories on the same address outputs."""
        if 24 in mops and 25 in mops:
            raise ModelError("PME and SME both select memory")
        if 24 in mops:
            return "program"
        if 25 in mops:
            return "storage"
        return None

    def _address(self):
        if self.state.ab is None or self.state.pg is None:
            raise ModelError("Memory access needs known AB and PG")
        return (self.state.pg << 8) | self.state.ab

    def _bus(self, mops, point):
        """Resolve ideal external memory response for this capture endpoint."""
        space = self._memory_space(mops)
        if 23 in mops or space is None:
            key = None  # External memory releases DB when CPU drives it.
        else:
            key = (space, self._address())
        if point == "start" and key != self._enable_key:
            self._enable_key = key
            self._enabled_since = self._slots
        if key is None:
            return None
        elapsed = self._slots - self._enabled_since + (point == "end")
        return self.memory.read(*key, elapsed)

    def step(self):
        """Advance one T subdivision, recording start/end observations.

        On error, roll back CPU, memory, cursor and trace for this slot.
        This is convenient experiment behavior, not a hardware recovery model.
        """
        state_before = deepcopy(self.state)
        cpu_trace_length = len(self.cpu.trace)
        trace_length = len(self.trace)
        control_before = (self.instruction, self._enable_key, self._enabled_since,
                          self._slots, self._pending_write, self._write_high)
        storage_before = dict(self.memory.storage)
        program_before = dict(self.memory.program)
        try:
            return self._step()
        except (ModelError, ValueError):
            self.cpu.state = state_before
            del self.cpu.trace[cpu_trace_length:]
            del self.trace[trace_length:]
            (self.instruction, self._enable_key, self._enabled_since,
             self._slots, self._pending_write, self._write_high) = control_before
            self.memory.storage.clear()
            self.memory.storage.update(storage_before)
            self.memory.program.clear()
            self.memory.program.update(program_before)
            raise

    def _step(self):
        phase, timing = self.state.phase, self.state.timing
        mops = self._controls(phase, timing)
        label = f"F{phase}T{timing}"
        bus_start = self._bus(mops, "start")
        # A DB->BR transfer must have valid data at the leading boundary.
        if 2 in mops and bus_start is None:
            raise ModelError(f"{label}: DB is not valid at start of T5 for BR capture")
        start = self.cpu.capture(mops, external_db=bus_start, memory_ready=True,
                                 point="start", label=f"{label} start")
        bus_end = self._bus(mops, "end")
        if 1 in mops and bus_end is None:
            raise ModelError(f"{label}: DB is not valid at end of T5 for IR capture")
        end = self.cpu.capture(mops, external_db=bus_end, memory_ready=True,
                               point="end", label=f"{label} end")

        write = None
        write_high = 27 in mops
        if write_high or self._write_high:
            signals = evaluate(self.state, mops, memory_ready=True)
            space = self._memory_space(mops)
            if space is None or 23 not in mops or signals.db is None:
                raise ModelError(f"{label}: WRITE needs selected memory and CPU-driven data")
            sample = MemoryWrite(space, self._address(), signals.db)
            if self._pending_write is not None and sample != self._pending_write:
                raise ModelError(f"{label}: memory selection/address/data changed during WRITE")
            if write_high:
                self._pending_write = sample
            else:
                # p.54: writing completes when WRITE falls. Require the same
                # memory selection/address/data through this boundary.
                self.memory.write(sample.space, sample.address, sample.value)
                write = sample
                self._pending_write = None
        self._write_high = write_high

        if phase == 0 and timing == 6:
            try:
                self.instruction = decode(self.state.ir)
            except ValueError as error:
                raise ModelError(str(error)) from error
        record = SlotTrace(MODEL_VERSION, self.interpretation,
                           self.instruction or "FETCH", phase, timing,
                           tuple(mops), start, end, write)
        self.trace.append(record)
        self._slots += 1
        # Explicit sequencer assumption: three phases, eight slots each.
        self.state.phase = 0 if phase == 2 and timing == 7 else phase + (timing == 7)
        self.state.timing = (timing + 1) % 8
        return record

    def run_instruction(self):
        """Run from F0T0 to the next F0T0; return its 24 slot records."""
        if (self.state.phase, self.state.timing) != (0, 0):
            raise ModelError("run_instruction requires an instruction boundary")
        self.instruction = None
        begin = len(self.trace)
        for _ in range(24):
            self.step()
        return self.trace[begin:]
