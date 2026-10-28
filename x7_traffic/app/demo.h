#ifndef X7_TRAFFIC_DEMO_H
#define X7_TRAFFIC_DEMO_H
#include <stdint.h>
#include "settings.h"
#include "scene.h"
struct demo { struct scene traffic; };
void demo_init(struct demo *);
void demo_actions(struct demo *, unsigned pressed, unsigned held);
void demo_tick(struct demo *, unsigned keys, const struct app_settings *);
void demo_render(const struct demo *, const struct app_settings *, uint16_t *);
#endif
