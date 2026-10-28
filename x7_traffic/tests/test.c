#include "demo.h"
#include "controls.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

static void event(struct cpu *cpu)
{
    do { assert(cpu_step(cpu)); } while (cpu->s.phase || cpu->s.timing);
}

static void literal_cycle(unsigned sensor)
{
    /* Same initial polling and sensor schedule as the v018 board fixture.
     * Expected WRITE-falling subdivisions come from its independent JSON result. */
    static const unsigned slots[] = {53,261,1254541,3763053,7525797,10034309,11288589};
    static const int lamps[] = {044,046,041,0201,0301,041,044};
    struct cpu cpu; cpu_init(&cpu);
    while (cpu.writes < 1) assert(cpu_step(&cpu));
    assert(cpu.last_write_slot == slots[0] && cpu.lamps == lamps[0]);
    while (cpu.s.phase || cpu.s.timing || cpu.s.r[0] != 4) assert(cpu_step(&cpu));
    for (unsigned i=0; i<9; i++) event(&cpu);
    cpu.tests=(uint8_t)(1u<<sensor);
    while (cpu.s.phase || cpu.s.timing || cpu.s.r[0] != 012) assert(cpu_step(&cpu));
    cpu.tests=0;
    unsigned writes=cpu.writes;
    while (cpu.writes < 7) {
        assert(cpu.slots < 12000000 && cpu_step(&cpu));
        if (cpu.writes != writes) {
            writes=cpu.writes;
            assert(cpu.last_write_slot == slots[writes-1] + (sensor == 3 ? 16u : 0u));
            assert(cpu.lamps == lamps[writes-1]);
        }
    }
    while (cpu.s.phase || cpu.s.timing || cpu.s.r[0] != 4) assert(cpu_step(&cpu));
    for (unsigned i=0; i<9; i++) event(&cpu);
    assert(cpu.slots == 11288752 + (sensor == 3 ? 16u : 0u));
}

static void fault_checks(void)
{
    struct cpu cpu; cpu_init(&cpu);
    event(&cpu); /* Execute RESET before setting this test's fetch location. */
    cpu.s.r[0]=0103; /* The delay immediate 172o is not an opcode in this subset. */
    for (unsigned i=0; i<8 && !cpu.fault; i++) cpu_step(&cpu);
    assert(cpu.fault == 1);
    unsigned slots=cpu.slots;
    assert(!cpu_step(&cpu) && cpu.slots == slots);
}

static void display_checks(void)
{
    struct demo phase, instruction;
    demo_init(&phase);
    demo_init(&instruction);
    demo_actions(&instruction,KEY_X,0);
    assert(instruction.traffic.instruction_view);

    /* Display mode never changes CPU or world progress. */
    for (unsigned i=0; i<60; i++) {
        demo_tick(&phase,0,0);
        demo_tick(&instruction,0,0);
        assert(phase.traffic.cpu.slots == instruction.traffic.cpu.slots);
        assert(phase.traffic.cpu.s.r[0] == instruction.traffic.cpu.s.r[0]);
        assert(phase.traffic.cpu.lamps == instruction.traffic.cpu.lamps);
        assert(phase.traffic.traffic_ms == instruction.traffic.traffic_ms);
        assert(instruction.traffic.inspector.s.phase == 0);
        assert(instruction.traffic.inspector.s.timing == 0);
    }
    assert(instruction.traffic.cpu.slots == 125000);

    /* Phase refresh includes MOP31's F1T1 -> F2T2 jump, not only T7. */
    demo_init(&phase);
    unsigned snapshots=0;
    for (unsigned i=0; i<200; i++) {
        uint32_t before=phase.traffic.inspector.slots;
        scene_step_slot(&phase.traffic);
        const struct cpu *cpu=&phase.traffic.cpu;
        int boundary=cpu->s.phase != cpu->last_phase || cpu->s.timing == 0;
        assert((phase.traffic.inspector.slots != before) == boundary);
        if (cpu->last_phase == 1 && cpu->last_timing == 1 && cpu->s.phase == 2) {
            assert(phase.traffic.inspector.s.timing == 2);
            snapshots++;
        }
    }
    assert(snapshots);

    /* In instruction view the reset snapshot holds until the first LRM ends. */
    demo_init(&instruction);
    demo_actions(&instruction,KEY_X,0);
    for (unsigned i=0; i<8; i++) scene_step_slot(&instruction.traffic);
    for (unsigned i=0; i<23; i++) scene_step_slot(&instruction.traffic);
    assert(instruction.traffic.inspector.slots == 8);
    scene_step_slot(&instruction.traffic);
    assert(instruction.traffic.inspector.slots == 32);
    demo_actions(&instruction,KEY_A,0);
    assert(instruction.traffic.paused);
    assert(instruction.traffic.inspector.slots == 33);
    demo_actions(&instruction,KEY_X,0);
    assert(!instruction.traffic.instruction_view && instruction.traffic.cpu.slots == 33);
}

