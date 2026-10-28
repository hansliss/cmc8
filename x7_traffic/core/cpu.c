/* Selected v018 MOP datapath for the book's traffic instruction subset.
 * No opcode directly changes a register or supplies an expected light pattern.
 * All transfers are consequences of active numbered MOPs and old wire values.
 */
#include "cpu.h"
#include "../generated/tables.h"
#define HAS(number) ((mops & (UINT64_C(1) << (number))) != 0)

int cpu_program(unsigned address)
{
    /* The transcription is contiguous, but keep the sparse contract explicit. */
    if (address < sizeof(program_cells)/sizeof(program_cells[0]) &&
        program_cells[address].address == address) return program_cells[address].value;
    return -1;
}

static int decode(int ir)
{
    if (ir == 0) return NOP;
    if (ir == 0x0c) return JSR;
    if (ir == 0x0f) return RSR;
    if ((ir & 0xf8) == 0x40) return LRM;
    if ((ir & 0xf8) == 0x18) return SRD;
    if ((ir & 0xf8) == 0x20) return LRI;
    if ((ir & 0xf8) == 0x80) return INR;
    if ((ir & 0xf8) == 0xa0) return DCR;
    if ((ir & 0xfc) == 0xc0) return BT0;
    if ((ir & 0xfc) == 0xc8) return BT1;
    if ((ir & 0xfc) == 0xe0) return BZ0;
    if ((ir & 0xfc) == 0xe8) return BZ1;
    if ((ir & 0xfc) == 0xf0) return JMP;
    return FETCH;
}

void cpu_init(struct cpu *cpu)
{
    *cpu = (struct cpu){0};
    cpu->s = (struct cpu_state){.ir=-1,.br=-1,.ab=-1,.pg=-1,.n=-1,
                               .z=-1,.h=-1,.t=-1,.phase=0,.timing=0};
    for (unsigned i=0; i<8; i++) cpu->s.r[i] = -1;
    cpu->start = cpu->end = (struct cpu_signals){-1,-1,-1,-1,-1};
    cpu->instruction = cpu->last_instruction = RESET;
    cpu->lamps = -1;
}

static struct cpu_signals evaluate(const struct cpu *cpu, uint64_t mops)
{
    const struct cpu_state *s = &cpu->s;
    struct cpu_signals wires = {-1,-1,-1,-1,-1};
    if (HAS(18)) wires.selected = s->n;
    if (HAS(19) && s->ir >= 0) wires.selected = s->ir & 7;
    if (HAS(20)) wires.selected = 7;
    if (HAS(4)) wires.di = s->br;
    if (HAS(5) && s->br >= 0) wires.di = s->br ^ 255;
    if (HAS(21) && wires.selected >= 0) wires.di = s->r[wires.selected];
    if (HAS(40)) wires.di = 0;
    if (HAS(41)) wires.di = 2;

    if (HAS(23)) wires.db = wires.di;
    else if (HAS(24) && s->pg >= 0 && s->ab >= 0)
        wires.db = cpu_program((unsigned)(s->pg*256+s->ab));
    if (HAS(7) && wires.di >= 0) {
        if (HAS(10)) wires.alu = (wires.di+1) & 255;
        else if (!HAS(3)) wires.alu = wires.di;
        else if (s->br >= 0) wires.alu = (wires.di+s->br) & 255;
    }
    wires.mux = wires.alu; /* No shifting instructions in this selected repertoire. */
    return wires;
}

