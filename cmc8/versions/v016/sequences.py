"""CMC8 control tables, with transcription kept separate from interpretation.

Source: printed pp.52–55, figures 4.10–4.13 (Page_058.jpg–Page_061.jpg).
Each row is a phase; each tuple is the full set of controls held over T0–T7.
"""

from dataclasses import dataclass


# Literal figure 4.12 transcription. The duplicate 24 in F0T2 is retained.
# The printed 1 at F1T5/F2T5 conflicts with figure 4.11 and p.53 prose.
PRINTED_LRS = (
    ((18, 21), (18, 21, 14), (18, 21, 24, 24), (18, 21, 7, 10, 24, 12),
     (4, 18, 29, 22, 24), (1, 24), (6,), ()),
    ((18, 21), (18, 21), (18, 21, 24), (18, 21, 7, 10, 24, 12),
     (4, 18, 29, 22, 24), (1, 24), (6,), ()),
    ((), (), (25,), (25,), (29, 25), (1, 25), (4, 22, 19), (30,)),
)

# Established correction I001 (project-owner decision, 2026-10-24):
# use MOP2 (DB → BR) at the two execution reads. See docs/model-v002.md (inherited correction).
# Keep all other printed controls. A duplicated control asserts only once.
LRS = tuple(
    tuple((2, *mops[1:]) if phase in {1, 2} and timing == 5 else mops
          for timing, mops in enumerate(row))
    for phase, row in enumerate(PRINTED_LRS)
)

# Derived internal schedule for SRS, not a printed MOP table.
# Figure 4.13: F0/F1 program reads; data output around F1T7–F2T5;
# SME F2T0–T5; WRITE F2T1–T4. MOP6 permits AB to load the operand
# address while the source register drives DI (p.52, final paragraph).
SRS = (
    LRS[0],
    (*LRS[1][:6], (6, 19, 21), (19, 21, 23)),
    ((19, 21, 23, 25),
     (19, 21, 23, 25, 27),
     (19, 21, 23, 25, 27),
     (19, 21, 23, 25, 27),
     (19, 21, 23, 25, 27),
     (19, 21, 23, 25),
     (), (30,)),
)

def memory_space_variant(storage_sequence, enable):
    """H002/H003: preserve every control except replace the SME enable.

    Derived from the LRS/SRS model, supported by the LRM observation on
    p.126 (DB carries data during F2T2–F2T5). This is not a transcribed
    program-memory or I/O MOP table.
    """
    phases = []
    for phase in storage_sequence:
        slots = []
        for mops in phase:
            slots.append(tuple(enable if number == 25 else number for number in mops))
        phases.append(tuple(slots))
    return tuple(phases)


LRM = memory_space_variant(LRS, 24)
SRM = memory_space_variant(SRS, 24)
# H003: p.113 explicitly describes an I/O register as a memory word
# activated with EDE rather than PME/SME. No special handshake is added.
LRD = memory_space_variant(LRS, 26)
SRD = memory_space_variant(SRS, 26)
# Selected H006-A: reuse AND's X->DI->DB->BR preparation (fig.5.7),
# with explicit held controls. No memory is enabled in F1. The direct
# X->DI->AB alternative remains in experiments/indexed_address_routes.py.
INDEXED_ADDRESS = (
    (20, 21),             # T0: X drives DI
    (20, 21, 23),         # T1: DI drives DB
    (20, 21, 23),         # T2
    (20, 21, 23),         # T3
    (20, 21, 23),         # T4
    (20, 21, 23, 2),      # T5: CPU-driven DB captured in BR
)
INDEXED_LOAD_F1 = (*INDEXED_ADDRESS, (6,), ())
INDEXED_STORE_F1 = (*INDEXED_ADDRESS, (6, 19, 21), (19, 21, 23))
LRX = (LRM[0], INDEXED_LOAD_F1, LRM[2])
LSX = (LRS[0], INDEXED_LOAD_F1, LRS[2])
SRX = (SRM[0], INDEXED_STORE_F1, SRM[2])
SSX = (SRS[0], INDEXED_STORE_F1, SRS[2])

# Figure 5.3, pp.70–71: phase changes at F1T1 without restarting T.
# The unused F1 cells are retained to show the printed phase layout.
SKIP_TO_F2 = ((), (31,), (), (), (), (), (), ())
JMP = (
    LRS[0],
    SKIP_TO_F2,
    ((), (), (24,), (24,), (24,), (2, 24), (4, 18, 15, 22), (30,)),
)

