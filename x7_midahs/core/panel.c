#include "panel.h"
#include "controls.h"

const struct panel_control panel_controls[CONTROL_COUNT]={
    {18,145,15,3,"SWITCH 0",0},{18,148,15,3,"SWITCH 1",1},
    {18,151,15,3,"SWITCH 2",2},{18,154,15,3,"SWITCH 3",3},
    {18,157,15,3,"SWITCH 4",4},{18,160,15,3,"SWITCH 5",5},
    {18,163,15,3,"SWITCH 6",6},{18,166,15,3,"SWITCH 7",7},
    {316,201,13,14,"GO",0xf1},{331,201,13,14,"AD",0xf3},
    {346,201,13,14,"DA",0xf5},{361,201,13,14,"+",0xf7},
    {316,218,13,14,"4",0xf8},{331,218,13,14,"5",0xfa},
    {346,218,13,14,"6",0xfc},{361,218,13,14,"7",0xfe},
    {316,235,13,14,"0",0xf0},{331,235,13,14,"1",0xf2},
    {346,235,13,14,"2",0xf4},{361,235,13,14,"3",0xf6},
    {299,190,11,11,"KEX",0},
    {22,209,12,10,"TT0",0},{22,221,12,10,"TT1",1},
    {22,233,12,10,"TT2",2},{22,245,12,10,"TT3",3},
    {70,67,12,11,"CL PULSE",0},{70,93,12,12,"CLOCK",0},
    {70,112,12,11,"RESET",0},{70,126,12,11,"INT",0},
    {70,149,12,11,"MEMR",0},{70,162,12,11,"HALT",0},
    {70,174,12,11,"SS",0},{70,195,12,11,"SCWR",0},
    {216,122,12,12,"WP",0}
};

void panel_init(struct panel *p)
{
    *p=(struct panel){.focus=8,.active_key=-1};
    midahs_init(&p->machine);
}

void panel_kex(struct panel *p)
{
    midahs_kex(&p->machine);
    p->active_key=-1; p->pulse_ticks=0; p->remaining_slots=0; p->clock_fraction=0; p->paused=0;
}

void panel_move(struct panel *p, unsigned direction)
{
    if (p->active_key>=0 && (p->held&KEY_A)) return; /* A held key never changes beneath the pointer. */
    const struct panel_control *from=&panel_controls[p->focus];
    int best=0x7fffffff;
    unsigned target=p->focus;
    for (unsigned i=0;i<CONTROL_COUNT;i++) {
        const struct panel_control *to=&panel_controls[i];
        int dx=(to->x+to->w/2)-(from->x+from->w/2);
        int dy=(to->y+to->h/2)-(from->y+from->h/2);
        int horizontal=direction==KEY_LEFT || direction==KEY_RIGHT;
        if ((direction==KEY_LEFT && dx>=0) || (direction==KEY_RIGHT && dx<=0) ||
            (direction==KEY_UP && dy>=0) || (direction==KEY_DOWN && dy<=0)) continue;
        int score=horizontal ? dx*dx+4*dy*dy : dy*dy+4*dx*dx;
        if (score<best) { best=score;target=i; }
    }
    p->focus=target;
}

static void activate(struct panel *p)
{
    if (p->focus<8) p->machine.ports[3]^=(uint8_t)(1u<<p->focus);
    else if (p->focus==CONTROL_KEX) panel_kex(p);
    else if (p->focus>=CONTROL_TT0 && p->focus<CONTROL_CL)
        p->machine.tests^=1u<<(p->focus-CONTROL_TT0);
    else if (p->focus==CONTROL_CL) {
        if (p->clock==CLOCK_MANUAL) panel_clock_pulse(p);
    } else if (p->focus==CONTROL_CLOCK) { p->clock=(p->clock+1)%3; p->clock_fraction=0; }
    else if (p->focus==CONTROL_RESET) p->machine.reset_level^=1;
    else if (p->focus==CONTROL_INT) p->machine.int_level^=1;
    else if (p->focus==CONTROL_MEMR) p->machine.memr^=1;
    else if (p->focus==CONTROL_HALT) p->machine.halt^=1;
    else if (p->focus==CONTROL_SS) p->machine.ss^=1;
    else if (p->focus==CONTROL_SCWR) p->machine.scwr^=1;
    else if (p->focus==CONTROL_WP) { p->machine.wp^=1; p->machine.write_blocked=0; }
    else if (p->active_key<0 && !p->machine.fault) {
        p->active_key=(int)p->focus;
        p->pulse_ticks=2; /* Even a press/release in one raw batch reaches the CPU. */
        midahs_press(&p->machine,panel_controls[p->focus].code);
    }
    midahs_inputs(&p->machine);
}

static unsigned direction(unsigned keys)
{
    if (keys&KEY_UP) return KEY_UP;
    if (keys&KEY_DOWN) return KEY_DOWN;
    if (keys&KEY_LEFT) return KEY_LEFT;
    return keys&KEY_RIGHT;
}

