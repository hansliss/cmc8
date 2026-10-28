/* Firmware shell: keep device ownership here, portable app behavior in demo.c. */
#include "sdk/platform/ui_abi.h"
#include "sdk/platform/fb_video.h"
#include "sdk/platform/timing.h"
#include "sdk/common/volume.h"
#include "demo.h"
#include "settings.h"
#include "controls.h"
#include "audio.h"
#include "paths.h"
int x7_forbid_key_mapping(int);
static struct demo scene;
struct app_settings app_settings; /* Audio is disabled; no app settings file is used. */
static struct fb_video video = {.fd = -1};
static struct x7_timing timing;
static void *gui, *applib;
static int window, initialized, mapping, registered, raw_mode;
static int key_fd = -1, log_fd = -1, timer = -1, calibration = -1, status;
static unsigned done, busy, rate = 100, epoch, frames, raw, stable, pressed;
static unsigned since[2], quit_since;

/* Fixed, bounded logging avoids printf/libc and handles short writes. */
static int record(const char *tag, x7_u64 value)
{
    char text[160];
    const char hex[] = "0123456789abcdef";
    unsigned n = 0, at = 0;
    while (*tag && n < 139) text[n++] = *tag++;
    text[n++] = ' '; text[n++] = '0'; text[n++] = 'x';
    for (unsigned i = 0; i < 16; i++) text[n++] = hex[(value >> ((15-i)*4)) & 15];
    text[n++] = '\n';
    if (log_fd < 0) return 1;
    while (at < n) {
        int count = sys_write(log_fd,text+at,n-at);
        if (count <= 0 || (unsigned)count > n-at) return 0;
        at += (unsigned)count;
    }
    return 1;
}
static int before(const char *tag) { return record(tag,0); }
static void finish(int result)
{
    status = result;
    done = 1;
    if (registered) ui_exit_loop();
}
static void fail(const char *tag)
{
    if (log_fd < 0) log_fd = sys_open(APP_ERROR_PATH,X7_O_WRONLY|X7_O_CREAT|X7_O_TRUNC,0600);
    record(tag,1);
    finish(1);
}

/* Raw type-zero events are complete masks, not independent press/release keys.
 * Preserve short press edges across a batch. Start/Select need 50 ms stable
 * qualification: the ADC scan occasionally reports transient false bits. */
static void input(void)
{
    unsigned events[10][3], now = OSTimeGet();
    int count = sys_read(key_fd,events,sizeof(events));
    if (count > 0) {
        if (count > (int)sizeof(events) || count % 12) { fail("Bad raw key record"); return; }
        for (unsigned i = 0; i < (unsigned)count / 12; i++) {
            if (events[i][0]) continue;
            unsigned next = x7_volume_keys(events[i][1],now,rate);
            for (unsigned j = 0; j < 2; j++) {
                unsigned bit = 4u << j;
                if ((next & bit) && !(raw & bit)) since[j] = now;
            }
            if ((next & KEY_HOME) && !(raw & KEY_HOME)) quit_since = now;
            pressed |= next & ~raw & ~12u;
            raw = next;
            stable = (next & ~12u) | (stable & next & 12u);
        }
    }
    x7_volume_poll(now,rate);
    for (unsigned j = 0; j < 2; j++) {
        unsigned bit = 4u << j;
        if ((raw & bit) && !(stable & bit) && now-since[j] >= (rate+19)/20) {
            stable |= bit;
            pressed |= bit;
        }
    }
    if ((raw & KEY_HOME) && now-quit_since >= (rate+1)/2) finish(0);
}
static void actions(void)
{
    demo_actions(&scene,pressed,stable);
    pressed = 0;
}
/* Inspector presentation must not starve behind simulation catch-up. The SDK
 * helper defers every draw while three ticks are owed; sustained CPU load can
 * keep that condition true forever. Retain its 30 Hz cadence, not its gate. */
static int presentation_due(void)
{
    if (timing.draw_phase < timing.rate) return 0;
    timing.draw_phase %= timing.rate;
    return 1;
}