# Figure 5.4, p.71: fetch target while preserving caller's PC+2, then
# select the next PC register and install the buffered target. PME falls
# at F1T6; the shown sequence does not preload AB from the target there.
JSR = (
    LRS[0],
    (*LRS[1][:6], (), ()),
    ((), (), (16,), (), (), (), (4, 18, 22), (30,)),
)
RSR = (
    LRS[0],
    SKIP_TO_F2,
    ((), (), (17,), (), (), (), (), (30,)),
)

# H007: JCR's p.70 register-target semantics + AND-style register/DB/BR
# preparation + the documented phase skip for two-cycle control flow.
# No memory is enabled in the execute cycle; N and PG remain unchanged.
JCR = (
    LRS[0],
    ((19, 21), (19, 21, 23, 31), (), (), (), (), (), ()),
    ((), (), (19, 21, 23), (19, 21, 23), (19, 21, 23),
     (19, 21, 23, 2), (4, 18, 22), (30,)),
)

# H010: documented immediate semantics, with the existing two-cycle phase
# skip and LRS operand-fetch controls. Increment PC before replacing BR
# with the immediate; then write R(A), even when A aliases the active PC.
# No memory address is taken from the immediate value itself.
LRI = (
    LRS[0],
    ((18, 21), (18, 21, 31), (), (), (), (), (), ()),
    ((), (), *LRS[1][2:6], (4, 19, 22), (30,)),
)

# H011: CPY uses the same buffered register transfer as JCR, changing
# only the destination selector from N to X. Buffering avoids selecting
# source R(A) and destination R7 on the single register port together.
CPY = (
    JCR[0],
    JCR[1],
    (*JCR[2][:6], (4, 20, 22), (30,)),
)

# H019: EXR's semantics/cycles are documented, but its transfer sequence is
# not. This candidate needs an explicit, provisional ALU input-A latch.
# Preserve X in BR, hold R(A) at the ALU input, write old X to R(A),
# reload BR from held A, then write old R(A) to X. No second register port.
EXR = (
    LRS[0],
    (*INDEXED_ADDRESS, (), ()),
    ((19, 21, 7), (), (), (), (4, 19, 22), (12,), (4, 20, 22), (30,)),
)
ALU_A_MODES = {("EXR", 2, 0): "capture", ("EXR", 2, 5): "held"}

# Fig.6.17/6.18: memory supplies the control byte directly to the external
# STRCS latch. Do not capture it in BR or preload AB with it. PME remains
# asserted from F1T2 through F2T5, including any SCWR wait cycles.
SEND_CONTROL_F1 = (
    (18, 21), (18, 21), (18, 21, 24), (18, 21, 7, 10, 24, 12),
    (4, 18, 22, 24), (24,), (24,), (24,),
)
SCW = (
    LRS[0], SEND_CONTROL_F1,
    ((24,), (24,), (24,), (24,), (24, 50), (24,), (), (30,)),
)
# H020: SCS uses the same control-byte/strobe sequence, omitting the
# acknowledgement sample. Its dedicated full timing table was not found.
SCS = (
    LRS[0], SEND_CONTROL_F1,
    ((24,), (24,), (24,), (24,), (24,), (24,), (), (30,)),
)
# STRCS has no numbered MOP in the supplied list; expose the named output.
CONTROL_STROBES = frozenset({("SCS", 1, 6), ("SCW", 1, 6)})

# Fig.4.20b, p.65: an eight-slot entry cycle, not an instruction opcode.
# MOP28 captures the pending request before MOP39/46 disable and clear it.
# Hold constant 02 on DI from T1 through the T4 write. PG is unchanged.
INTERRUPT_ENTRY = (
    (28, 39, 46), (41,), (41, 16), (41,), (41, 18, 22), (), (), (30,),
)

# Fig.5.7: reuse the selected AND-style X preparation already used by
# indexed instructions. Functional DB drive starts T1; the sparse printed
# row also lists MOP23 at T0. H012 selects the functional placement.
AND = (
    LRS[0],
    (*INDEXED_ADDRESS, (), ()),
    ((19, 21), (19, 21), (19, 21), (19, 21, 3, 7, 9, 32, 12),
     (4, 22, 20), (), (), (30,)),
)

