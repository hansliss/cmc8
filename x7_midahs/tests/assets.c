#include "demo.h"
#include "paths.h"
#include "sdk/syscalls.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
static unsigned scenario,position,closed;
int sys_open(const char *path,int flags,x7_u32 mode)
{
    assert(!strcmp(path,APP_RESOURCE_DIR "/panel.rgb565") && flags==X7_O_RDONLY && !mode);
    return scenario==1 ? -2 : 14;
}
x7_ssize_t sys_read(int fd,void *buffer,x7_size_t size)
{
    assert(fd==14);
    if (scenario==4) return -5;
    if (scenario==5) return size+1;
    unsigned length=PANEL_BYTES;
    if (scenario==2) length--;
    if (scenario==3) length++;
    unsigned count=position<length ? length-position : 0;
    if (count>size)count=size;
    if (count>397)count=397; /* Successful load must handle many short reads. */
    for (unsigned i=0;i<count;i++) ((unsigned char *)buffer)[i]=(unsigned char)(position+i);
    position+=count;
    return count;
}
int sys_close(int fd) {assert(fd==14);closed++;return scenario==6?-5:0;}
int main(void)
{
    for (scenario=0;scenario<7;scenario++) {
        struct demo demo;demo_init(&demo);position=closed=0;
        int result=demo_load_photo(&demo);
        assert(closed==(scenario==1?0u:1u));
        if (scenario) {assert(result<0 && !demo.panel.photo);continue;}
        assert(!result && demo.panel.photo && position==PANEL_BYTES);
        uint16_t *p=malloc(480*272*sizeof(*p));assert(p);
        demo_render(&demo,0,p);assert(p[0]==0x0100);free(p);
    }
    puts("Photo short reads, RGB565 decode, missing/truncated/oversize/read/close failures passed");
    return 0;
}
