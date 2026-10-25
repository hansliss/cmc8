; Parameters are textual; %% labels are unique to each invocation.
INCLUDE "io.inc"

MACRO COUNTDOWN count
    LRI R4,#\count
%%loop:
    DCR R4
    BZ0 %%loop
ENDM

PAGE 0
ORG 0
    OUT 4,044o
    COUNTDOWN 3
    COUNTDOWN 2
    JMP worker             ; Encodes page3 automatically.

PAGE 3
ORG 020o
worker:
    OUT 4,201o
    SCS #0xA6
    JMP worker

ASSERT PAGEOF(worker) == 3
