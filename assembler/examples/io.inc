; A reusable include guard and a tiny two-instruction output macro.
IFNDEF CMC8_IO_MACROS
CMC8_IO_MACROS EQU 1

MACRO OUT port, value
    LRI R3,#\value
    SRD R3,\port
ENDM

ENDIF
