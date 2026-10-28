#include "demo.h"
#include "paths.h"
#include "sdk/syscalls.h"
static unsigned char photo[PANEL_BYTES];

int demo_load_photo(struct demo *demo)
{
    demo->panel.photo=0;
    int fd=sys_open(APP_RESOURCE_DIR "/panel.rgb565",X7_O_RDONLY,0);
    if (fd<0) return -1;
    unsigned total=0;
    int valid=1;
    while (total<PANEL_BYTES) {
        int count=sys_read(fd,photo+total,PANEL_BYTES-total);
        if (count<=0 || (unsigned)count>PANEL_BYTES-total) { valid=0;break; }
        total+=(unsigned)count;
    }
    unsigned char extra;
    if (valid && sys_read(fd,&extra,1)!=0) valid=0;
    if (sys_close(fd)<0) valid=0;
    if (!valid) return -1;
    demo->panel.photo=photo;
    return 0;
}