# H015: XOR shares AND's documented operand/result roles, cycles and Z
# effect. Substitute only the ALU operation, MOP8 for MOP9.
XOR = tuple(
    tuple(tuple(8 if mop == 9 else mop for mop in slot) for slot in phase)
    for phase in AND
)


def immediate_logic(operation):
    """H016: fetch the immediate like LRS, then use AND's ALU/Z slots.

    BR holds immediate data rather than X; write the result to R(A),
    not X. No target-address preload or third-cycle memory read is needed.
    """
    return (
        LRS[0],
        (*LRS[1][:6], (), ()),
        ((19, 21), (19, 21), (19, 21), (19, 21, 3, 7, operation, 32, 12),
         (4, 22, 19), (), (), (30,)),
    )


XRI = immediate_logic(8)
ANI = immediate_logic(9)

# Fig.5.8: INR needs DI held from R(A), not a buffered DB operand.
# Keep both full execute phases: fig.5.1 and the application establish
# three cycles. H013 selects the table's F2T3 rather than prose F2T2.
REGISTER_OUTPUT = ((19, 21),) + ((19, 21, 23),) * 7
INR = (
    LRS[0],
    REGISTER_OUTPUT,
    ((19, 21), (19, 21), (19, 21), (19, 21, 10, 7, 12, 32),
     (), (), (4, 19, 22), (30,)),
)

# Fig.5.8: decrement using complement-increment-complement; no subtractor.
# H014 adds MOP32 with a named DI zero-test input at final writeback.
# p.77 says the corresponding circuitry/controls were omitted. The added
# MOP32 here is a functional model choice, not a printed DCR control.
DCR = (
    LRS[0],
    (*REGISTER_OUTPUT[:5], (19, 21, 23, 2), (), ()),
    ((5,), (5,), (5,), (5, 10, 7, 12), (), (), (5, 19, 22, 32), (30,)),
)
ZERO_SOURCES = {("DCR", 2, 6): "di"}

# Fig.5.12, selected E003 correction: F1T1's 2->F uses MOP31,
# not printed MOP30. Fig.5.11 MOP33 supplies old Link to bit7 and
# captures ALU bit0 as new Link at F2T2. BR drives DI at T5, write T6.
RRL = (
    LRS[0],
    ((19, 21), (19, 21, 23, 31), (), (), (), (), (), ()),
    ((), (), (19, 21, 7, 11, 12, 33), (), (), (4,), (19, 22, 4), (30,)),
)


def shift_variant(high_source):
    """H018: preserve RRL timing, replacing the Link gate with a source.

    MOP13 wraps ALU bit0 for ROR; MOP43 inserts zero for SHR. Only
    RRL asserts MOP33 and updates Link. Figure 5.11 calls zero insertion
    57; retain 43 from the original functional list in the selected table.
    """
    return tuple(
        tuple(tuple(high_source if mop == 33 else mop for mop in slot) for slot in phase)
        for phase in RRL
    )


ROR = shift_variant(13)
SHR = shift_variant(43)

# Fig.5.6 BB0, selected functional correction: F1T4 uses MOP4, not
# the printed MOP6. Preserve target in BR and operand address in AB.
# MOP22 at F2T6 is supplied by the H circuit, not this static PLA table.
BB0 = (
    LRS[0],
    (*LRS[1][:6], (), ()),
    ((19, 21), (19, 21, 54), (19, 21, 54, 55), (), (), (), (4, 18), (30,)),
)
BB1 = BB0  # IR bit 3 selects the opposite condition in the XOR circuit.


def flag_branch(condition_mop):
    """H008: combine operand increment with the two-cycle phase skip.

    Unlike JMP, the PC must advance past the address even when not taken.
    The flag/test path is independent of the PC's DI path at F2T2.
    """
    return (
        LRS[0],
        ((18, 21), (18, 21, 31), (), (), (), (), (), ()),
        ((), (), (18, 21, 24, condition_mop, 55),
         (18, 21, 7, 10, 24, 12), (4, 18, 22, 24),
         (2, 24), (4, 18), (30,)),
    )


BZ0 = BZ1 = flag_branch(51)
BL0 = BL1 = flag_branch(52)
BT0 = BT1 = flag_branch(53)
BRANCHES = frozenset({"BB0", "BB1", "BZ0", "BZ1", "BL0", "BL1", "BT0", "BT1"})
PAGE_BRANCHES = frozenset({"BZ0", "BZ1", "BL0", "BL1"})

