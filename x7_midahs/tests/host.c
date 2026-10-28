/* Native-only screenshot helper; no stdio is linked into the console app. */
#include "demo.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc,char **argv)
{
    if (argc>1 && !strcmp(argv[1],"--opcodes")) {
        for (unsigned opcode=0;opcode<256;opcode++) {
            struct midahs m;midahs_init(&m);
            m.kex=0;m.pg=0;m.n=0;m.r[0]=0;m.r[3]=0x69;m.r[7]=64;
            m.program[0]=(uint8_t)opcode;m.program[1]=4;
            unsigned cycles=(unsigned)midahs_step(&m);
            printf("%u %u %u\n",opcode,cycles,m.fault);
        }
        return 0;
    }
    if (argc>1 && !strcmp(argv[1],"--oracle")) {
        /* Test-only wire protocol: memory, ports, registers and six control bytes. */
        unsigned char input[1024+1024+7+8+6];
        while (fread(input,1,sizeof(input),stdin)==sizeof(input)) {
            struct midahs m;midahs_init(&m);
            memcpy(m.program,input,1024);memcpy(m.storage,input+1024,1024);
            memcpy(m.ports,input+2048,7);memcpy(m.r,input+2055,8);
            const unsigned char *s=input+2063;
            m.n=s[0];m.pg=s[1];m.z=s[2];m.link=s[3];m.tests=s[4];m.kex=s[5];
            unsigned before=m.cycles;midahs_step(&m);
            for (unsigned i=0;i<8;i++) printf("%u ",m.r[i]);
            printf("%u %u %u %u %u %u\n",m.pg,m.n,m.z,m.link,m.cycles-before,m.fault);
        }
        return 0;
    }
    struct demo demo;demo_init(&demo);
    static unsigned char photo[PANEL_BYTES];
    const char *photo_path=argc>2?argv[2]:"x7_midahs/resources/panel.rgb565";
    FILE *file=fopen(photo_path,"rb");
    if (file) {if (fread(photo,1,sizeof(photo),file)==sizeof(photo)) demo.panel.photo=photo;fclose(file);}
    for (unsigned i=0;i<20;i++) demo_tick(&demo,0,0);
    if (argc>3) demo.panel.focus=(unsigned)atoi(argv[3])%CONTROL_COUNT;
    if (argc>4) { demo.panel.help=1;demo.panel.help_page=(unsigned)atoi(argv[4])%2; }
    static uint16_t pixels[480*272];demo_render(&demo,0,pixels);
    file=fopen(argc>1?argv[1]:"midahs.ppm","wb");if (!file)return 1;
    fputs("P6\n480 272\n255\n",file);
    for (unsigned i=0;i<480*272;i++) {
        unsigned p=pixels[i];unsigned char rgb[3]={((p>>11)&31)*255/31,((p>>5)&63)*255/63,(p&31)*255/31};
        if (fwrite(rgb,1,3,file)!=3)return 1;
    }
    return fclose(file)!=0;
}