static void speed_checks(void)
{
    static const unsigned slots_per_second[SPEED_COUNT] = {62500,125000,500000,2000000};
    for (unsigned speed=0; speed<SPEED_COUNT; speed++) {
        struct demo demo; demo_init(&demo);
        while (demo.traffic.speed != speed) demo_actions(&demo,KEY_Y,0);
        assert(!demo.traffic.cpu.slots && !demo.traffic.instruction_view);
        for (unsigned i=0; i<60; i++) demo_tick(&demo,0,0);
        assert(demo.traffic.cpu.slots == slots_per_second[speed]);
        assert(demo.traffic.traffic_ms == 1000);
        demo_actions(&demo,KEY_START,0);
        unsigned before=demo.traffic.cpu.slots;
        demo_actions(&demo,KEY_Y,0);
        assert(demo.traffic.speed == (speed+1)%SPEED_COUNT);
        demo_tick(&demo,0,0);
        assert(demo.traffic.cpu.slots == before); /* Speed control works while paused. */
        demo_actions(&demo,KEY_A,0);
        assert(demo.traffic.cpu.slots == before+1); /* Manual step is always one T slot. */
        demo_actions(&demo,KEY_SELECT,0);
        assert(demo.traffic.speed == SPEED_NORMAL);
    }

    /* Mixed rates retain fractional slots instead of rounding every host tick. */
    struct demo mixed; demo_init(&mixed);
    demo_tick(&mixed,0,0);                       /* 1x: 2083 + 1/3 slots */
    demo_actions(&mixed,KEY_Y,0);demo_tick(&mixed,0,0); /* 4x */
    demo_actions(&mixed,KEY_Y,0);demo_tick(&mixed,0,0); /* 16x */
    demo_actions(&mixed,KEY_Y,0);demo_tick(&mixed,0,0); /* 0.5x */
    assert(mixed.traffic.cpu.slots == 44791);
    assert(mixed.traffic.slot_fraction == 80);

    /* At equal CPU time the processor agrees, but traffic clocks intentionally
     * differ: Y accelerates only the processor. */
    struct demo normal, fast; demo_init(&normal);demo_init(&fast);
    demo_actions(&fast,KEY_Y,0);
    for (unsigned i=0; i<60; i++) demo_tick(&normal,0,0);
    for (unsigned i=0; i<15; i++) demo_tick(&fast,0,0);
    assert(normal.traffic.cpu.slots == fast.traffic.cpu.slots);
    for (unsigned i=0; i<8; i++) assert(normal.traffic.cpu.s.r[i] == fast.traffic.cpu.s.r[i]);
    assert(normal.traffic.cpu.s.phase == fast.traffic.cpu.s.phase);
    assert(normal.traffic.cpu.s.timing == fast.traffic.cpu.s.timing);
    assert(normal.traffic.cpu.lamps == fast.traffic.cpu.lamps);
    assert(normal.traffic.traffic_ms == 1000);
    assert(fast.traffic.traffic_ms == 250);

    /* Same host time, same unobstructed traffic speed and arrival schedule,
     * regardless of requested CPU rate. */
    int32_t car_position=0;
    for (unsigned speed=0; speed<SPEED_COUNT; speed++) {
        struct demo demo; demo_init(&demo);
        while (demo.traffic.speed != speed) demo_actions(&demo,KEY_Y,0);
        demo.traffic.cars[0]=(struct car){.lane=0,.speed=20,.active=1};
        for (unsigned i=0; i<60; i++) demo_tick(&demo,0,0);
        assert(demo.traffic.traffic_ms == 1000);
        assert(demo.traffic.arrivals[2] == 11000);
        assert(demo.traffic.arrivals[3] == 25000);
        assert(demo.traffic.cars[1].active); /* First main-road arrival, at 1s. */
        assert(demo.traffic.cars[1].speed >= 14 && demo.traffic.cars[1].speed <= 26);
        if (speed==0) car_position=demo.traffic.cars[0].position;
        assert(demo.traffic.cars[0].position == car_position);
        assert(car_position >= 19*256 && car_position <= 20*256);
    }
}