# Figure 4.19 documents EIN's fetch tail: BR->AB at T6, phase reset at T7.
# H005: use it consistently for NOP and all six flag instructions. This
# changes NOP's optional AB preload relative to v005, not its PC/flag effects.
SINGLE_CYCLE = ((*LRS[0][:7], (30,)),)
NOP = SINGLE_CYCLE


@dataclass(frozen=True)
class FlagInstruction:
    name: str
    mop: int
    flag: str
    value: int
    confidence: str
    basis: str


# Exact opcodes from fig.5.1; all six remain provisional implementations.
# EIN has stronger timing evidence (p.62 and fig.4.19).
FLAG_INSTRUCTIONS = {
    0x02: FlagInstruction("DIN", 39, "inte", 0, "likely", "consistency-supported extrapolation"),
    0x03: FlagInstruction("EIN", 38, "inte", 1, "high", "documented timing; derived decoder"),
    0x04: FlagInstruction("REL", 35, "link", 0, "likely", "consistency-supported extrapolation"),
    0x05: FlagInstruction("SEL", 34, "link", 1, "likely", "consistency-supported extrapolation"),
    0x06: FlagInstruction("REZ", 37, "z", 0, "likely", "consistency-supported extrapolation"),
    0x07: FlagInstruction("SEZ", 36, "z", 1, "likely", "consistency-supported extrapolation"),
}

SEQUENCES = {"NOP": NOP, "LRS": LRS, "SRS": SRS, "LRM": LRM, "SRM": SRM,
             "LRD": LRD, "SRD": SRD, "LRX": LRX, "LSX": LSX, "SRX": SRX, "SSX": SSX,
             "JMP": JMP, "JCR": JCR, "JSR": JSR, "RSR": RSR,
             "BB0": BB0, "BB1": BB1, "BZ0": BZ0, "BZ1": BZ1,
             "BL0": BL0, "BL1": BL1, "BT0": BT0, "BT1": BT1,
             "LRI": LRI, "CPY": CPY, "AND": AND, "INR": INR, "DCR": DCR,
             "XOR": XOR, "XRI": XRI, "ANI": ANI,
             "ROR": ROR, "SHR": SHR, "RRL": RRL, "EXR": EXR,
             "SCS": SCS, "SCW": SCW}
for flag_instruction in FLAG_INSTRUCTIONS.values():
    SEQUENCES[flag_instruction.name] = SINGLE_CYCLE


def decode(opcode):
    """Figure 5.1, p.67: implemented instruction families, including all branches."""
    if opcode is None:
        raise ValueError("Cannot decode an unknown opcode")
    if opcode == 0x00:
        return "NOP"
    if opcode in {0x08, 0x09}:
        return "SCW" if opcode == 0x08 else "SCS"
    if opcode == 0x0C:
        return "JSR"
    if opcode == 0x0F:
        return "RSR"
    if opcode & 0xFC == 0xF0:
        return "JMP"
    if opcode & 0xF8 == 0xF8:
        return "JCR"
    if opcode in FLAG_INSTRUCTIONS:
        return FLAG_INSTRUCTIONS[opcode].name
    page_branches = {0xC0: "BT0", 0xC8: "BT1", 0xE0: "BZ0", 0xE8: "BZ1",
                     0xE4: "BL0", 0xEC: "BL1"}
    if opcode & 0xFC in page_branches:
        return page_branches[opcode & 0xFC]
    if opcode & 0xF8 in {0xD0, 0xD8}:
        return "BB1" if opcode & 8 else "BB0"
    families = {0x10: "LRD", 0x18: "SRD", 0x20: "LRI", 0x28: "XRI",
                0x30: "ANI", 0x38: "CPY",
                0x40: "LRM", 0x48: "LRX", 0x50: "LRS", 0x58: "LSX",
                0x60: "SRM", 0x68: "SRX", 0x70: "SRS", 0x78: "SSX",
                0x80: "INR", 0x88: "ROR", 0x90: "SHR", 0x98: "RRL",
                0xA0: "DCR", 0xA8: "XOR", 0xB0: "AND", 0xB8: "EXR"}
    family = opcode & 0xF8
    if family in families:
        return families[family]
    raise ValueError(f"Unsupported opcode 0x{opcode:02X}; instruction is not implemented by this model")
