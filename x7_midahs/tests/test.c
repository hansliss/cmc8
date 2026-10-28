#include "demo.h"
#include "controls.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../generated/reference.h"

static void run(struct midahs *m,unsigned instructions)
{
    for (unsigned i=0;i<instructions;i++) assert(midahs_step(m));
}
static unsigned code(char key)
{
    return key>='0' && key<='7' ? 0xf0+2*(unsigned)(key-'0') :
           key=='G'?0xf1:key=='A'?0xf3:key=='D'?0xf5:0xf7;
}
static void tap(struct midahs *m,char key)
{
    midahs_press(m,code(key));run(m,100);midahs_release(m);run(m,200);
}
static void keys(struct midahs *m,const char *s) { while (*s) tap(m,*s++); }

static void monitor_checks(void)
{
    struct midahs m;midahs_init(&m);run(&m,300);
    assert(m.kex && m.ports[6]==4 && m.ports[2]==023);
    midahs_press(&m,code('+'));run(&m,300);
    assert(m.ports[1]==0); /* Figure 8.10 waits for release. */
    midahs_release(&m);run(&m,300);assert(m.ports[1]==1);
    run(&m,300);assert(m.ports[1]==1);
    keys(&m,"0123D257A0123");assert(m.program[0123]==0257 && m.ports[2]==0257);
    keys(&m,"AA0020D123");assert(m.ports[6]==2 && m.storage[020]==0123);
    keys(&m,"AA0003");assert(m.ports[6]==1);m.ports[3]=0xa5;
    keys(&m,"0003");assert(m.ports[2]==0xa5);
    keys(&m,"+D252");assert(m.ports[4]==0252);
    keys(&m,"AA0000G");assert(!m.kex);
    for (unsigned value=0;value<256;value+=17) {
        m.ports[3]=(uint8_t)value;run(&m,50);assert(m.ports[4]==value);
    }
    m.program[100]=0x69;midahs_kex(&m);run(&m,300);
    assert(m.kex && m.program[100]==0x69 && m.ports[4]==255);
    keys(&m,"3000D");midahs_press(&m,code('1'));run(&m,100);midahs_release(&m);
    for (unsigned i=0;i<300 && !m.fault;i++) midahs_step(&m);
    assert(m.fault==FAULT_ROM);
    midahs_kex(&m);run(&m,300);assert(!m.fault && m.kex);

    /* Enter the entire SWITCHES program with the real monitor, then run it. */
    for (unsigned i=0;i<768;i++) m.program[i]=0;
    keys(&m,"0000D023+003+033+004+360+000A0000G");
    m.ports[3]=0x5a;run(&m,100);assert(!m.kex && m.ports[4]==0x5a);
    midahs_kex(&m);run(&m,300);
    m.program[256]=0x23;m.program[257]=0x69;m.program[258]=0x1b;
    m.program[259]=4;m.program[260]=0xf1;m.program[261]=0;
    keys(&m,"1000G");assert(!m.kex && m.pg==1 && m.ports[4]==0x69);
}

