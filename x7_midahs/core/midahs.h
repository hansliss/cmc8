#ifndef X7_MIDAHS_MACHINE_H
#define X7_MIDAHS_MACHINE_H
#include <stdint.h>
enum midahs_wait { WAIT_NONE, WAIT_RESET, WAIT_MEMR, WAIT_HALT, WAIT_SCWR };
enum midahs_fault { FAULT_NONE, FAULT_OPCODE, FAULT_PORT, FAULT_ROM, FAULT_MODE };
struct midahs {
    uint8_t program[1024], storage[1024], ports[7], r[8];
    unsigned n, pg, z, link, inte, tests, kex, fault;
    /* Logical pin levels, independent of the console's own debugger pause. */
    unsigned reset_level, int_level, memr, halt, ss, scwr, wp;
    unsigned intr, inta, sse, ss_grant, pending_scw, waiting, write_blocked, key_seen;
    int pending_inte; /* EIN/DIN effect at the following ordinary fetch; -1 means none. */
    uint32_t cycles;
};
void midahs_init(struct midahs *);
void midahs_kex(struct midahs *); /* RAM/latches survive, keyboard is released. */
void midahs_inputs(struct midahs *); /* Settle IRQ/SS input latches without executing. */
unsigned midahs_next_cycles(const struct midahs *);
int midahs_step(struct midahs *); /* One instruction/control/wait event; cycles, or zero on fault. */
void midahs_press(struct midahs *, unsigned keycode);
void midahs_release(struct midahs *);
const char *midahs_error(const struct midahs *);
#endif
