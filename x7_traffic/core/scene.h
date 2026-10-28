#ifndef TRAFFIC_SCENE_H
#define TRAFFIC_SCENE_H
#include "cpu.h"
#define CAR_COUNT 32
enum scene_speed { SPEED_HALF, SPEED_NORMAL, SPEED_FOUR, SPEED_SIXTEEN, SPEED_COUNT };
/* Q8 pixel coordinates, 480x272 presentation. Scene occupies x=0..255. */
struct car { int32_t position; unsigned speed; uint8_t lane, color, active; };
struct scene {
    struct cpu cpu;
    struct cpu inspector; /* Captured only at the selected display boundary. */
    struct car cars[CAR_COUNT];
    uint32_t random, arrivals[4], traffic_ms; /* Arrivals and traffic time are milliseconds. */
    unsigned paused, instruction_view, speed, slot_fraction, traffic_fraction, held;
};
void scene_init(struct scene *);
const char *scene_speed_name(const struct scene *);
void scene_actions(struct scene *, unsigned pressed);
void scene_input(struct scene *, unsigned held);
void scene_tick(struct scene *, unsigned held);
void scene_step_slot(struct scene *);
void scene_step_instruction(struct scene *);
#endif
