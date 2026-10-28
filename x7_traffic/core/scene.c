#include "scene.h"
#include "controls.h"

static uint32_t random_value(struct scene *scene)
{
    uint32_t x = scene->random;
    x ^= x<<13; x ^= x>>17; x ^= x<<5;
    return scene->random = x;
}

void scene_init(struct scene *scene)
{
    *scene = (struct scene){.random=1977,.speed=SPEED_NORMAL};
    cpu_init(&scene->cpu);
    scene->inspector = scene->cpu;
    scene->arrivals[0] = 1000;
    scene->arrivals[1] = 2000;
    /* Two illustrative first arrivals share the first service. After that,
     * each side approach averages FIVE MINUTES between cars. */
    scene->arrivals[2] = 12*1000;
    scene->arrivals[3] = 26*1000;
}

const char *scene_speed_name(const struct scene *scene)
{
    static const char *const names[SPEED_COUNT] = {"0.5X", "1X", "4X", "16X"};
    return names[scene->speed];
}

static void vehicles(struct scene *scene)
{
    /* Fixed 10 ms traffic update, independent of the CPU multiplier. */
    for (unsigned lane=0; lane<4; lane++) {
        if (scene->arrivals[lane] <= 10) {
            int clear = 1;
            for (unsigned i=0; i<CAR_COUNT; i++)
                if (scene->cars[i].active && scene->cars[i].lane == lane &&
                    scene->cars[i].position < 12*256) clear = 0;
            if (clear) for (unsigned i=0; i<CAR_COUNT; i++) if (!scene->cars[i].active) {
                scene->cars[i] = (struct car){.position=-12*256,
                    .speed=14+2*(random_value(scene)%7),.lane=(uint8_t)lane,
                    .color=(uint8_t)(random_value(scene)%4),.active=1};
                break;
            }
            unsigned seconds = lane < 2 ? 3+random_value(scene)%10 : 240+random_value(scene)%121;
            scene->arrivals[lane] = seconds*1000;
        } else scene->arrivals[lane] -= 10;
    }
    /* Positions advance at most 0.26px per update. All cars in front are old
     * positions, so queue spacing is independent of array/allocation order. */
    int32_t positions[CAR_COUNT];
    for (unsigned i=0; i<CAR_COUNT; i++) positions[i] = scene->cars[i].position;
    for (unsigned i=0; i<CAR_COUNT; i++) {
        struct car *car = &scene->cars[i];
        if (!car->active) continue;
        int32_t limit = 10000*256;
        for (unsigned j=0; j<CAR_COUNT; j++) {
            if (scene->cars[j].active && scene->cars[j].lane == car->lane &&
                positions[j] > positions[i] && positions[j]-20*256 < limit)
                limit = positions[j]-20*256;
        }
        int side = car->lane >= 2, stop = side ? 70 : 94;
        int green = scene->cpu.lamps >= 0 && (scene->cpu.lamps & (side ? 128 : 4));
        int yellow = scene->cpu.lamps >= 0 && (scene->cpu.lamps & (side ? 64 : 2));
        if ((!green || yellow) && car->position <= stop*256 && limit > stop*256) limit = stop*256;
        int32_t next = positions[i] + (int32_t)(car->speed*256/100);
        if (next > limit) next = limit;
        if (next > car->position) car->position = next;
        if (car->position > (side ? 226 : 268)*256) car->active = 0;
    }
}

static void sensors(struct scene *scene)
{
    unsigned tests = 0;
    for (unsigned i=0; i<CAR_COUNT; i++) {
        const struct car *car = &scene->cars[i];
        if (car->active && car->lane >= 2 && car->position > 45*256 && car->position <= 70*256)
            tests |= 1u << (car->lane == 2 ? 1 : 3);
    }
    if (scene->held & KEY_UP) tests |= 2;
    if (scene->held & KEY_DOWN) tests |= 8;
    scene->cpu.tests = (uint8_t)tests;
}

void scene_step_slot(struct scene *scene)
{
    if (!cpu_step(&scene->cpu)) {
        scene->inspector = scene->cpu;
        return;
    }
    int instruction_boundary = scene->cpu.s.phase == 0 && scene->cpu.s.timing == 0;
    int phase_boundary = scene->cpu.s.phase != scene->cpu.last_phase || scene->cpu.s.timing == 0;
    if (instruction_boundary || (!scene->instruction_view && phase_boundary))
        scene->inspector = scene->cpu;
}

void scene_step_instruction(struct scene *scene)
{
    /* If paused halfway through an instruction, finish that instruction. */
    for (unsigned i=0; i<32; i++) {
        scene_step_slot(scene);
        if (scene->cpu.fault || (scene->cpu.s.phase == 0 && scene->cpu.s.timing == 0)) break;
    }
}

void scene_actions(struct scene *scene, unsigned pressed)
{
    if (pressed & KEY_SELECT) { scene_init(scene); return; }
    if (pressed & KEY_START) scene->paused ^= 1;
    if (pressed & KEY_X) {
        scene->instruction_view ^= 1;
        scene->inspector = scene->cpu;
    }
    if (pressed & KEY_Y) scene->speed = (scene->speed+1)%SPEED_COUNT;
    if (pressed & KEY_A) {
        scene->paused=1;
        scene_step_slot(scene);
        scene->inspector = scene->cpu; /* Manual slot stepping always shows that slot. */
    }
    if (pressed & KEY_B) { scene->paused=1; scene_step_instruction(scene); }
}

void scene_input(struct scene *scene, unsigned held)
{
    scene->held = held;
    sensors(scene);
}

void scene_tick(struct scene *scene, unsigned held)
{
    scene_input(scene,held);
    if (scene->paused || scene->cpu.fault) return;
    /* Rates are in HALF-speed units, so the same denominator represents every
     * setting exactly, including changes between rates with a pending fraction.
     * No CPU slots or delay instructions are skipped. */
    static const unsigned half_units[SPEED_COUNT] = {1,2,8,32};
    scene->slot_fraction += 125000*half_units[scene->speed];
    unsigned slots = scene->slot_fraction/120;
    scene->slot_fraction %= 120;
    for (unsigned i=0; i<slots && !scene->cpu.fault; i++) {
        scene_step_slot(scene);
    }
    if (scene->cpu.fault) return;

    /* Traffic has its own fixed-rate clock. Y affects only CPU execution.
     * 60 host ticks produce 100 ten-millisecond vehicle/arrival updates. */
    scene->traffic_fraction += 100;
    unsigned updates = scene->traffic_fraction/60;
    scene->traffic_fraction %= 60;
    for (unsigned i=0; i<updates; i++) {
        scene->traffic_ms += 10;
        vehicles(scene);
        sensors(scene);
    }
}
