/* Generated from specification/instructions.json; regenerate with tools/export_reference.py. */
#ifndef X7_MIDAHS_REFERENCE_H
#define X7_MIDAHS_REFERENCE_H
#define REFERENCE_ROWS 43
#define REFERENCE_PAGE_ROWS 22
#define REFERENCE_PAGES 2
struct reference_row { const char *form, *bits, *octal, *flags, *meaning; unsigned bytes, cycles; };
static const struct reference_row reference_rows[REFERENCE_ROWS] = {
    {"AND Rr", "10110rrr", "260+r", "Z", "Rr AND X TO X", 1, 3},
    {"ANI Rr,#I", "00110rrr", "060+r", "Z", "Rr AND I TO Rr", 2, 3},
    {"BB0 Rr,A", "11010rrr", "320+r", "-", "IF Rr BIT0 CLEAR", 2, 3},
    {"BB1 Rr,A", "11011rrr", "330+r", "-", "IF Rr BIT0 SET", 2, 3},
    {"BL0 p,A", "111001pp", "344+p", "-", "IF L CLEAR", 2, 2},
    {"BL1 p,A", "111011pp", "354+p", "-", "IF L SET", 2, 2},
    {"BT0 t,A", "110000tt", "300+t", "-", "IF TEST t LOW", 2, 2},
    {"BT1 t,A", "110010tt", "310+t", "-", "IF TEST t HIGH", 2, 2},
    {"BZ0 p,A", "111000pp", "340+p", "-", "IF Z CLEAR", 2, 2},
    {"BZ1 p,A", "111010pp", "350+p", "-", "IF Z SET", 2, 2},
    {"CPY Rr", "00111rrr", "070+r", "-", "Rr TO X", 1, 2},
    {"DCR Rr", "10100rrr", "240+r", "Z", "DECREMENT Rr", 1, 3},
    {"DIN", "00000010", "002", "INTE", "DISABLE IRQ", 1, 1},
    {"EIN", "00000011", "003", "INTE", "ENABLE IRQ", 1, 1},
    {"EXR Rr", "10111rrr", "270+r", "-", "EXCHANGE Rr X", 1, 3},
    {"INR Rr", "10000rrr", "200+r", "Z", "INCREMENT Rr", 1, 3},
    {"JCR Rr", "11111rrr", "370+r", "-", "JUMP TO Rr", 1, 2},
    {"JMP p,A", "111100pp", "360+p", "-", "JUMP PAGE p", 2, 2},
    {"JSR A", "00001100", "014", "-", "CALL NEXT PC REG", 2, 3},
    {"LRD Rr,P", "00010rrr", "020+r", "-", "PORT P TO Rr", 2, 3},
    {"LRI Rr,#I", "00100rrr", "040+r", "-", "I TO Rr", 2, 2},
    {"LRM Rr,A", "01000rrr", "100+r", "-", "PM A TO Rr", 2, 3},
    {"LRS Rr,A", "01010rrr", "120+r", "-", "SM A TO Rr", 2, 3},
    {"LRX Rr", "01001rrr", "110+r", "-", "PM X TO Rr", 1, 3},
    {"LSX Rr", "01011rrr", "130+r", "-", "SM X TO Rr", 1, 3},
    {"NOP", "00000000", "000", "-", "FETCH ONLY", 1, 1},
    {"REL", "00000100", "004", "L", "CLEAR L", 1, 1},
    {"REZ", "00000110", "006", "Z", "CLEAR Z", 1, 1},
    {"ROR Rr", "10001rrr", "210+r", "-", "ROTATE RIGHT", 1, 2},
    {"RRL Rr", "10011rrr", "230+r", "L", "RIGHT THROUGH L", 1, 2},
    {"RSR", "00001111", "017", "-", "RETURN PREV PC", 1, 2},
    {"SCS #I", "00001001", "011", "-", "SEND CONTROL", 2, 3},
    {"SCW #I", "00001000", "010", "-", "CONTROL THEN WAIT", 2, 3},
    {"SEL", "00000101", "005", "L", "SET L", 1, 1},
    {"SEZ", "00000111", "007", "Z", "SET Z", 1, 1},
    {"SHR Rr", "10010rrr", "220+r", "-", "SHIFT RIGHT ZERO", 1, 2},
    {"SRD Rr,P", "00011rrr", "030+r", "-", "Rr TO PORT P", 2, 3},
    {"SRM Rr,A", "01100rrr", "140+r", "-", "Rr TO PM A", 2, 3},
    {"SRS Rr,A", "01110rrr", "160+r", "-", "Rr TO SM A", 2, 3},
    {"SRX Rr", "01101rrr", "150+r", "-", "Rr TO PM X", 1, 3},
    {"SSX Rr", "01111rrr", "170+r", "-", "Rr TO SM X", 1, 3},
    {"XOR Rr", "10101rrr", "250+r", "Z", "Rr XOR X TO X", 1, 3},
    {"XRI Rr,#I", "00101rrr", "050+r", "Z", "Rr XOR I TO Rr", 2, 3},
};
#endif
