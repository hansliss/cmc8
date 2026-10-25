; Human-readable companion to figure8.6, printed pp.146–147.
; All numeric constants below have an o suffix and are octal.
; The executable bytes are separately preserved in specification/traffic-program.json.
; Assemble with the standalone C tool in assembler/; no assembler is needed to run the board fixture.

        ORG 000o                  ; Program-memory page0; R0 is main PC.
        LRM R3,LIGHT0
        SRD R3,004o               ; ED4 drives both sets of traffic lamps.
HIT:    BT1 1,FRAM                ; Demand on T1 or T3.
        BT1 3,FRAM
        JMP 0,HIT
FRAM:   LRM R3,LIGHT1
        SRD R3,004o
        JSR WAIT10
        LRM R3,LIGHT2
        SRD R3,004o
        JSR WAIT10
        JSR WAIT10
        LRM R3,LIGHT3
        SRD R3,004o
        JSR WAIT10
        JSR WAIT10
        JSR WAIT10
        LRM R3,LIGHT4
        SRD R3,004o
        JSR WAIT10
        JSR WAIT10
        LRM R3,LIGHT2
        SRD R3,004o
        JSR WAIT10
        LRM R3,LIGHT0
        SRD R3,004o
        JMP 0,HIT

        ORG 066o
LIGHT0: BYTE 044o                  ; Main green; side red.
LIGHT1: BYTE 046o                  ; Main green+yellow; side red.
LIGHT2: BYTE 041o                  ; Both roads red.
LIGHT3: BYTE 201o                  ; Main red; side green.
LIGHT4: BYTE 301o                  ; Main red; side green+yellow.
        BYTE 000o,000o,000o,000o,000o ; Reserved light patterns.

        ORG 100o                  ; JSR selects R1 as PC; R0 retains the return.
WAIT10: LRI R3,#000o
        LRI R4,#172o              ; 122 decimal, despite printed “dec76”.
HOPP:   INR R3
        BZ0 0,HOPP                ; Repeat until the byte wraps to zero.
        DCR R4
        BZ0 0,HOPP                ; Repeat 122 batches of 256 increments.
        RSR
