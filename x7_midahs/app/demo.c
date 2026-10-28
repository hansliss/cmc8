/* All panel overlays use the actual board latches; keys do not fake displays. */
#include "demo.h"
#include "controls.h"
#include "sdk/platform/font.h"
#include "../generated/reference.h"
#define WHITE 0xef7d
#define DIM 0x9cd3
#define CYAN 0x5dff
#define RED 0xfae8
#define BG 0x1082

void demo_init(struct demo *demo) { panel_init(&demo->panel); }
void demo_actions(struct demo *demo, unsigned pressed, unsigned held) { panel_actions(&demo->panel,pressed,held); }
void demo_tick(struct demo *demo, unsigned held, const struct app_settings *settings)
{
    (void)settings;
    panel_tick(&demo->panel,held);
}

static void rect(uint16_t *pixels,int x,int y,int w,int h,uint16_t color)
{
    for (int row=y;row<y+h;row++) if (row>=0 && row<272)
        for (int col=x;col<x+w;col++) if (col>=0 && col<480) pixels[row*480+col]=color;
}
static void outline(uint16_t *pixels,int x,int y,int w,int h,uint16_t color)
{
    rect(pixels,x,y,w,1,color);rect(pixels,x,y+h-1,w,1,color);
    rect(pixels,x,y,1,h,color);rect(pixels,x+w-1,y,1,h,color);
}
static void text(uint16_t *pixels,int x,int y,const char *s,unsigned scale,uint16_t color)
{
    for (;*s;s++,x+=(int)(6*scale)) {
        unsigned c=(unsigned char)*s;
        static const unsigned char lower_r[7]={0,0,22,25,16,16,16};
        static const unsigned char lower_p[7]={0,0,30,17,30,16,16};
        static const unsigned char lower_t[7]={8,8,30,8,8,9,6};
        static const unsigned char hash[7]={10,10,31,10,31,10,10};
        const unsigned char *glyph=0;
        if (c=='r') glyph=lower_r;
        else if (c=='p') glyph=lower_p;
        else if (c=='t') glyph=lower_t;
        else if (c=='#') glyph=hash;
        if (*s=='+') {
            rect(pixels,x,y+3*(int)scale,5*(int)scale,(int)scale,color);
            rect(pixels,x+2*(int)scale,y+(int)scale,(int)scale,5*(int)scale,color);
            continue;
        }
        if (!glyph) {
            if (c>='a' && c<='z') c-=32;
            if (c>='0' && c<='9') c-='0';
            else if (c>='A' && c<='Z') c=c-'A'+10;
            else if (c=='-') c=36;
            else if (c==':') c=41;
            else if (c==',') c=42;
            else continue;
            glyph=moon_font[c];
        }
        for (unsigned row=0;row<7;row++) for (unsigned col=0;col<5;col++)
            if (glyph[row]&(16u>>col))
                rect(pixels,x+(int)(col*scale),y+(int)(row*scale),(int)scale,(int)scale,color);
    }
}
static void octal(uint16_t *pixels,int x,int y,unsigned value,unsigned digits,unsigned scale)
{
    char s[5];
    for (unsigned i=0;i<digits;i++) s[digits-i-1]=(char)('0'+((value>>(3*i))&7));
    s[digits]=0;text(pixels,x,y,s,scale,RED);
}
static void page_digits(uint16_t *pixels,int x,int y,const struct midahs *m,unsigned scale)
{
    for (unsigned i=0;i<3;i++) if (m->ports[6]&(1u<<i))
        octal(pixels,x+(int)(6*scale*i),y,(m->ports[0]>>(3*(2-i)))&7,1,scale);
}

