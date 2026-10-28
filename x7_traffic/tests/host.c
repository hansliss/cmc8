/* Host-only trace and screenshot utility; no stdio is linked into the console. */
#include "demo.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int trace(unsigned count)
{
    struct cpu cpu; cpu_init(&cpu);
    for (unsigned i=0;i<count;i++) {
        if (i==200) cpu.tests=2;
        if (i==500) cpu.tests=0;
        if (!cpu_step(&cpu)) return 1;
        printf("%u %llu %d %d %d %d %d %d %d %d %d %d %d %d",
               i,(unsigned long long)cpu.mops,cpu.last_phase,cpu.last_timing,
               cpu.s.ir,cpu.s.br,cpu.s.ab,cpu.s.pg,cpu.s.n,cpu.s.z,cpu.s.h,cpu.s.t,
               cpu.s.phase,cpu.s.timing);
        for (unsigned j=0;j<8;j++) printf(" %d",cpu.s.r[j]);
        printf(" %d %d %d %d %d %d %d %d %d %d %d\n",
               cpu.start.selected,cpu.start.di,cpu.start.db,cpu.start.alu,cpu.start.mux,
               cpu.end.selected,cpu.end.di,cpu.end.db,cpu.end.alu,cpu.end.mux,cpu.lamps);
    }
    return 0;
}
int main(int argc,char **argv)
{
    if (argc>1 && !strcmp(argv[1],"--trace")) return trace(argc>2 ? (unsigned)atoi(argv[2]) : 4000);
    struct demo demo; demo_init(&demo);
    unsigned ticks=argc>2 ? (unsigned)atoi(argv[2]) : 1800;
    for (unsigned i=0;i<ticks;i++) demo_tick(&demo,0,0);
    static uint16_t pixels[480*272];
    demo_render(&demo,0,pixels);
    const char *path=argc>1 ? argv[1] : "traffic.ppm";
    FILE *file=fopen(path,"wb");
    if (!file) return 1;
    fputs("P6\n480 272\n255\n",file);
    for (unsigned i=0;i<480*272;i++) {
        unsigned pixel=pixels[i];
        unsigned char rgb[3]={(unsigned char)(((pixel>>11)&31)*255/31),
                              (unsigned char)(((pixel>>5)&63)*255/63),
                              (unsigned char)((pixel&31)*255/31)};
        if (fwrite(rgb,1,3,file)!=3) return 1;
    }
    return fclose(file)!=0;
}
