"""Figure 4.2, printed p.38 (Page_044.jpg), CMC8 only.

English transcription; NOT a claim that each MOP is a physical wire.
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
}

# These functions are catalogued, but these two figures alone do not give
# enough information to implement their capture/source/timing semantics.
# MOP29 has a conditional, always-ready path in v006; waiting remains unresolved.
UNRESOLVED = {
    28: "interrupt sampling, INTA capture and INTR interaction",
    32: "Z update source and capture timing",
    33: "Link update source and capture timing",
    47: "reset distribution, capture timing and affected storage",
    50: "SCWR/SSE handshake and test-input behavior",
}
