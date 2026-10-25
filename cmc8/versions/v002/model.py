"""Experimental datapath for figures 4.1–4.2; see docs/model-v002.md.

Evaluate combinational paths first, then explicitly capture storage. A capture
is an experiment boundary, NOT an inferred CMC8 clock edge or timing slot.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field

from .mops import MOPS, UNRESOLVED

MODEL_VERSION = "v002"


class ModelError(ValueError):
    """The requested experiment has an ambiguous or unavailable meaning."""


@dataclass
class State:
    # None means unknown, including power-on state. Never assume power-on zero.
    registers: list[int | None] = field(default_factory=lambda: [None] * 8)
    ir: int | None = None
    br: int | None = None
    ab: int | None = None
    pg: int | None = None
    n: int | None = None
    link: int | None = None
    z: int | None = None
    inte: int | None = None
    intr: int | None = None
    inta: int | None = None
    wait: int | None = None
    sse: int | None = None
    phase: int | None = None
    timing: int | None = None


@dataclass(frozen=True)
class Evaluation:
    version: str
    mops: tuple[int, ...]
    selected_register: int | None
    di: int | None
    db: int | None
    alu: int | None
    mux: int | None
    outputs: tuple[str, ...]
    writes: dict[str, int | None]
    register_writes: dict[int, int | None]


@dataclass
class Trace:
    version: str
    label: str
    before: State
    signals: Evaluation
    after: State

    def to_dict(self):
        """Return a JSON-serializable record, including the full model identity."""
        return asdict(self)


def validate_state(state):
    if len(state.registers) != 8:
        raise ModelError("The register bank must contain eight registers")
    widths = {"ir": 8, "br": 8, "ab": 8, "pg": 2, "n": 3,
              "phase": 2, "timing": 3}
    for name, value in vars(state).items():
        if name == "registers":
            values, width = value, 8
        else:
            values, width = [value], widths.get(name, 1)
        for item in values:
            if item is not None and (type(item) is not int or not 0 <= item < 2**width):
                raise ModelError(f"Invalid {name} value: {item!r}")


def evaluate(state: State, mops, *, external_db=None, memory_ready=None) -> Evaluation:
    """Resolve controls against old storage, without changing that storage.

    Multiple drivers are rejected even when their values happen to agree.
    Arithmetic without XOR/AND/increment selection is provisionally addition.
    Unknown data propagates as None. An absent bus driver is also None.
    """
    validate_state(state)
    active = frozenset(mops)
    if active - MOPS.keys():
        raise ModelError(f"Unknown MOPs: {sorted(active - MOPS.keys())}")
    unresolved = active & UNRESOLVED.keys()
    if 29 in active:
        if memory_ready is not True:
            raise ModelError("MOP29 requires memory_ready=True; wait cycles are not implemented")
        unresolved = unresolved - {29}
    if unresolved:
        details = "; ".join(f"MOP{n}: {UNRESOLVED[n]}" for n in sorted(unresolved))
        raise ModelError(f"Not yet specified in {MODEL_VERSION}: {details}")
    if external_db is not None and (type(external_db) is not int or not 0 <= external_db <= 255):
        raise ModelError("external_db must be an eight-bit integer or None")

    def exclusive(numbers, description):
        chosen = active.intersection(numbers)
        if len(chosen) > 1:
            raise ModelError(f"Conflicting {description}: {sorted(chosen)}")
        return next(iter(chosen), None)

    selector = exclusive({18, 19, 20}, "register selectors")
    selected = {18: state.n, 19: None if state.ir is None else state.ir & 7,
                20: 7}.get(selector)
    if active & {21, 22} and selector is None:
        raise ModelError("Register transfer requires MOP18, 19 or 20")

    driver = exclusive({4, 5, 21, 40, 41}, "DI drivers")
    di = None
    if driver == 4:
        di = state.br
    elif driver == 5:
        di = None if state.br is None else state.br ^ 255
    elif driver == 21:
        di = None if selected is None else state.registers[selected]
    elif driver in {40, 41}:
        di = 0 if driver == 40 else 2

    if 23 in active and external_db is not None:
        raise ModelError("CPU and external device both drive DB")
    db = di if 23 in active else external_db
    operation = exclusive({8, 9, 10}, "ALU operations")
    a = di if 7 in active else None
    b = state.br if 3 in active else None
    alu = None
    if operation == 10:
        alu = None if a is None else (a + 1) & 255
    elif a is not None and b is not None:
        if operation == 8:
            alu = a ^ b
        elif operation == 9:
            alu = a & b
        else:
            alu = (a + b) & 255

    exclusive({13, 43}, "MUX high-bit sources")
    mux = alu
    if mux is not None and 11 in active:
        # Provisional: Link supplies the shifted-in bit unless overridden.
        high = 0 if 43 in active else (alu & 1 if 13 in active else state.link)
        mux = None if high is None else (alu >> 1) | (high << 7)
    elif mux is not None and 13 in active:
        mux = (mux & 127) | ((alu & 1) << 7)
    elif mux is not None and 43 in active:
        mux &= 127

    writes = {"wait": 0} if 29 in active else {}
    register_writes = {}

    def write(name, value):
        if name in writes:
            raise ModelError(f"Multiple writes to {name}")
        writes[name] = value

    if 1 in active:
        write("ir", db)
    exclusive({2, 12}, "BR sources")
    if 2 in active or 12 in active:
        write("br", db if 2 in active else mux)
    exclusive({6, 14}, "AB sources")
    if 6 in active or 14 in active:
        write("ab", state.br if 6 in active else di)
    exclusive({15, 42}, "PG sources")
    if 15 in active:
        write("pg", None if state.ir is None else state.ir & 3)
    if 42 in active:
        write("pg", 0)
    exclusive({16, 17, 45}, "N updates")
    if 16 in active or 17 in active:
        write("n", None if state.n is None else (state.n + (1 if 16 in active else -1)) & 7)
    if 45 in active:
        write("n", 0)
    for zero, one, name in [(35, 34, "link"), (37, 36, "z"),
                            (39, 38, "inte"), (48, 49, "sse")]:
        choice = exclusive({zero, one}, f"{name} updates")
        if choice is not None:
            write(name, int(choice == one))
    if 46 in active:
        write("intr", 0)
    choice = exclusive({30, 31}, "phase updates")
    if choice is not None:
        write("phase", 0 if choice == 30 else 2)
    if 22 in active:
        if selected is None:
            raise ModelError("Cannot write an unknown register selection")
        register_writes[selected] = di
    if 44 in active:
        if state.n is None:
            raise ModelError("Cannot clear PC while N is unknown")
        if state.n in register_writes:
            raise ModelError("PC clear conflicts with register write")
        register_writes[state.n] = 0

    outputs = tuple(name for number, name in [(23, "DBDIR"), (24, "PME"),
                    (25, "SME"), (26, "EDE"), (27, "WRITE")] if number in active)
    return Evaluation(MODEL_VERSION, tuple(sorted(active)), selected, di, db,
                      alu, mux, outputs, writes, register_writes)


class Simulator:
    """Manual MOP experiments; no automatic instruction decoder or clock yet."""

    def __init__(self, state=None):
        self.state = deepcopy(state) if state is not None else State()
        validate_state(self.state)
        self.trace: list[Trace] = []

    def capture(self, mops, *, external_db=None, label="", point="manual", memory_ready=None) -> Trace:
        """Evaluate then commit all storage writes simultaneously.

        point="start" captures storage and samples an open IR latch;
        point="end" updates only IR. The endpoint samples do not simulate
        arbitrary transitions inside a subdivision.
        Errors leave both state and trace unchanged. DI and DB are wires,
        not retained registers. Call evaluate() for observation without capture.
        """
        if point not in {"manual", "start", "end"}:
            raise ModelError(f"Unknown capture point: {point}")
        before = deepcopy(self.state)
        signals = evaluate(before, mops, external_db=external_db, memory_ready=memory_ready)
        after = deepcopy(before)
        for name, value in signals.writes.items():
            # IR is transparent over T5: expose its start and final samples.
            # Other destinations capture once at the start in this model.
            if point != "end" or name == "ir":
                setattr(after, name, value)
        if point != "end":
            for index, value in signals.register_writes.items():
                after.registers[index] = value
        validate_state(after)
        record = Trace(MODEL_VERSION, label, before, signals, deepcopy(after))
        self.state = after
        self.trace.append(record)
        return record