static void scene_checks(void)
{
    struct demo demo; demo_init(&demo);
    struct scene *scene=&demo.traffic;
    /* Pause and slot/instruction stepping do not advance a hidden instruction CPU. */
    demo_actions(&demo,KEY_START,0);
    demo_tick(&demo,0,0);
    assert(scene->paused && !scene->cpu.slots);
    demo_actions(&demo,KEY_A,0);
    assert(scene->cpu.slots == 1 && scene->cpu.last_timing == 0);
    demo_actions(&demo,KEY_B,0);
    assert(scene->cpu.slots == 8 && scene->cpu.s.timing == 0);
    demo_actions(&demo,KEY_START,0);
    for (unsigned i=0; i<60; i++) demo_tick(&demo,0,0);
    assert(scene->cpu.slots == 125008);
    assert(scene->traffic_ms == 1000);
    /* Vehicle detection is supplied to the same actual T input as manual input. */
    scene->cars[0]=(struct car){.position=60*256,.lane=2,.speed=7,.active=1};
    scene_input(scene,KEY_DOWN);
    assert(scene->cpu.tests == (2|8));
    /* At red, the front bumper cannot advance beyond the stop line. */
    scene->cpu.lamps=044;
    scene->cars[0].position=70*256;
    demo_actions(&demo,KEY_START,0);
    unsigned traffic_before=scene->traffic_ms;
    for (unsigned i=0;i<60;i++) demo_tick(&demo,0,0);
    assert(scene->traffic_ms == traffic_before); /* Pause freezes cars and arrivals. */
    demo_actions(&demo,KEY_A,0);
    assert(scene->traffic_ms == traffic_before); /* CPU stepping leaves traffic still. */
    demo_actions(&demo,KEY_START,0);
    for (unsigned i=0;i<6;i++) demo_tick(&demo,0,0);
    assert(scene->traffic_ms == traffic_before+100);
    assert(scene->cars[0].position==70*256);
    demo_actions(&demo,KEY_SELECT,0);
    assert(!scene->cpu.slots && !scene->instruction_view && scene->random==1977);

    /* Draw the real renderer across edge positions with framebuffer canaries. */
    uint16_t *allocation=malloc((480*272+2)*sizeof(uint16_t));
    assert(allocation);
    allocation[0]=0x1234;allocation[480*272+1]=0x5678;
    scene->cars[0]=(struct car){.position=-12*256,.lane=0,.speed=7,.active=1};
    for (unsigned i=0;i<400;i++) {
        demo_tick(&demo,0,0);
        demo_render(&demo,0,allocation+1);
        assert(allocation[0]==0x1234 && allocation[480*272+1]==0x5678);
    }
    free(allocation);
}

int main(void)
{
    literal_cycle(1);
    literal_cycle(3);
    scene_checks();
    fault_checks();
    display_checks();
    speed_checks();
    puts("Literal v018 cycle, sensors, stepping, clock, vehicles and renderer passed");
    return 0;
}
