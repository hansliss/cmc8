; Reconstructed KEX monitor, not a dump of the original ROM.
; R0 main PC, R1 subroutine PC, R2 memory mode (P=4,S=2,E=1),
; R3 bit0 DA, bit1 previous key was AD; R4 digit position, R5 scratch,
; R6 key, R7/X scratch.
; Keyboard press/release routine follows corrected figure 8.10.
PAGE 3
ORG 0
keyboard:
        LRD R6,5
        CPY R6
        XRI X,#377o
        BZ1 keyboard
        NOP                     ; Retain figure 8.10's padding byte.
held:   LRD X,5
        XRI X,#377o
        BZ0 held
        RSR
start:  SCS #201o
        LRI R2,#4
        SRD R2,6
        LRI R3,#0
        LRI R4,#0
        LRI R5,#0
        SRD R5,0
        SRD R5,1
refresh:
        LRD X,1
        LSX R5
        SRD R5,2
loop:   JSR keyboard
        BB0 R6,digit
        LRI R4,#0
        XRI R6,#361o
        BZ1 go
        XRI R6,#2
        BZ1 address_mode
        XRI R6,#6
        BZ1 data_mode
; '+' advances address and reads the selected cell.
        ANI R3,#1
        LRD X,1
        INR X
        SRD X,1
        JMP refresh
address_mode:
        ; A second AD cycles P -> S -> E -> P.
        CPY R3
        ANI X,#2
        BZ1 set_address
        SHR R2
        CPY R2
        ANI X,#7
        BZ0 mode_ready
        LRI R2,#4
mode_ready:
        SRD R2,6
set_address:
        LRI R3,#2
        JMP refresh
 data_mode:
        LRI R3,#1
        JMP loop
 digit:
        ANI R3,#1
        SHR R6
        ANI R6,#7
        BB1 R3,data_digit
        ; Four AD digits: page then three offset digits.
        CPY R4
        ANI X,#255
        BZ0 offset_digit
        ANI R6,#3
        ; Replicate the page into all three display fields (E,S,P).
        CPY R6
        ROR R6
        ROR R6
        ROR R6
        ROR R6
        ROR R6
        XOR R6
        ROR R6
        ROR R6
        ROR R6
        ROR R6
        ROR R6
        XOR R6
        SRD X,0
        LRI R5,#0
        SRD R5,1
        INR R4
        JMP refresh
 offset_digit:
        LRD R5,1
        JSR append
        SRD X,1
        INR R4
        CPY R4
        XRI X,#4
        BZ0 refresh
        LRI R4,#0
        JMP refresh
 data_digit:
        LRD R5,2
        CPY R4
        ANI X,#255
        BZ0 append_data
        LRI R5,#0
 append_data:
        JSR append
        SRD X,2
        LRD R5,2
        LRD X,1
        SSX R5
        INR R4
        CPY R4
        XRI X,#3
        BZ0 loop
        LRI R4,#0
        JMP loop
 append:
        ; (old << 3) | digit, modulo 256. Five rotates after mask.
        ANI R5,#37o
        ROR R5
        ROR R5
        ROR R5
        ROR R5
        ROR R5
        CPY R5
        XOR R6
        RSR
 go:
        ; Build the book's page-2 trampoline at 316/317 octal.
        LRD R5,0
        ANI R5,#3
        LRI R6,#360o
        CPY R5
        XOR R6
        EXR R6
        LRD R5,1
        LRI X,#2
        SRD X,0
        LRI X,#4
        SRD X,6
        LRI X,#316o
        SSX R6
        INR X
        SSX R5
        SCS #200o
        JMP 2,316o
ASSERT $ <= 3*256+363o,"Monitor overlaps KEX entry"
ORG 363o
        JMP start
