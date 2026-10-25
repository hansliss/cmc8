"""Figure 4.2 plus branch and shift extensions in chapter 5, CMC8 only.

English transcription; NOT a claim that each MOP is a physical wire.
MOP1–50: p.38; MOP51–55: p.72; MOP57: p.79 shift circuit.
Numbers are preserved so traces can be compared with the book.
"""

MOPS = {
    1: "DB → IR",
    2: "DB → BR",
    3: "BR → ALU input B",
    4: "BR → DI",
    5: "complement BR → DI",
    6: "BR → AB",
    7: "DI → ALU input A",
    8: "DI XOR BR in ALU",
    9: "DI AND BR in ALU",
    10: "DI + 1 in ALU",
    11: "shift one step right in MUX",
    12: "ALU → BR via MUX",
    13: "ALU bit 0 → BR bit 7 in MUX",
    14: "DI → AB",
    15: "IR bits 0–1 → PG",
    16: "N + 1 → N",
    17: "N - 1 → N",
    18: "select register N",
    19: "select register A",
    20: "select register X",
    21: "register → DI",
    22: "DI → register",
    23: "DI → DB (DBDIR)",
    24: "PME asserted",
    25: "SME asserted",
    26: "EDE asserted",
    27: "WRITE asserted",
    28: "sample /INT",
    29: "sample /MEMR",
    30: "0 → phase",
    31: "2 → phase",
    32: "update Z flag",
    33: "update Link flag",
    34: "1 → L",
    35: "0 → L",
    36: "1 → Z",
    37: "0 → Z",
    38: "1 → INTE",
    39: "0 → INTE",
    40: "0 → DI",
    41: "2 → DI",
    42: "0 → PG",
    43: "0 → MUX bit 7",
    44: "0 → PC",
    45: "0 → N",
    46: "0 → INTR",
    47: "sample /RESET",
    48: "0 → SSE",
    49: "1 → SSE",
    50: "sample /SCWR",
    # Figure 5.5, p.72: additions to the original figure-4.2 platform.
    51: "Z → branch condition input",
    52: "L → branch condition input",
    53: "selected test input → T → branch condition input",
    54: "DI bit 0 → branch condition input",
    55: "clock H at T2 (condition XOR IR bit 3)",
    # Fig.5.11 zero insertion; the original list calls this function 43.
    # These are functional aliases in this model, not proven wire aliases.
    57: "0 → MUX bit 7 (figure 5.11 label)",
}

# These functions still lack implemented capture/source/timing semantics.
# MOP32 now uses the p.75 ALU zero test; H014 adds a provisional DI source
# for the explicitly omitted DCR circuitry. See docs/model-v015.md.
# MOP29 remains always-ready; generic memory waits are not implemented.
# MOP50 now samples SCWR at T4; the sequencer realizes its eight-slot waits.
UNRESOLVED = {
    28: "interrupt sampling, INTA capture and INTR interaction",
    47: "reset distribution, capture timing and affected storage",
}