static void hardware_checks(void)
{
    struct midahs m;
    /* Each physical TT selector drives the corresponding BT1 condition. */
    for (unsigned bit=0;bit<4;bit++) {
        midahs_init(&m);m.kex=0;m.pg=0;m.n=0;m.r[0]=0;
        m.program[0]=(uint8_t)(0xc8|bit);m.program[1]=16;
        assert(midahs_step(&m)==2 && m.r[0]==2);
        m.tests=1u<<bit;m.r[0]=0;
        assert(midahs_step(&m)==2 && m.r[0]==16);
    }
    midahs_init(&m);m.kex=0;m.pg=0;m.n=0;m.r[0]=0;m.r[3]=0x69;
    m.program[0]=0x63;m.program[1]=64;m.program[64]=0x12;m.wp=1;
    assert(midahs_step(&m)==3 && m.program[64]==0x12 && m.write_blocked);
    m.wp=0;m.r[0]=0;
    assert(midahs_step(&m)==3 && m.program[64]==0x69);
    m.wp=1;m.r[0]=0;m.program[0]=0x73;
    assert(midahs_step(&m)==3 && m.storage[64]==0x69); /* WP does not protect SM. */

    /* HALT/SS grants one instruction, preserves that grant through MEMR, and
     * does not repeat while SS remains low. */
    midahs_init(&m);m.kex=0;m.pg=0;m.n=0;m.r[0]=0;m.halt=0;
    m.program[0]=0;m.program[1]=0x83;m.program[2]=0;
    assert(midahs_step(&m)==1 && m.waiting==WAIT_HALT && !m.r[0]);
    m.ss=0;assert(midahs_step(&m)==1 && m.r[0]==1);
    assert(midahs_step(&m)==1 && m.waiting==WAIT_HALT && m.r[0]==1);
    m.ss=1;midahs_inputs(&m);m.ss=0;m.memr=1;
    assert(midahs_step(&m)==1 && m.waiting==WAIT_MEMR && m.ss_grant);
    m.memr=0;assert(midahs_step(&m)==3 && m.r[0]==2 && m.r[3]==1);
    assert(midahs_step(&m)==1 && m.waiting==WAIT_HALT && m.r[0]==2);
    m.halt=1;assert(midahs_step(&m)==1 && m.r[0]==3);

    /* RESET keeps RAM, flags and pending IRQ; entry uses next PC register,
     * vector 002 on the current page, and a disabled interrupt latch. */
    midahs_init(&m);m.n=3;m.pg=2;m.r[0]=99;m.r[3]=0x69;m.link=1;m.z=1;
    m.inte=1;m.int_level=0;midahs_inputs(&m);assert(m.intr);
    m.reset_level=0;m.pending_scw=1;
    assert(midahs_step(&m)==1 && m.n==0 && m.pg==0 && m.r[0]==0);
    assert(m.r[3]==0x69 && m.link==1 && m.z==1 && m.intr && !m.pending_scw);
    m.reset_level=1;
    assert(midahs_step(&m)==1 && m.inta && m.n==1 && m.r[1]==2 && !m.inte && !m.intr);
    m.program[2]=0x0f;assert(midahs_step(&m)==2 && m.n==0 && m.r[0]==0);

    /* EIN becomes effective during its successor's fetch, after that boundary's
     * IRQ test: a held request must not skip the successor instruction. */
    midahs_init(&m);m.kex=0;m.pg=0;m.n=0;m.r[0]=0;m.int_level=0;
    m.program[0]=3;m.program[1]=0;m.program[2]=0x0f;
    assert(midahs_step(&m)==1 && !m.inte && !m.intr && m.r[0]==1);
    assert(midahs_step(&m)==1 && m.inte && m.intr && m.r[0]==2 && m.n==0);
    assert(midahs_step(&m)==1 && m.inta && m.n==1 && m.r[0]==2 && m.r[1]==2);

    /* SCW sends its control once then holds without fetching a successor. */
    midahs_init(&m);m.kex=0;m.pg=0;m.n=0;m.r[0]=0;m.scwr=1;
    m.program[0]=8;m.program[1]=0x81;m.program[2]=0x23;m.program[3]=0x69;
    assert(midahs_step(&m)==3 && m.pending_scw && m.kex && m.r[0]==2);
    m.kex=0;
    for (unsigned i=0;i<4;i++) assert(midahs_step(&m)==1 && !m.kex && m.r[0]==2);
    m.scwr=0;assert(midahs_step(&m)==1 && !m.pending_scw && m.r[0]==2);
    assert(midahs_step(&m)==2 && m.r[3]==0x69);
}

