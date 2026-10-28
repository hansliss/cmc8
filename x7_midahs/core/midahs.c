/* Instruction-level C port of demos/shared/cpu.mjs and demos/midahs/board.mjs.
 * The reconstructed monitor is ordinary machine code; no keys directly edit RAM.
 */
#include "midahs.h"
#include "../generated/programs.h"

void midahs_release(struct midahs *m) { m->ports[5]=255; }
void midahs_press(struct midahs *m, unsigned code) { m->ports[5]=(uint8_t)code; m->key_seen=0; }

void midahs_kex(struct midahs *m)
{
    /* Functional result of RESET plus the book's injected JMP3,363o.
     * No electrical bus injection is simulated here. */
    m->n=0; m->pg=3; m->r[0]=0363; m->cycles=1; m->fault=0; m->kex=0;
    m->pending_scw=0; m->waiting=WAIT_NONE; m->write_blocked=0; m->inta=0;
    midahs_release(m);
}

void midahs_init(struct midahs *m)
{
    *m=(struct midahs){.reset_level=1,.int_level=1,.halt=1,.ss=1,.pending_inte=-1}; /* Explicit demo startup values, not power-on claims. */
    for (unsigned i=0; i<sizeof(initial_cells)/sizeof(initial_cells[0]); i++)
        m->program[initial_cells[i].address]=initial_cells[i].value;
    midahs_kex(m);
}

static unsigned fetch(struct midahs *m)
{
    unsigned value=m->program[m->pg*256+m->r[m->n]];
    m->r[m->n]++;
    return value;
}

static unsigned read_port(struct midahs *m, unsigned port)
{
    if (port==5 && m->ports[5]!=255) m->key_seen=1;
    return port<7 ? m->ports[port] : 255; /* Explicit demo open-bus value. */
}

static void write_port(struct midahs *m, unsigned port, unsigned value)
{
    if (port==0 || port==1 || port==2 || port==4 || port==6) m->ports[port]=(uint8_t)value;
    else m->fault=FAULT_PORT;
}

static unsigned memory_address(struct midahs *m, unsigned *space, unsigned address)
{
    if (m->kex) {
        unsigned mode=m->ports[6]&7;
        if (mode==1) { *space=2; return address; }
        if (mode!=2 && mode!=4) { m->fault=FAULT_MODE; return 0; }
        *space=mode==4 ? 0 : 1;
        unsigned shift=mode==4 ? 0 : 3;
        return ((m->ports[0]>>shift)&3)*256+address;
    }
    return m->pg*256+address;
}

static unsigned read_memory(struct midahs *m, unsigned space, unsigned address)
{
    address=memory_address(m,&space,address);
    return space==2 ? read_port(m,address) : space==0 ? m->program[address] : m->storage[address];
}

static void write_memory(struct midahs *m, unsigned space, unsigned address, unsigned value)
{
    address=memory_address(m,&space,address);
    if (m->fault) return;
    if (space==2) { write_port(m,address,value); return; }
    if (space==0 && m->wp) { m->write_blocked=1; return; }
    if (space==0 && address>=768) { m->fault=FAULT_ROM; return; }
    if (space==0) m->program[address]=(uint8_t)value;
    else m->storage[address]=(uint8_t)value;
}

static void result(struct midahs *m, unsigned reg, unsigned value)
{
    m->r[reg]=(uint8_t)value;
    m->z=m->r[reg]==0;
}

void midahs_inputs(struct midahs *m)
{
    if (m->inte && !m->int_level) m->intr=1;
    if (!m->halt && m->ss) m->sse=1;
    if (!m->halt && !m->ss && m->sse) { m->ss_grant=1; m->sse=0; }
}

static unsigned instruction_cycles(unsigned opcode)
{
    unsigned family=opcode&0xf8;
    if (opcode==0 || (opcode>=2 && opcode<=7)) return 1;
    if (opcode==0x0f || family==0x20 || family==0x38 ||
        family==0x88 || family==0x90 || family==0x98 || family==0xf8 ||
        (opcode&0xfc)==0xc0 || (opcode&0xfc)==0xc8 ||
        (opcode&0xf0)==0xe0 || (opcode&0xfc)==0xf0) return 2;
    return 3;
}

unsigned midahs_next_cycles(const struct midahs *m)
{
    if (!m->reset_level || m->pending_scw || m->intr || m->memr ||
        (!m->halt && !m->ss_grant)) return 1;
    return instruction_cycles(m->program[m->pg*256+m->r[m->n]]);
}

