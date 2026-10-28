#ifndef TRAFFIC_CPU_H
#define TRAFFIC_CPU_H
#include <stdint.h>

/* -1 is unknown or undriven; it is never silently turned into zero. */
struct cpu_state {
    int16_t r[8], ir, br, ab, pg, n, z, h, t, phase, timing;
};
struct cpu_signals { int16_t selected, di, db, alu, mux; };
struct cpu {
    struct cpu_state s;
    struct cpu_signals start, end;
    uint64_t mops;
    uint32_t slots, writes, last_write_slot;
    int instruction, last_phase, last_timing, last_instruction;
    int16_t lamps;
    uint8_t tests, fault, write_high;
    int16_t pending_address, pending_value;
};
void cpu_init(struct cpu *);
int cpu_step(struct cpu *); /* One T subdivision; zero on fault, no further progress. */
const char *cpu_instruction(const struct cpu *);
int cpu_program(unsigned address); /* Sparse literal book image; -1 outside supplied cells. */
#endif
