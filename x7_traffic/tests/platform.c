/* Adapted SDK firmware boundary fixture. Compile this app's actual shell,
 * framebuffer and disabled-audio path against firmware mocks.
 * One scenario per process keeps static app lifetime identical to the console. */
#include "sdk/platform/ui_abi.h"
#include "sdk/common/volume.h"
#include "audio.h"
#include "settings.h"
#include "controls.h"
#include "paths.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned scenario, now, iteration, raw_last, queued, submissions, audible, presentations;
static unsigned mapping, raw_mode, started, initialized, exited, freed, renamed;
static int result, window, registered, loop_exit;
static void *pool;
static void (*cal_cb)(void *), (*frame_cb)(void *);
static void (*dispatcher)(struct ui_app_message *);
static char *argv[]={"cmc8-traffic",0};
static struct app_process_prefix process={.argv=argv};
static unsigned keys(void)
{
    if (iteration==5) return KEY_B;
    if (iteration==12 || iteration==14 || iteration==16 || iteration==18) return KEY_Y;
    if (iteration==10 || (iteration>=20 && iteration<30) || (iteration>=40 && iteration<50)) return KEY_START;
    if (iteration>=60 && iteration<70) return 2;
    if (iteration>=80 && iteration<120) return KEY_A;
    if (iteration>=121) return KEY_HOME;
    return 0;
}
x7_u32 OSTimeGet(void)
{
    /* Sustained work cost keeps simulation debt above the old draw-skip gate. */
    if (scenario==7) now+=5;
    return now;
}
void OSTimeDly(x7_u16 ticks) { now+=ticks; }
int app_getpid(void) { return 1; }
struct app_process_prefix *app_get_process(int pid) { assert(pid==1); return &process; }
void app_exit(int status) { assert(!registered && !raw_mode && !mapping); exited++; result=status; }
void app_ui_init(int argc,char **v,void *p) { assert(argc==1 && v==argv && !p); initialized=1; }
void app_ui_quit(void) { assert(initialized && !window); initialized=0; }
void *x7_dlopen(const char *path,int flags)
{
    (void)flags;
    if ((scenario==1 && !strcmp(path,"gui.so")) || (scenario==4 && !strcmp(path,"libsound.so"))) return 0;
    return (void *)1;
}
int x7_dlclose(void *p) { assert(p); return 0; }
int x7_forbid_key_mapping(int value) { mapping=(unsigned)value; return 0; }
int sys_open(const char *path,int flags,x7_u32 mode)
{
    (void)mode;
    assert(strcmp(path,APP_SETTINGS_PATH)); /* No stray example config I/O. */
    if (!strcmp(path,"/dev/fb")) return 10;
    if (!strcmp(path,"/dev/key")) return 11;
    if (!flags) return -2; /* Missing config: defaults. */
    return 12;
}
x7_ssize_t sys_write(int fd,const void *p,x7_size_t size) { (void)p; assert(fd==12); return size; }
x7_ssize_t sys_read(int fd,void *p,x7_size_t size)
{
    assert(fd==11 && size==120);
    if (scenario==5) return 13;
    unsigned mask=keys();
    if (mask==raw_last) return -1; /* Empty nonblocking queue. */
    unsigned *event=p; event[0]=0; event[1]=mask; event[2]=0; raw_last=mask;
    return 12;
}
int sys_close(int fd) { assert(fd>=10); return 0; }
int sys_fsync(int fd) { assert(fd==12); return 0; }
int sys_mkdir(const char *path,x7_u32 mode) { (void)path; (void)mode; return 0; }
int sys_rename(const char *from,const char *to) { (void)from; assert(!strcmp(to,"/mnt/card/res/clauncher/volume.cfg")); renamed++; return 0; }
void *x7_syscall_114(x7_size_t size,x7_u32 flags)
{
    assert(size==5*262144 && flags==10);
    if (scenario==2) return 0;
    pool=malloc(size); assert(pool); return pool;
}
int x7_syscall_115(void *p) { assert(p==pool && !started); free(p); pool=0; freed++; return 0; }
x7_word_t x7_syscall_116(const void *p) { return (x7_word_t)p; }
int sys_ioctl(int fd,x7_u32 command,x7_word_t arg)
{
    if (fd==11) {
        assert(command==0x4003);
        raw_mode=(unsigned)arg;
        return scenario==3 && arg ? -5 : 0;
    }
    assert(fd==10);
    if (command==0x4662) { unsigned *p=(void *)arg; p[0]=480; p[1]=272; }
    if (command==0x4660) started=1;
    if (command==0x4661) {
        if (scenario==6) return -5;
        started=0;
    }
    if (command==0x5011) memset((void *)arg,0,3*sizeof(x7_word_t));
    if (command==0x4667) { assert(started && pool); presentations++; }
    return 0;
}
int ui_create_window(int x,int y,int w,int h,unsigned mode,int (*cb)(struct ui_message *),unsigned extra)
{ assert(!x&&!y&&w==480&&h==272&&mode==2&&cb&&!extra); return window=1; }
void ui_set_focus(unsigned w) { assert(w==1); }
void ui_delete_window(unsigned w) { assert(w==1); window=0; }
void *ui_dc_get(unsigned w) { assert(w==1); return (void *)1; }
int ui_default_callback(struct ui_message *m) { (void)m; return 0; }
void ui_background_color(void *dc,unsigned c) { assert(dc&&!c); }
void ui_clear_rect(void *dc,int x,int y,int r,int b) { assert(dc&&!x&&!y&&r==479&&b==271); }
void ui_screen_update(void) {}
void ui_register_dispatcher(void (*cb)(struct ui_app_message *)) { dispatcher=cb; registered=1; }
void ui_unregister_dispatcher(void (*cb)(struct ui_app_message *)) { assert(cb==dispatcher); registered=0; }
void ui_exit_loop(void) { loop_exit=1; }
int ui_set_timer(unsigned ms,void (*cb)(void *),void *arg)
{
    assert(!arg);
    if (ms==1000) { cal_cb=cb; return 1; }
    assert(ms==1); frame_cb=cb; return 2;
}
void ui_kill_timer(int timer) { if (timer==1) cal_cb=0; else { assert(timer==2); frame_cb=0; } }
int ui_get_msg(struct ui_app_message *m) { (void)m; assert(iteration<250); return !loop_exit; }
void ui_dispatch_msg(struct ui_app_message *m)
{
    (void)m;
    if (cal_cb) { now+=100; cal_cb(0); }
    else { now++; iteration++; if (queued>=441) queued-=441; else queued=0; assert(frame_cb); frame_cb(0); }
}
struct pcm { void *planes[6]; int channels,frames,precision; };
void *audio_open(void) { return (void *)2; }
int audio_command(void *p,x7_u32 command,x7_word_t arg)
{
    assert(p==(void *)2);
    if (command==0x4d414f45u) *(int *)arg=(int)queued;
    return 0;
}
int audio_submit(void *p,struct pcm *pcm)
{
    assert(p==(void *)2 && pcm->channels==2 && pcm->frames==1024 && !pcm->precision);
    assert(pcm->planes[0]==pcm->planes[1]);
    int *samples=pcm->planes[0];
    for (unsigned i=0;i<1024;i++) {
        assert(samples[i]>=-8192 && samples[i]<=8192);
        if (samples[i]) audible++;
        samples[i]=0x7fffffff; /* Firmware destructively converts submitted PCM. */
    }
    queued+=1024; submissions++; return 0;
}
void audio_close(void *p) { assert(p==(void *)2); }
int main(int argc,char **v)
{
    scenario=argc>1 ? (unsigned)atoi(v[1]) : 0;
    process_start(0);
    assert(exited==1 && !cal_cb && !frame_cb && !initialized);
    assert(result==((scenario==1||scenario==2||scenario==3||scenario==5||scenario==6)?1:0));
    if (!scenario || scenario==4 || scenario==6) {
        assert(iteration>=171 && renamed>=1 && x7_volume_percent<100);
        assert(!submissions && !audible); /* This app never starts sound. */
    }
    if (scenario==7) assert(iteration>121 && presentations>10);
    if (scenario==6) { assert(pool && !freed); free(pool); }
    else assert(!pool);
    printf("platform scenario %u passed\n",scenario);
}
