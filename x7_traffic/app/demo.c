/* Portable fixed-point scene and RGB565 diagnostics; no firmware calls. */
#include "demo.h"
#include "controls.h"
#include "sdk/platform/font.h"
#define WIDTH 480
#define HEIGHT 272
#define BG 0x1082
#define INK 0xef7d
#define DIM 0x7bef
#define CYAN 0x5dff
#define ROAD 0x3187

void demo_init(struct demo *demo) { scene_init(&demo->traffic); }
void demo_actions(struct demo *demo, unsigned pressed, unsigned held)
{
    scene_input(&demo->traffic,held);
    scene_actions(&demo->traffic,pressed);
}
void demo_tick(struct demo *demo, unsigned keys, const struct app_settings *settings)
{
    (void)settings;
    scene_tick(&demo->traffic,keys);
}

static void rectangle(uint16_t *pixels, int x, int y, int w, int h, uint16_t color)
{
    for (int row=y; row<y+h; row++) if (row>=0 && row<HEIGHT)
        for (int col=x; col<x+w; col++) if (col>=0 && col<WIDTH) pixels[row*WIDTH+col]=color;
}

static void text(uint16_t *pixels, int x, int y, const char *value, uint16_t color)
{
    for (; *value && x+5<WIDTH; value++,x+=6) {
        unsigned c=(unsigned char)*value;
        if (c>='a' && c<='z') c-=32;
        if (c>='0' && c<='9') c-='0';
        else if (c>='A' && c<='Z') c=c-'A'+10;
        else if (c=='-') c=36;
        else if (c=='.') c=37;
        else if (c=='!') c=38;
        else if (c=='?') c=39;
        else if (c==':') c=41;
        else continue;
        for (int row=0; row<7; row++) for (int col=0; col<5; col++)
            if (moon_font[c][row] & (16u>>col)) rectangle(pixels,x+col,y+row,1,1,color);
    }
}

static void value(uint16_t *pixels, int x, int y, const char *label, int number, unsigned digits, unsigned base)
{
    char buffer[32];
    unsigned length=0;
    while (*label && length<24) buffer[length++]=*label++;
    for (unsigned i=0; i<digits; i++) {
        unsigned divisor=1;
        for (unsigned j=i+1; j<digits; j++) divisor*=base;
        buffer[length++]=number<0 ? '-' : "0123456789ABCDEF"[((unsigned)number/divisor)%base];
    }
    buffer[length]=0;
    text(pixels,x,y,buffer,INK);
}

static void signal(uint16_t *pixels, int x, int y, int lamps, unsigned offset)
{
    static const uint16_t colors[] = {0xf800,0xffe0,0x07e0};
    rectangle(pixels,x-2,y-2,11,31,0);
    for (unsigned bit=0; bit<3; bit++)
        rectangle(pixels,x,y+(int)bit*9,7,7,
                  lamps>=0 && (lamps&(1u<<(bit+offset))) ? colors[bit] : 0x2945);
}

static void roads(uint16_t *pixels, const struct scene *scene)
{
    rectangle(pixels,0,24,254,218,0x1945);
    rectangle(pixels,0,110,254,50,ROAD);
    rectangle(pixels,101,24,50,218,ROAD);
    for (int x=0; x<254; x+=18) if (x<100 || x>150) rectangle(pixels,x,134,10,1,DIM);
    for (int y=26; y<242; y+=18) if (y<105 || y>160) rectangle(pixels,125,y,1,10,DIM);
    rectangle(pixels,98,137,2,22,INK);
    rectangle(pixels,152,111,2,22,INK);
    rectangle(pixels,102,106,22,2,INK);
    rectangle(pixels,127,162,22,2,INK);
    text(pixels,8,90,"MAIN",DIM);
    text(pixels,159,32,"SIDE",DIM);
    static const uint16_t colors[] = {0x5dff,0xfda8,0xd3ba,0xeedb};
    for (unsigned i=0; i<CAR_COUNT; i++) {
        const struct car *car=&scene->cars[i];
        if (!car->active) continue;
        int position=car->position/256, x=0, y=0;
        if (car->lane==0) { x=position-12; y=142; }
        if (car->lane==1) { x=254-position; y=118; }
        if (car->lane==2) { x=109; y=position+24-12; }
        if (car->lane==3) { x=134; y=242-position; }
        /* Clip cars to the scene, including entry/exit boundaries. */
        int w=car->lane<2 ? 12 : 7, h=car->lane<2 ? 7 : 12;
        for (int row=y; row<y+h; row++) if (row>=24 && row<242)
            for (int col=x; col<x+w; col++) if (col>=0 && col<254)
                pixels[row*WIDTH+col]=colors[car->color];
    }
    signal(pixels,86,169,scene->cpu.lamps,0);
    signal(pixels,163,80,scene->cpu.lamps,0);
    signal(pixels,83,69,scene->cpu.lamps,5);
    signal(pixels,164,169,scene->cpu.lamps,5);
    value(pixels,8,213,"T1 ",(scene->cpu.tests>>1)&1,1,10);
    value(pixels,8,225,"T3 ",(scene->cpu.tests>>3)&1,1,10);
    text(pixels,153,224,"SIDE",DIM);
}