static void reference_screen(uint16_t *pixels,unsigned page)
{
    for (unsigned i=0;i<480*272;i++) pixels[i]=BG;
    text(pixels,8,7,"CMC8 INSTRUCTION CARD",1,CYAN);
    char title[]="1 OF 2";title[0]=(char)('1'+page);
    text(pixels,162,7,title,1,WHITE);
    text(pixels,302,7,"L R PAGE   B BACK",1,DIM);
    text(pixels,8,24,"FORM",1,DIM);
    text(pixels,144,24,"BITS",1,DIM);
    text(pixels,208,24,"OCTAL",1,DIM);
    text(pixels,266,24,"FLAGS",1,DIM);
    text(pixels,308,24,"B",1,DIM);text(pixels,326,24,"C",1,DIM);
    text(pixels,352,24,"OPERATION",1,DIM);
    unsigned first=page*REFERENCE_PAGE_ROWS;
    for (unsigned row=0;row<REFERENCE_PAGE_ROWS && first+row<REFERENCE_ROWS;row++) {
        const struct reference_row *entry=&reference_rows[first+row];
        int y=36+(int)row*9;
        if (row&1) rect(pixels,4,y-1,472,9,0x18c3);
        text(pixels,8,y,entry->form,1,WHITE);
        text(pixels,144,y,entry->bits,1,CYAN);
        text(pixels,208,y,entry->octal,1,WHITE);
        text(pixels,266,y,entry->flags,1,WHITE);
        octal(pixels,308,y,entry->bytes,1,1);
        octal(pixels,326,y,entry->cycles,1,1);
        text(pixels,352,y,entry->meaning,1,DIM);
    }
    text(pixels,8,239,"r REG 0-7  X R7  p PAGE 0-3  t TEST 0-3",1,CYAN);
    text(pixels,8,250,"A ADDRESS  P PORT  I IMMEDIATE  B BYTES  C BASE CYCLES",1,DIM);
    text(pixels,8,261,"- NO FLAG CHANGE   OCTAL BASE + SELECTOR   WAITS ADD CYCLES",1,DIM);
}