void panel_actions(struct panel *p, unsigned pressed, unsigned held)
{
    p->held=held;
    if (pressed&(KEY_L|KEY_R)) {
        if (!p->help) {
            p->help=1;p->help_page=0;p->direction=0;
            midahs_release(&p->machine);p->active_key=-1;p->pulse_ticks=0;
        } else p->help_page^=1;
        return;
    }
    if (p->help) {
        if (pressed&(KEY_A|KEY_B|KEY_START|KEY_SELECT)) p->help=0;
        else if (pressed&(KEY_LEFT|KEY_RIGHT|KEY_UP|KEY_DOWN)) p->help_page^=1;
        return; /* Help buttons never leak into the emulated panel. */
    }
    if (pressed&KEY_SELECT) {
        const unsigned char *photo=p->photo;
        panel_init(p);p->photo=photo;
        return;
    }
    if (pressed&KEY_B) panel_kex(p);
    if (pressed&KEY_START) p->paused^=1;
    unsigned move=direction(pressed);
    if (move) {panel_move(p,move);p->direction=move;p->repeat_ticks=18;}
    if (pressed&KEY_A) activate(p);
    if (p->active_key>=0 && !(held&KEY_A) && !p->pulse_ticks && (p->machine.key_seen || !p->machine.kex)) {
        midahs_release(&p->machine);p->active_key=-1;
    }
}

void panel_tick(struct panel *p, unsigned held)
{
    p->held=held;
    if (p->help) return; /* Reading the card freezes execution, including virtual clocking. */
    unsigned move=direction(held);
    if (!move) p->direction=0;
    else if (move==p->direction && p->repeat_ticks && !--p->repeat_ticks) {
        panel_move(p,move);p->repeat_ticks=6;
    }
    if (p->paused || (p->machine.fault && p->machine.reset_level)) {
        if (p->pulse_ticks) p->pulse_ticks--;
        if (p->active_key>=0 && !(held&KEY_A) && !p->pulse_ticks && (p->machine.key_seen || !p->machine.kex)) {
            midahs_release(&p->machine);p->active_key=-1;
        }
        return;
    }
    /* H retains the original subdivision rate; L is one machine cycle/sec.
     * Register/port effects still commit only at instruction boundaries. */
    unsigned rate=p->clock==CLOCK_HIGH?125000:p->clock==CLOCK_LOW?8:0;
    p->clock_fraction+=rate;
    unsigned pulses=p->clock_fraction/60;
    p->clock_fraction%=60;
    for (unsigned i=0;i<pulses;i++) panel_clock_pulse(p);
    if (p->pulse_ticks) p->pulse_ticks--;
    if (p->active_key>=0 && !(held&KEY_A) && !p->pulse_ticks && (p->machine.key_seen || !p->machine.kex)) {
        midahs_release(&p->machine);p->active_key=-1;
    }
}

void panel_clock_pulse(struct panel *p)
{
    struct midahs *m=&p->machine;
    if (p->help) return;
    if (m->fault && m->reset_level) return;
    midahs_inputs(m);
    if (!p->remaining_slots) {
        p->planned_cycles=midahs_next_cycles(m);
        p->remaining_slots=8*p->planned_cycles;
    }
    /* A held reset can abort the current approximation at the next T7 edge. */
    if (!m->reset_level) p->remaining_slots=8-(p->clock_pulses&7);
    p->clock_pulses++;
    if (!--p->remaining_slots) {
        unsigned needed=midahs_next_cycles(m);
        /* A wait released during this group must not execute a 2/3-cycle
         * instruction in the single cycle originally reserved for waiting. */
        if (needed>p->planned_cycles) {
            p->remaining_slots=8*(needed-p->planned_cycles);
            p->planned_cycles=needed;
        } else midahs_step(m);
    }
    if (p->active_key>=0 && !(p->held&KEY_A) && !p->pulse_ticks && (m->key_seen || !m->kex)) {
        midahs_release(m);p->active_key=-1;
    }
}

const char *panel_control_state(const struct panel *p,unsigned index)
{
    const struct midahs *m=&p->machine;
    if (index<8) return m->ports[3]&(1u<<index)?"ON":"OFF";
    if (index==CONTROL_KEX) return "PRESS";
    if (index<CONTROL_TT0) return p->active_key==(int)index?"HELD":"PRESS";
    if (index<CONTROL_CL) return m->tests&(1u<<(index-CONTROL_TT0))?"HIGH":"LOW";
    if (index==CONTROL_CL) return p->clock==CLOCK_MANUAL?"PULSE T":"MANUAL ONLY";
    if (index==CONTROL_CLOCK) return p->clock==CLOCK_HIGH?"HIGH":p->clock==CLOCK_MANUAL?"MANUAL":"LOW";
    if (index==CONTROL_RESET) return m->reset_level?"RELEASED":"RESET";
    if (index==CONTROL_INT) return m->int_level?"RELEASED":"REQUEST";
    if (index==CONTROL_MEMR) return m->memr?"BUSY":"READY";
    if (index==CONTROL_HALT) return m->halt?"RUN":"HALT";
    if (index==CONTROL_SS) return m->ss?"RELEASED":"STEP";
    if (index==CONTROL_SCWR) return m->scwr?"WAIT":"ACK";
    return m->wp?"ON":"OFF";
}