void demo_render(const struct demo *demo, const struct app_settings *settings, uint16_t *pixels)
{
    (void)settings;
    const struct scene *scene=&demo->traffic;
    const struct cpu *cpu=&scene->inspector;
    for (unsigned i=0; i<WIDTH*HEIGHT; i++) pixels[i]=BG;
    text(pixels,7,8,"CMC8 TRAFFIC",INK);
    text(pixels,90,8,scene->paused ? "PAUSE" : "RUN",INK);
    text(pixels,126,8,scene_speed_name(scene),INK);
    text(pixels,156,8,scene->instruction_view ? "INSTR" : "PHASE",CYAN);
    value(pixels,190,8,"SEC ",(int)(scene->traffic_ms/1000),5,10);
    roads(pixels,scene);
    rectangle(pixels,258,0,1,246,DIM);
    text(pixels,268,8,"V018 MOP DATAPATH",CYAN);
    value(pixels,268,23,"F",cpu->last_phase,1,10);
    value(pixels,286,23,"T",cpu->last_timing,1,10);
    text(pixels,312,23,cpu_instruction(cpu),INK);
    value(pixels,384,23,"PG ",cpu->s.pg,1,10);
    value(pixels,432,23,"N ",cpu->s.n,1,10);
    value(pixels,268,36,"IR ",cpu->s.ir,3,8);
    value(pixels,340,36,"BR ",cpu->s.br,3,8);
    value(pixels,412,36,"AB ",cpu->s.ab,3,8);
    for (unsigned i=0; i<8; i++) {
        char label[]="R0 "; label[1]=(char)('0'+i);
        int x=268+(int)(i%2)*106, y=50+(int)(i/2)*12;
        if (cpu->end.selected==(int)i) rectangle(pixels,x-2,y-2,90,11,0x22cb);
        value(pixels,x,y,label,cpu->s.r[i],3,8);
    }
    value(pixels,268,101,"DI ",cpu->end.di,3,8);
    value(pixels,374,101,"DB ",cpu->end.db,3,8);
    value(pixels,268,113,"ALU ",cpu->end.alu,3,8);
    value(pixels,374,113,"MUX ",cpu->end.mux,3,8);
    value(pixels,268,127,"Z ",cpu->s.z,1,10);
    value(pixels,310,127,"H ",cpu->s.h,1,10);
    value(pixels,352,127,"ED4 ",cpu->lamps,3,8);
    text(pixels,268,142,"MOPS - LIT WHEN ASSERTED",CYAN);
    for (unsigned number=1; number<=57; number++) {
        int x=268+(int)((number-1)%8)*26, y=155+(int)((number-1)/8)*11;
        int active=(cpu->mops&(UINT64_C(1)<<number))!=0;
        rectangle(pixels,x-2,y-1,23,10,active ? 0x246a : 0x18c3);
        char label[3]={(char)('0'+number/10),(char)('0'+number%10),0};
        text(pixels,x,y,label,active ? 0xffe0 : DIM);
    }
    if (cpu->fault) value(pixels,268,242,"CPU FAULT ",cpu->fault,1,10);
    else {
        value(pixels,268,242,"CPU SEC ",(int)(scene->cpu.slots/125000),5,10);
        text(pixels,356,242,"--- UNDRIVEN",DIM);
    }
    text(pixels,7,251,"START PAUSE  A SLOT  B INSTR  X VIEW  Y SPEED  SELECT RESET",INK);
    text(pixels,7,262,"UP DOWN SENSORS  VOL SOUND  HOLD HOME EXIT",DIM);
}