static void control_checks(void)
{
    struct panel p;panel_init(&p);
    for (unsigned bit=0;bit<4;bit++) {
        p.focus=CONTROL_TT0+bit;panel_actions(&p,KEY_A,0);
        assert(p.machine.tests&(1u<<bit));
    }
    p.focus=CONTROL_CLOCK;panel_actions(&p,KEY_A,0);assert(p.clock==CLOCK_MANUAL);
    unsigned cycles=p.machine.cycles;
    for (unsigned i=0;i<60;i++) panel_tick(&p,0);
    assert(p.machine.cycles==cycles && !p.clock_pulses);
    p.focus=CONTROL_CL;
    for (unsigned i=0;i<15;i++) panel_actions(&p,KEY_A,0);
    assert(p.machine.cycles==cycles && p.clock_pulses==15);
    panel_actions(&p,KEY_A,0);
    assert(p.machine.cycles==cycles+2 && p.clock_pulses==16); /* JMP3 completes. */
    p.focus=CONTROL_CLOCK;panel_actions(&p,KEY_A,0);assert(p.clock==CLOCK_LOW);
    for (unsigned i=0;i<60;i++) panel_tick(&p,0);
    assert(p.clock_pulses==24);
    panel_actions(&p,KEY_A,0);assert(p.clock==CLOCK_HIGH);
    for (unsigned i=0;i<5;i++) panel_tick(&p,0);
    assert(p.machine.kex && p.machine.ports[2]==023);
    panel_actions(&p,KEY_A,0);assert(p.clock==CLOCK_MANUAL);
    /* A quick keypad tap survives slow/manual clocking until ED5 is read. */
    p.focus=11;panel_actions(&p,KEY_A,0);
    for (unsigned i=0;i<5;i++) panel_tick(&p,0);
    assert(p.active_key==11 && p.machine.ports[5]!=255);
    panel_move(&p,KEY_LEFT);assert(p.focus!=11); /* Released A can navigate to CL. */
    p.focus=CONTROL_CL;
    for (unsigned i=0;i<2000 && !p.machine.ports[1];i++) panel_actions(&p,KEY_A,0);
    assert(p.machine.ports[1]==1 && p.active_key<0);

    /* Releasing a one-cycle halt wait mid-group cannot commit a three-cycle
     * instruction early. The remaining instruction cycles are reserved first. */
    struct panel delayed;panel_init(&delayed);
    delayed.machine.kex=0;delayed.machine.pg=0;delayed.machine.n=0;
    delayed.machine.r[0]=0;delayed.machine.program[0]=0x83;
    delayed.machine.halt=0;delayed.machine.ss=1;
    for (unsigned i=0;i<4;i++) panel_clock_pulse(&delayed);
    delayed.focus=CONTROL_SS;panel_actions(&delayed,KEY_A,0);
    for (unsigned i=0;i<19;i++) panel_clock_pulse(&delayed);
    assert(delayed.machine.r[3]==0 && delayed.clock_pulses==23);
    panel_clock_pulse(&delayed);
    assert(delayed.machine.r[3]==1 && delayed.machine.r[0]==1);

    p.focus=CONTROL_WP;panel_actions(&p,KEY_A,0);assert(p.machine.wp);
    p.focus=CONTROL_RESET;panel_actions(&p,KEY_A,0);assert(!p.machine.reset_level);
    p.focus=CONTROL_INT;panel_actions(&p,KEY_A,0);assert(!p.machine.int_level);
    p.focus=CONTROL_MEMR;panel_actions(&p,KEY_A,0);assert(p.machine.memr);
    p.focus=CONTROL_HALT;panel_actions(&p,KEY_A,0);assert(!p.machine.halt);
    p.focus=CONTROL_SS;panel_actions(&p,KEY_A,0);assert(!p.machine.ss);
    p.focus=CONTROL_SCWR;panel_actions(&p,KEY_A,0);assert(p.machine.scwr);
}

static void reference_checks(void)
{
    assert(REFERENCE_ROWS==43 && REFERENCE_PAGES==2);
    for (unsigned i=0;i<REFERENCE_ROWS;i++) {
        assert(strlen(reference_rows[i].bits)==8);
        assert(strlen(reference_rows[i].form)<=21);
        assert(strlen(reference_rows[i].meaning)<=20);
    }
    struct demo demo;demo_init(&demo);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    demo.panel.focus=7;
    unsigned pulses=demo.panel.clock_pulses, cycles=demo.panel.machine.cycles;
    demo_actions(&demo,KEY_R,0);
    assert(demo.panel.help && demo.panel.help_page==0);
    for (unsigned i=0;i<60;i++) demo_tick(&demo,KEY_RIGHT,0);
    assert(demo.panel.clock_pulses==pulses && demo.panel.machine.cycles==cycles);
    assert(demo.panel.focus==7);
    demo_actions(&demo,KEY_R,0);assert(demo.panel.help_page==1);
    demo_actions(&demo,KEY_LEFT,0);assert(demo.panel.help_page==0);
    demo_actions(&demo,KEY_B,0);
    assert(!demo.panel.help && demo.panel.machine.cycles==cycles);
    assert(!demo.panel.paused); /* Help did not change existing debugger pause. */
    demo_actions(&demo,KEY_START,0);assert(demo.panel.paused);
    demo.panel.machine.program[100]=0x69;
    demo_actions(&demo,KEY_L,0);demo_actions(&demo,KEY_SELECT,0);
    assert(!demo.panel.help && demo.panel.paused && demo.panel.machine.program[100]==0x69);

    uint16_t *allocation=malloc((480*272+2)*sizeof(uint16_t));assert(allocation);
    allocation[0]=0x1234;allocation[480*272+1]=0x5678;
    demo_actions(&demo,KEY_L,0);
    for (unsigned page=0;page<REFERENCE_PAGES;page++) {
        demo.panel.help_page=page;demo_render(&demo,0,allocation+1);
        assert(allocation[0]==0x1234 && allocation[480*272+1]==0x5678);
    }
    free(allocation);
}