int midahs_step(struct midahs *m)
{
    midahs_inputs(m);
    /* RESET and interrupt entry are separate one-cycle boundary events. Pins
     * are functionally sampled here; this is not the v018 edge sequencer. */
    if (!m->reset_level) {
        m->n=0; m->pg=0; m->r[0]=0; m->inta=0; m->fault=0;
        m->pending_scw=0; m->waiting=WAIT_RESET; m->cycles++;
        return 1;
    }
    if (m->fault) return 0;
    m->waiting=WAIT_NONE;
    if (m->pending_scw) {
        if (m->scwr) m->waiting=WAIT_SCWR;
        else m->pending_scw=0;
        m->cycles++;return 1;
    }
    if (m->intr) {
        m->inta=1; m->intr=0; m->inte=0;
        m->n=(m->n+1)&7; m->r[m->n]=2; m->cycles++;
        return 1;
    }
    m->inta=0;
    /* EIN/DIN take effect in the following ordinary fetch, after that fetch's
     * interrupt acceptance check. A low INT after EIN cannot skip its successor. */
    if (m->pending_inte>=0) {
        m->inte=(unsigned)m->pending_inte;m->pending_inte=-1;
        midahs_inputs(m);
    }
    if (m->memr || (!m->halt && !m->ss_grant)) {
        m->waiting=m->memr?WAIT_MEMR:WAIT_HALT;
        m->cycles++;return 1;
    }
    m->ss_grant=0;
    unsigned opcode=fetch(m), reg=opcode&7, family=opcode&0xf8, cycles=0;
    if (opcode==0) cycles=1;
    else if (opcode>=2 && opcode<=7) {
        /* INTE needs the fetch-tail delay for correct interrupt acceptance.
         * L/Z are visible at boundaries; their next instruction sees the value. */
        if (opcode<4) m->pending_inte=(int)(opcode&1);
        else if (opcode<6) m->link=opcode&1;
        else m->z=opcode&1;
        cycles=1;
    } else if (opcode==8 || opcode==9) {
        unsigned control=fetch(m);
        if ((control&0xc0)==0x80) m->kex=control&1;
        if (opcode==8 && m->scwr) { m->pending_scw=1; m->waiting=WAIT_SCWR; }
        cycles=3;
    } else if (opcode==0x0c) {
        unsigned target=fetch(m);
        m->n=(m->n+1)&7; m->r[m->n]=(uint8_t)target; cycles=3;
    } else if (opcode==0x0f) { m->n=(m->n+7)&7; cycles=2; }
    else if (family==0x10) { m->r[reg]=(uint8_t)read_port(m,fetch(m)); cycles=3; }
    else if (family==0x18) { unsigned port=fetch(m); write_port(m,port,m->r[reg]); cycles=3; }
    else if (family==0x20) { m->r[reg]=(uint8_t)fetch(m); cycles=2; }
    else if (family==0x28 || family==0x30) {
        unsigned operand=fetch(m);
        result(m,reg,family==0x28 ? m->r[reg]^operand : m->r[reg]&operand); cycles=3;
    } else if (family==0x38) { m->r[7]=m->r[reg]; cycles=2; }
    else if (family>=0x40 && family<=0x78) {
        unsigned address=opcode&8 ? m->r[7] : fetch(m), space=opcode&0x10 ? 1 : 0;
        if (opcode&0x20) write_memory(m,space,address,m->r[reg]);
        else m->r[reg]=(uint8_t)read_memory(m,space,address);
        cycles=3;
    } else if (family==0x80 || family==0xa0) {
        result(m,reg,m->r[reg]+(family==0x80 ? 1u : 255u)); cycles=3;
    } else if (family==0x88 || family==0x90 || family==0x98) {
        unsigned value=m->r[reg], high=family==0x88 ? value&1 : family==0x98 ? m->link : 0;
        m->r[reg]=(uint8_t)((value>>1)|(high<<7));
        if (family==0x98) m->link=value&1;
        cycles=2;
    } else if (family==0xa8 || family==0xb0) {
        result(m,7,family==0xa8 ? m->r[reg]^m->r[7] : m->r[reg]&m->r[7]); cycles=3;
    } else if (family==0xb8) {
        unsigned value=m->r[reg]; m->r[reg]=m->r[7]; m->r[7]=(uint8_t)value; cycles=3;
    } else if ((opcode&0xfc)==0xc0 || (opcode&0xfc)==0xc8) {
        unsigned target=fetch(m);
        if (((m->tests>>(opcode&3))&1)==((opcode>>3)&1)) m->r[m->n]=(uint8_t)target;
        cycles=2;
    } else if (family==0xd0 || family==0xd8) {
        unsigned target=fetch(m);
        if ((m->r[reg]&1)==((opcode>>3)&1)) m->r[m->n]=(uint8_t)target;
        cycles=3;
    } else if ((opcode&0xfc)==0xf0 || (opcode&0xf0)==0xe0) {
        unsigned target=fetch(m), condition=opcode&4 ? m->link : m->z;
        if ((opcode&0xfc)==0xf0 || condition==((opcode>>3)&1)) {
            m->pg=opcode&3; m->r[m->n]=(uint8_t)target;
        }
        cycles=2;
    } else if (family==0xf8) { m->r[m->n]=m->r[reg]; cycles=2; }
    else m->fault=FAULT_OPCODE;
    if (m->fault) return 0;
    midahs_inputs(m);
    m->cycles+=cycles;
    return (int)cycles;
}

const char *midahs_error(const struct midahs *m)
{
    static const char *const errors[]={"", "BAD OPCODE", "READONLY PORT", "MONITOR ROM", "MEMORY MODE"};
    return errors[m->fault];
}
