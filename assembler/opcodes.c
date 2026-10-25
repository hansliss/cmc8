#include "asm.h"

/* Figure5.1. Register selectors and PP/TT fields are inserted by assemble.c. */
static const Instruction instructions[] = {
    {"NOP",0x00,1,OP_NONE}, {"DIN",0x02,1,OP_NONE}, {"EIN",0x03,1,OP_NONE},
    {"REL",0x04,1,OP_NONE}, {"SEL",0x05,1,OP_NONE}, {"REZ",0x06,1,OP_NONE},
    {"SEZ",0x07,1,OP_NONE}, {"SCW",0x08,2,OP_CONTROL}, {"SCS",0x09,2,OP_CONTROL},
    {"JSR",0x0C,2,OP_CALL}, {"RSR",0x0F,1,OP_NONE},
    {"LRD",0x10,2,OP_PORT}, {"SRD",0x18,2,OP_PORT},
    {"LRI",0x20,2,OP_IMMEDIATE}, {"XRI",0x28,2,OP_IMMEDIATE},
    {"ANI",0x30,2,OP_IMMEDIATE}, {"CPY",0x38,1,OP_REG},
    {"LRM",0x40,2,OP_MEMORY}, {"LRX",0x48,1,OP_REG},
    {"LRS",0x50,2,OP_MEMORY}, {"LSX",0x58,1,OP_REG},
    {"SRM",0x60,2,OP_MEMORY}, {"SRX",0x68,1,OP_REG},
    {"SRS",0x70,2,OP_MEMORY}, {"SSX",0x78,1,OP_REG},
    {"INR",0x80,1,OP_REG}, {"ROR",0x88,1,OP_REG}, {"SHR",0x90,1,OP_REG},
    {"RRL",0x98,1,OP_REG}, {"DCR",0xA0,1,OP_REG}, {"XOR",0xA8,1,OP_REG},
    {"AND",0xB0,1,OP_REG}, {"EXR",0xB8,1,OP_REG},
    {"BT0",0xC0,2,OP_TEST_BRANCH}, {"BT1",0xC8,2,OP_TEST_BRANCH},
    {"BB0",0xD0,2,OP_BIT_BRANCH}, {"BB1",0xD8,2,OP_BIT_BRANCH},
    {"BZ0",0xE0,2,OP_PAGE_BRANCH}, {"BL0",0xE4,2,OP_PAGE_BRANCH},
    {"BZ1",0xE8,2,OP_PAGE_BRANCH}, {"BL1",0xEC,2,OP_PAGE_BRANCH},
    {"JMP",0xF0,2,OP_PAGE_BRANCH}, {"JCR",0xF8,1,OP_REG}
};

const Instruction *instruction(const char *name)
{
    size_t i;
    for (i = 0; i < sizeof(instructions) / sizeof(instructions[0]); ++i)
        if (same(name, instructions[i].name)) return &instructions[i];
    return NULL;
}
