; Default user program: switches ED3 -> output lamps ED4 (book p.126).
PAGE 0
ORG 0
loop:   LRD R3,3
        SRD R3,4
        JMP loop
