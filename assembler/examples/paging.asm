; JSR cannot change PG, and RSR does not restore it.
; An explicit pair of jumps bridges pages while keeping the return on page0.
PAGE 0
ORG 0
main:       JSR call_page3
returned:   NOP
            JMP returned

call_page3: JMP worker
return_stub: RSR                 ; Executed on page0 before selecting the saved PC.

PAGE 3
ORG 020o
worker:     LRI R3,#0x69
            JMP return_stub      ; Encodes PG=0 from the label.
