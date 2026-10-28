#ifndef X7_MIDAHS_DEMO_H
#define X7_MIDAHS_DEMO_H
#include <stdint.h>
#include "settings.h"
#include "panel.h"
struct demo { struct panel panel; };
void demo_init(struct demo *);
void demo_actions(struct demo *, unsigned pressed, unsigned held);
void demo_tick(struct demo *, unsigned held, const struct app_settings *);
void demo_render(const struct demo *, const struct app_settings *, uint16_t *);
int demo_load_photo(struct demo *); /* Optional asset failure leaves a labeled fallback. */
#endif