int cpu_step(struct cpu *cpu)
{
    if (cpu->fault) return 0;
    const int phase = cpu->s.phase, timing = cpu->s.timing;
    if (phase == 0 && timing == 0 && cpu->instruction != RESET) cpu->instruction = FETCH;
    if (phase == 0 && timing == 6 && cpu->instruction != RESET) {
        cpu->instruction = decode(cpu->s.ir);
        if (cpu->instruction == FETCH) { cpu->fault=1; return 0; }
    }
    uint64_t mops;
    if (cpu->instruction == RESET) mops = reset_mops[timing];
    else if (phase == 0 && timing < 6) mops = fetch_mops[timing];
    else if (cpu->instruction >= 0 && phase < 3) mops = instruction_mops[cpu->instruction][phase][timing];
    else { cpu->fault=2; return 0; }

    if (phase == 0 && timing == 0 && cpu->instruction != RESET) mops |= UINT64_C(1)<<28;
    /* H022 ready-memory checkpoints at external reads. This fixture never waits. */
    if (timing == 4 && HAS(24) && !HAS(23) && cpu->instruction >= 0 &&
        (phase == 0 || (instruction_mops[cpu->instruction][phase][5] & (UINT64_C(1)<<2))))
        mops |= UINT64_C(1)<<29;

    /* Figure 5.5's H.Q-bar adds the conditional PC and page capture at T6. */
    int branch = cpu->instruction == BT0 || cpu->instruction == BT1 ||
                 cpu->instruction == BZ0 || cpu->instruction == BZ1;
    if (branch && phase == 2 && timing == 6 && cpu->s.h == 0) {
        mops |= UINT64_C(1)<<22;
        if (cpu->instruction == BZ0 || cpu->instruction == BZ1) mops |= UINT64_C(1)<<15;
    }
    /* Quiet INT, released RESET and ready memory are fixture inputs. RESET's
     * asynchronous INTA clear has no visible register in this selected core. */
    if (timing == 7) mops |= UINT64_C(1)<<47;
    cpu->mops = mops;
    cpu->last_phase = phase;
    cpu->last_timing = timing;
    cpu->last_instruction = cpu->instruction;
    struct cpu_signals wires = evaluate(cpu,mops);
    struct cpu_state next = cpu->s;
    int zero = cpu->instruction == DCR ? wires.di : wires.alu;
    if ((HAS(1) || HAS(2)) && wires.db < 0) { cpu->fault=3; return 0; }
    if (HAS(12) && wires.mux < 0) { cpu->fault=4; return 0; }
    if ((HAS(22) && (wires.selected < 0 || wires.di < 0)) || (HAS(32) && zero < 0)) {
        cpu->fault=5; return 0;
    }
    if (HAS(1)) next.ir = wires.db;
    if (HAS(2)) next.br = wires.db;
    if (HAS(12)) next.br = wires.mux;
    if (HAS(6)) next.ab = cpu->s.br;
    if (HAS(14)) next.ab = wires.di;
    if (HAS(15)) next.pg = cpu->s.ir & 3;
    if (HAS(16)) next.n = (cpu->s.n+1) & 7;
    if (HAS(17)) next.n = (cpu->s.n+7) & 7;
    if (HAS(22)) next.r[wires.selected] = wires.di;
    if (HAS(32)) next.z = zero == 0; /* Selected H014 DI detector for DCR. */
    if (HAS(42)) next.pg = 0;
    if (HAS(45)) next.n = 0;
    if (HAS(30)) next.phase = 0;
    if (HAS(31)) next.phase = 2;
    if (HAS(53)) next.t = (cpu->tests >> (cpu->s.ir & 3)) & 1;
    if (HAS(55)) {
        int condition = HAS(51) ? cpu->s.z : next.t;
        if (condition < 0) { cpu->fault=6; return 0; }
        next.h = condition ^ ((cpu->s.ir >> 3) & 1);
    }
    cpu->start = wires;
    cpu->s = next; /* All leading-edge storage captures use OLD wires. */
    cpu->end = evaluate(cpu,mops);
    /* IR is transparent across its T5 slot; other destinations capture once. */
    if (HAS(1)) cpu->s.ir = cpu->end.db;

    if (HAS(27) || cpu->write_high) {
        if (!HAS(26) || !HAS(23) || cpu->s.ab != 4 || cpu->end.db < 0) {
            cpu->fault=7; return 0;
        }
        if (cpu->write_high && (cpu->pending_address != cpu->s.ab || cpu->pending_value != cpu->end.db)) {
            cpu->fault=8; return 0;
        }
        cpu->pending_address = cpu->s.ab;
        cpu->pending_value = cpu->end.db;
        if (!HAS(27)) {
            cpu->lamps = cpu->pending_value;
            cpu->last_write_slot = cpu->slots;
            cpu->writes++;
        }
    }
    cpu->write_high = HAS(27);
    cpu->slots++;
    if (timing == 7 && !HAS(30)) cpu->s.phase = phase+1;
    cpu->s.timing = (timing+1) & 7;
    if (cpu->instruction == RESET && timing == 7) cpu->instruction = FETCH;
    return 1;
}

const char *cpu_instruction(const struct cpu *cpu)
{
    int instruction = cpu->last_instruction;
    return instruction == RESET ? "RESET" : instruction == FETCH ? "FETCH" : instruction_names[instruction];
}
