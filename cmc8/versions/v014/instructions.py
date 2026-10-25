"""Inspectable branch, control, flag and load/store sequencer with an external harness.

No instruction semantics are assigned directly to registers: all CPU data
movement goes through the numbered MOP tables and datapath simulator.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field

from .model import MODEL_VERSION, ModelError, Simulator, State, Trace, evaluate
from .sequences import (ALU_A_MODES, BRANCHES, PAGE_BRANCHES, FLAG_INSTRUCTIONS,
                        FlagInstruction, LRS, PRINTED_LRS, SEQUENCES, ZERO_SOURCES, decode)


@dataclass
class Memory:
    """Program/storage memories and simple bidirectional I/O registers.

    Both address spaces use (PG << 8) | AB, following printed pp.41–43.
    Devices use AB only (p.43), with EDE/DBDIR selecting bus direction.
    This is a static register harness, not a model of arbitrary peripherals.
    Program writes are allowed unless their page is explicitly read-only.
    Missing cells return unknown. Delays count whole subdivisions since enable.
    A delay of 4 reaches end-of-T5 from T2 but misses start-of-T5.
    """

    program: dict[int, int] = field(default_factory=dict)
    storage: dict[int, int] = field(default_factory=dict)
    program_delay: int = 0
    storage_delay: int = 0
    program_readonly_pages: frozenset[int] = field(default_factory=frozenset)
    devices: dict[int, int] = field(default_factory=dict)
    device_delay: int = 0

    def __post_init__(self):
        for name, cells, limit in [("program", self.program, 1024),
                                   ("storage", self.storage, 1024),
                                   ("devices", self.devices, 256)]:
            for address, value in cells.items():
                if type(address) is not int or not 0 <= address < limit:
                    raise ModelError(f"Invalid {name} address: {address}")
                if type(value) is not int or not 0 <= value < 256:
                    raise ModelError(f"Invalid {name} byte: {value}")
        self.program_readonly_pages = frozenset(self.program_readonly_pages)
        for page in self.program_readonly_pages:
            if type(page) is not int or not 0 <= page < 4:
                raise ModelError(f"Invalid read-only program page: {page}")
        for delay in (self.program_delay, self.storage_delay, self.device_delay):
            if type(delay) is not int or delay < 0:
                raise ModelError("Memory delays must be nonnegative whole subdivisions")

    def _cells(self, space):
        if space == "program":
            return self.program
        if space == "storage":
            return self.storage
        if space == "devices":
            return self.devices
        raise ModelError(f"Unknown address space: {space}")

    def read(self, space, address, elapsed):
        delays = {"program": self.program_delay, "storage": self.storage_delay,
                  "devices": self.device_delay}
        cells = self._cells(space)
        return cells.get(address) if elapsed >= delays[space] else None

    def write(self, space, address, value):
        """Commit stable data at WRITE falling; device capture is an assumption."""
        cells = self._cells(space)
        if space == "program" and address >> 8 in self.program_readonly_pages:
            raise ModelError(f"Program page {address >> 8} is read-only")
        cells[address] = value


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
    control_ir: int | None
    flag_effect: FlagInstruction | None
    branch_taken: bool | None

    def to_dict(self):
        return asdict(self)


class InstructionSimulator:
    """Step one subdivision or execute one supported instruction.

    All memory-ready checks require ready=True. Waiting, interrupts and HALT
    remain outside this version. The state must start at an instruction boundary.
    """

    def __init__(self, state: State, memory: Memory, *, interpretation="text", ready=True,
                 test_inputs=(None, None, None, None)):
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
        # Logical levels at T0–T3, independently of PG. May be changed
        # between steps for timing experiments; unknowns never default low.
        self.test_inputs = tuple(test_inputs)
        evaluate(self.state, (), test_inputs=self.test_inputs)
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
        if phase == 0 and timing < 6:
            controls = LRS[0][timing]
            if timing == 2:
                previous_flag = FLAG_INSTRUCTIONS.get(self.state.ir)
                if previous_flag is not None:
                    controls = (*controls, previous_flag.mop)
            return controls
        if self.instruction == "LRS" and self.interpretation == "printed":
            return PRINTED_LRS[phase][timing]
        controls = SEQUENCES[self.instruction][phase][timing]
        if self.instruction in BRANCHES and (phase, timing) == (2, 6):
            if self.state.h is None:
                raise ModelError("Conditional write needs a known sampled H")
            if self.state.h == 0:
                # Fig.5.5 ORs H.Q-bar/T6 with the static PLA's MOP22.
                controls = (*controls, 22)
                if self.instruction in PAGE_BRANCHES:
                    controls = (*controls, 15)
        return controls

    def _memory_space(self, mops):
        """Select one external address space with PME, SME or EDE."""
        selected = [space for number, space in
                    [(24, "program"), (25, "storage"), (26, "devices")]
                    if number in mops]
        if len(selected) > 1:
            raise ModelError("Multiple external address spaces selected")
        return selected[0] if selected else None

    def _address(self, space):
        if self.state.ab is None:
            raise ModelError("External access needs known AB")
        if space == "devices":
            return self.state.ab  # p.43: I/O does not use page bits.
        if self.state.pg is None:
            raise ModelError("Memory access needs known PG")
        return (self.state.pg << 8) | self.state.ab

    def _bus(self, mops, point):
        """Resolve ideal external memory response for this capture endpoint."""
        space = self._memory_space(mops)
        if 23 in mops or space is None:
            key = None  # External memory releases DB when CPU drives it.
        else:
            key = (space, self._address(space))
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
        devices_before = dict(self.memory.devices)
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
            self.memory.devices.clear()
            self.memory.devices.update(devices_before)
            raise

    def _step(self):
        phase, timing = self.state.phase, self.state.timing
        if phase == 0 and timing == 0:
            self.instruction = None  # Label the new fetch independently of retained IR.
        control_ir = self.state.ir
        flag_effect = (FLAG_INSTRUCTIONS.get(control_ir)
                       if phase == 0 and timing == 2 else None)
        if phase == 0 and timing == 6:
            try:
                self.instruction = decode(self.state.ir)
            except ValueError as error:
                raise ModelError(str(error)) from error
        mops = self._controls(phase, timing)
        zero_source = ZERO_SOURCES.get((self.instruction, phase, timing), "alu")
        alu_a_mode = ALU_A_MODES.get((self.instruction, phase, timing), "di")
        label = f"F{phase}T{timing}"
        bus_start = self._bus(mops, "start")
        # Validate resolved DB, including legitimate CPU-driven loopback.
        # A DB->BR transfer must have valid data at the leading boundary.
        resolved_start = evaluate(self.state, mops, external_db=bus_start, memory_ready=True,
                                  test_inputs=self.test_inputs, zero_source=zero_source,
                                  alu_a_mode=alu_a_mode)
        if 2 in mops and resolved_start.db is None:
            raise ModelError(f"{label}: DB is not valid at start of T5 for BR capture")
        if 12 in mops and resolved_start.mux is None:
            raise ModelError(f"{label}: ALU/MUX result is not known for BR capture")
        if 32 in mops and resolved_start.zero_value is None:
            raise ModelError(f"{label}: zero-test value is not known")
        if alu_a_mode == "capture" and resolved_start.alu_a_value is None:
            raise ModelError(f"{label}: ALU input A is not known for holding-latch capture")
        start = self.cpu.capture(mops, external_db=bus_start, memory_ready=True,
                                 point="start", label=f"{label} start", test_inputs=self.test_inputs,
                                 zero_source=zero_source, alu_a_mode=alu_a_mode)
        bus_end = self._bus(mops, "end")
        resolved_end = evaluate(self.state, mops, external_db=bus_end, memory_ready=True,
                                test_inputs=self.test_inputs, zero_source=zero_source,
                                alu_a_mode=alu_a_mode)
        if 1 in mops and resolved_end.db is None:
            raise ModelError(f"{label}: DB is not valid at end of T5 for IR capture")
        end = self.cpu.capture(mops, external_db=bus_end, memory_ready=True,
                               point="end", label=f"{label} end", test_inputs=self.test_inputs,
                               zero_source=zero_source, alu_a_mode=alu_a_mode)

        write = None
        write_high = 27 in mops
        if write_high or self._write_high:
            signals = evaluate(self.state, mops, memory_ready=True)
            space = self._memory_space(mops)
            if space is None or 23 not in mops or signals.db is None:
                raise ModelError(f"{label}: WRITE needs a selected device/memory and CPU-driven data")
            sample = MemoryWrite(space, self._address(space), signals.db)
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

        record = SlotTrace(MODEL_VERSION, self.interpretation,
                           self.instruction or "FETCH", phase, timing,
                           tuple(mops), start, end, write, control_ir, flag_effect,
                           self.state.h == 0 if self.instruction in BRANCHES
                           and (phase, timing) == (2, 6) else None)
        self.trace.append(record)
        self._slots += 1
        # MOP31 can already have changed phase at T1. Keep that captured
        # value; the next slot is F2T2, not F2T0. At a phase boundary,
        # MOP30's captured reset wins over advancement.
        # Instruction length follows the controls, not a fixed 24-slot loop.
        if timing == 7 and 30 not in mops:
            self.state.phase = phase + 1
        self.state.timing = (timing + 1) % 8
        return record

    def run_instruction(self):
        """Run from F0T0 to the next F0T0; return its 8, 16 or 24 slot records.

        A flag instruction's effect is deferred to the next fetch's T2;
        returning here does not force that effect to happen early."""
        if (self.state.phase, self.state.timing) != (0, 0):
            raise ModelError("run_instruction requires an instruction boundary")
        self.instruction = None
        begin = len(self.trace)
        while True:
            self.step()
            if (self.state.phase, self.state.timing) == (0, 0):
                return self.trace[begin:]