static void panel_checks(void)
{
    struct demo demo;demo_init(&demo);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    assert(demo.panel.machine.ports[2]==023);
    /* Short raw press+release is stretched until the CPU actually sees it. */
    demo_actions(&demo,KEY_A,0);
    assert(demo.panel.active_key==8);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    assert(!demo.panel.machine.kex && demo.panel.active_key<0);
    demo.panel.focus=11;demo_actions(&demo,KEY_A,0);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    assert(demo.panel.active_key<0); /* A program not reading ED5 does not latch UI keys forever. */
    demo.panel.focus=8;
    /* Move left through KEX and the added board controls to the switches. */
    demo_actions(&demo,KEY_LEFT,KEY_LEFT);demo_actions(&demo,0,0);
    assert(demo.panel.focus==CONTROL_KEX);
    for (unsigned i=0;i<8 && demo.panel.focus>=8;i++) {
        demo_actions(&demo,KEY_LEFT,KEY_LEFT);demo_actions(&demo,0,0);
    }
    assert(demo.panel.focus<8);
    unsigned bit=demo.panel.focus;
    demo_actions(&demo,KEY_A,KEY_A);demo_actions(&demo,0,0);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    assert(demo.panel.machine.ports[3]==(1u<<bit));
    assert(demo.panel.machine.ports[4]==(1u<<bit));
    demo_actions(&demo,KEY_B,0);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    assert(demo.panel.machine.kex && demo.panel.machine.ports[3]==(1u<<bit));
    /* Every control is reachable using the actual navigation function. */
    unsigned seen[CONTROL_COUNT]={0};seen[8]=1;
    for (unsigned pass=0;pass<CONTROL_COUNT;pass++) for (unsigned i=0;i<CONTROL_COUNT;i++) if (seen[i]) {
        static const unsigned directions[]={KEY_UP,KEY_DOWN,KEY_LEFT,KEY_RIGHT};
        for (unsigned d=0;d<4;d++) {
            demo.panel.focus=i;panel_move(&demo.panel,directions[d]);seen[demo.panel.focus]=1;
        }
    }
    for (unsigned i=0;i<CONTROL_COUNT;i++) assert(seen[i]);
    /* Holding A locks the selected key and release produces exactly one '+'. */
    demo.panel.focus=11;demo_actions(&demo,KEY_A,KEY_A);
    demo_actions(&demo,KEY_LEFT,KEY_A|KEY_LEFT);assert(demo.panel.focus==11);
    for (unsigned i=0;i<10;i++) demo_tick(&demo,KEY_A,0);
    assert(demo.panel.machine.ports[1]==0);
    demo_actions(&demo,0,0);
    for (unsigned i=0;i<5;i++) demo_tick(&demo,0,0);
    assert(demo.panel.machine.ports[1]==1);
    /* Pause does not lose input/volume ownership and CPU stepping is not implicit. */
    demo_actions(&demo,KEY_START,0);unsigned cycles=demo.panel.machine.cycles;
    for (unsigned i=0;i<60;i++) demo_tick(&demo,0,0);
    assert(demo.panel.machine.cycles==cycles);
    demo_actions(&demo,KEY_B,0);assert(!demo.panel.paused);

    uint16_t *allocation=malloc((480*272+2)*sizeof(uint16_t));assert(allocation);
    allocation[0]=0x1234;allocation[480*272+1]=0x5678;
    for (unsigned i=0;i<CONTROL_COUNT;i++) {
        demo.panel.focus=i;demo_render(&demo,0,allocation+1);
        assert(allocation[0]==0x1234 && allocation[480*272+1]==0x5678);
    }
    free(allocation);
}
int main(void)
{
    monitor_checks();panel_checks();hardware_checks();control_checks();reference_checks();
    puts("Monitor, keypad entry, GO/KEX, switches, navigation, pulses and renderer passed");
    return 0;
}