void demo_render(const struct demo *demo,const struct app_settings *settings,uint16_t *pixels)
{
    (void)settings;
    const struct panel *p=&demo->panel;
    if (p->help) { reference_screen(pixels,p->help_page);return; }
    const struct midahs *m=&p->machine;
    for (unsigned y=0;y<272;y++) for (unsigned x=0;x<480;x++) {
        if (p->photo && x<PANEL_WIDTH) {
            unsigned offset=2*(y*PANEL_WIDTH+x);
            pixels[y*480+x]=(uint16_t)(p->photo[offset]|(p->photo[offset+1]<<8));
        } else pixels[y*480+x]=BG;
    }
    if (!p->photo) {
        text(pixels,110,60,"MIDAHS",3,WHITE);
        text(pixels,80,90,"PHOTO NOT LOADED",1,DIM);
        outline(pixels,310,93,69,65,DIM);
        text(pixels,8,107,"ED4",1,DIM);
        text(pixels,8,178,"ED3",1,DIM);
    }
    /* Crisp register digits over the three groups in the photograph. */
    rect(pixels,315,118,63,17,0);
    page_digits(pixels,315,123,m,1);
    octal(pixels,336,123,m->ports[1],3,1);
    octal(pixels,357,123,m->ports[2],3,1);
    /* Derived instruction-level fetch observations, not a MOP bus trace. */
    rect(pixels,102,29,29,8,0);octal(pixels,104,29,m->pg,1,1);octal(pixels,112,29,m->r[m->n],3,1);
    rect(pixels,102,241,19,9,0);octal(pixels,103,242,m->program[m->pg*256+m->r[m->n]],3,1);
    for (unsigned bit=0;bit<8;bit++) {
        rect(pixels,17,116+(int)bit*3,4,2,m->ports[4]&(1u<<bit)?0xffe0:0x2104);
        const struct panel_control *control=&panel_controls[bit];
        rect(pixels,control->x,control->y,control->w,control->h,0x18c3);
        rect(pixels,control->x+((m->ports[3]&(1u<<bit))?9:1),control->y,4,control->h,WHITE);
    }
    for (unsigned i=8;i<20;i++) {
        const struct panel_control *control=&panel_controls[i];
        rect(pixels,control->x,control->y,control->w,control->h,p->active_key==(int)i?0x2b6f:0x2104);
        text(pixels,control->x+(control->name[1]?1:4),control->y+3,control->name,1,WHITE);
    }
    /* Extra board switches use real pin levels; small levers show up/down. */
    for (unsigned i=CONTROL_TT0;i<CONTROL_COUNT;i++) {
        const struct panel_control *control=&panel_controls[i];
        unsigned level=0;
        if (i<CONTROL_CL) level=(m->tests>>(i-CONTROL_TT0))&1;
        else if (i==CONTROL_RESET) level=m->reset_level;
        else if (i==CONTROL_INT) level=m->int_level;
        else if (i==CONTROL_MEMR) level=m->memr;
        else if (i==CONTROL_HALT) level=m->halt;
        else if (i==CONTROL_SS) level=m->ss;
        else if (i==CONTROL_SCWR) level=m->scwr;
        else if (i==CONTROL_WP) level=m->wp;
        rect(pixels,control->x,control->y,control->w,control->h,0x2104);
        outline(pixels,control->x,control->y,control->w,control->h,DIM);
        int offset=level?1:control->h-4;
        if (i==CONTROL_CLOCK) offset=p->clock==CLOCK_HIGH?1:p->clock==CLOCK_MANUAL?4:7;
        if (i==CONTROL_CL) offset=4;
        rect(pixels,control->x+3,control->y+offset,6,3,
             i==CONTROL_CL && p->focus==i && (p->held&KEY_A)?CYAN:WHITE);
    }
    const struct panel_control *focus=&panel_controls[p->focus];
    outline(pixels,focus->x-2,focus->y-2,focus->w+4,focus->h+4,CYAN);
    /* A small pointer plus snapping outline identifies even 3px switch targets. */
    rect(pixels,focus->x+focus->w+3,focus->y,4,1,CYAN);
    rect(pixels,focus->x+focus->w+4,focus->y-1,3,3,CYAN);
    /* This is the KEX pushbutton, not the separate KEX-active lamp. */
    rect(pixels,301,192,7,7,0x2104);
    outline(pixels,301,192,7,7,DIM);

    rect(pixels,391,0,89,272,BG);
    text(pixels,397,7,"MIDAHS",1,CYAN);
    text(pixels,397,25,"PAGE ESP",1,DIM);page_digits(pixels,397,36,m,2);
    text(pixels,397,59,"ADDRESS",1,DIM);octal(pixels,397,70,m->ports[1],3,2);
    text(pixels,397,93,"DATA",1,DIM);octal(pixels,397,104,m->ports[2],3,2);
    text(pixels,397,128,"SELECTED",1,DIM);
    text(pixels,397,141,focus->name,focus->name[1]?1:2,WHITE);
    text(pixels,397,157,panel_control_state(p,p->focus),p->focus<8?2:1,CYAN);
    static const char *const waits[]={"","RESET","WAIT MEMR","HALTED","WAIT SCWR"};
    text(pixels,397,180,p->paused?"PAUSED":m->waiting?waits[m->waiting]:
         m->kex?(m->r[3]&1?"KEX DA":"KEX AD"):"USER",1,WHITE);
    text(pixels,397,192,m->fault?midahs_error(m):m->intr?"IRQ PENDING":m->write_blocked?"WRITE BLOCKED":"",1,RED);
    text(pixels,397,202,"T",1,DIM);octal(pixels,409,202,p->clock_pulses&7,1,1);
    text(pixels,397,212,"D PAD MOVE",1,DIM);
    text(pixels,397,223,"A PRESS",1,DIM);
    text(pixels,397,234,"B KEX",1,DIM);
    text(pixels,397,245,"L R HELP",1,DIM);
    text(pixels,397,260,"HOLD HOME",1,DIM);
}
