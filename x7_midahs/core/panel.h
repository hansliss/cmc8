#ifndef X7_MIDAHS_PANEL_H
#define X7_MIDAHS_PANEL_H
#include "midahs.h"
#define PANEL_WIDTH 391
#define PANEL_HEIGHT 272
#define PANEL_BYTES (PANEL_WIDTH*PANEL_HEIGHT*2)
#define CONTROL_COUNT 34
#define CONTROL_TT0 21
#define CONTROL_CL 25
#define CONTROL_CLOCK 26
#define CONTROL_RESET 27
#define CONTROL_INT 28
#define CONTROL_MEMR 29
#define CONTROL_HALT 30
#define CONTROL_SS 31
#define CONTROL_SCWR 32
#define CONTROL_WP 33
enum panel_clock { CLOCK_HIGH, CLOCK_MANUAL, CLOCK_LOW };
#define CONTROL_KEX 20
struct panel_control { int x,y,w,h; const char *name; unsigned code; };
extern const struct panel_control panel_controls[CONTROL_COUNT];
struct panel {
    struct midahs machine;
    unsigned focus, paused, clock, clock_fraction, pulse_ticks, held, direction, repeat_ticks;
    unsigned remaining_slots, planned_cycles;
    unsigned help, help_page;
    uint32_t clock_pulses;
    int active_key;
    const unsigned char *photo;
};
void panel_init(struct panel *);
void panel_actions(struct panel *, unsigned pressed, unsigned held);
void panel_tick(struct panel *, unsigned held);
void panel_clock_pulse(struct panel *);
const char *panel_control_state(const struct panel *, unsigned index);
void panel_move(struct panel *, unsigned direction);
void panel_kex(struct panel *);
#endif
