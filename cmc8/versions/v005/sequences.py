"""CMC8 control tables, with transcription kept separate from interpretation.

Source: printed pp.52–55, figures 4.10–4.13 (Page_058.jpg–Page_061.jpg).
Each row is a phase; each tuple is the full set of controls held over T0–T7.
"""

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
# H004: p.51 establishes common fetch through T5; p.67 gives NOP one cycle.
# T6 is idle in this minimal model; T7 resets the phase using MOP30.
# Retaining the LRS T6 BR->AB transfer is an unresolved alternative, not
# required for NOP's architectural effect. See docs/model-v005.md.
NOP = ((*LRS[0][:6], (), (30,)),)

SEQUENCES = {"NOP": NOP, "LRS": LRS, "SRS": SRS, "LRM": LRM, "SRM": SRM,
             "LRD": LRD, "SRD": SRD}


def decode(opcode):
    """Figure 5.1, p.67: NOP and six direct-address load/store families."""
    if opcode is None:
        raise ValueError("Cannot decode an unknown opcode")
    if opcode == 0x00:
        return "NOP"
    families = {0x10: "LRD", 0x18: "SRD", 0x40: "LRM", 0x50: "LRS", 0x60: "SRM", 0x70: "SRS"}
    family = opcode & 0xF8
    if family in families:
        return families[family]
    raise ValueError(f"Unsupported opcode 0x{opcode:02X}; only NOP and LRM/LRS/SRM/SRS/LRD/SRD are implemented")