static void frame(void *argument)
{
    unsigned slot, begin;
    int result;
    (void)argument;
    if (done || busy) return;
    busy = 1;
    input();
    if (done) { busy=0; return; }
    actions();
    begin = OSTimeGet();
    x7_timing_update(&timing,begin);
    for (unsigned n=0; n<3 && x7_timing_due(&timing); n++) {
        demo_tick(&scene,stable,&app_settings);
        x7_timing_step(&timing);
        if (x7_timing_work_done(begin,OSTimeGet())) break;
    }
    if (presentation_due()) {
        result = fb_video_acquire(&video,frames,&slot);
        if (result < 0) fail("Framebuffer acquire failed");
        else if (!result) {
            demo_render(&scene,&app_settings,fb_video_pixels(&video,slot));
            if (fb_video_submit(&video,slot) < 0) fail("Framebuffer submit failed");
            else frames++;
        }
    }
    if (!done) app_audio_pump(0);
    busy = 0;
}
static void calibrate(void *argument)
{
    (void)argument;
    rate = OSTimeGet()-epoch;
    ui_kill_timer(calibration); calibration=-1;
    if (!rate || rate > 10000) { fail("Clock calibration failed"); return; }
    record("OS ticks per second",rate);
    x7_timing_init(&timing,rate,OSTimeGet());
    timer = ui_set_timer(1,frame,0);
    if (timer < 0) fail("Frame timer failed");
}
static int window_message(struct ui_message *message)
{
    if (message->msgid == 13) return 0; /* Raw input owns key handling. */
    return ui_default_callback(message);
}
static void system_message(struct ui_app_message *message)
{
    if (message->type == 1001) finish(0);
}
void app_start_error(int stage, int result)
{
    log_fd = sys_open(APP_ERROR_PATH,X7_O_WRONLY|X7_O_CREAT|X7_O_TRUNC,0600);
    record("CRT stage",(unsigned)stage);
    record("CRT result",(x7_s64)result);
    if (log_fd >= 0) { sys_fsync(log_fd); sys_close(log_fd); log_fd=-1; }
}
void *process_start(void *argument)
{
    struct app_process_prefix *process;
    struct ui_app_message message;
    unsigned argc=0;
    (void)argument;
    x7_volume_init();
#if X7_DEBUG_LOG
    log_fd=sys_open(APP_LOG_PATH,X7_O_WRONLY|X7_O_CREAT|X7_O_TRUNC,0600);
#endif
    record("CMC8 MOP traffic v018",1);
    demo_init(&scene);
    process=app_get_process(app_getpid());
    if (!process) { fail("No process"); goto cleanup; }
    if (process->argv) while (argc<32 && process->argv[argc]) argc++;
    if (argc==32) { fail("Invalid launcher arguments"); goto cleanup; }
    /* Retain the filesystem module reference, matching the tested apps. */
    if (!x7_dlopen("libc_fs.so",2) && !x7_dlopen("libc_fs.so",2)) {
        fail("Filesystem unavailable"); goto cleanup;
    }
    /* This app uses the shared master volume but has no local settings. */
    applib=x7_dlopen("/mnt/diska/lib/applib.so",1);
    if (!applib) { fail("applib unavailable"); goto cleanup; }
    app_ui_init(argc,process->argv,0); initialized=1;
    mapping=1; x7_forbid_key_mapping(1);
    gui=x7_dlopen("gui.so",1);
    if (!gui) { fail("GUI unavailable"); goto cleanup; }
    window=ui_create_window(0,0,480,272,2,window_message,0);
    if (window<=0) { fail("Window failed"); goto cleanup; }
    ui_set_focus((unsigned)window);
    void *dc=ui_dc_get((unsigned)window);
    if (!dc) { fail("DC unavailable"); goto cleanup; }
    ui_background_color(dc,0); ui_clear_rect(dc,0,0,479,271); ui_screen_update();
    if (fb_video_open(&video,record,before)<0) { fail("Framebuffer failed"); goto cleanup; }
    key_fd=sys_open("/dev/key",X7_O_RDWR,0);
    if (key_fd<0) { fail("Keys unavailable"); goto cleanup; }
    raw_mode=1;
    if (sys_ioctl(key_fd,0x4003,1)<0) { fail("Raw key mode failed"); goto cleanup; }
    app_audio_open();
    ui_register_dispatcher(system_message); registered=1;
    epoch=OSTimeGet(); calibration=ui_set_timer(1000,calibrate,0);
    if (calibration<0) { fail("Calibration timer failed"); goto cleanup; }
    while (!done && ui_get_msg(&message)==1) ui_dispatch_msg(&message);
cleanup:
    /* Stop producers before releasing anything their callbacks could access. */
    if (timer>=0) ui_kill_timer(timer);
    if (calibration>=0) ui_kill_timer(calibration);
    if (registered) ui_unregister_dispatcher(system_message);
    app_audio_close();
    x7_volume_flush();
    if (key_fd>=0) {
        if (raw_mode) sys_ioctl(key_fd,0x4003,0);
        sys_close(key_fd);
    }
    if (mapping) x7_forbid_key_mapping(0);
    if (fb_video_close(&video,record,before)<0) status=1;
    if (window>0) ui_delete_window((unsigned)window);
    if (gui) x7_dlclose(gui);
    if (initialized) app_ui_quit();
    if (applib) x7_dlclose(applib);
    record("Frames",frames);
    record("Audio errors",app_audio_errors);
    record("Volume save errors",x7_volume_save_errors);
    record("Exit status",(unsigned)status);
    if (log_fd>=0) { sys_fsync(log_fd); sys_close(log_fd); }
    app_exit(status);
    return 0;
}
