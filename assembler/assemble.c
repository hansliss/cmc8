#include "asm.h"
#include <ctype.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    Assembly *result;
    int pass, page, offset[4], wrap, equ_depth;
    const SourceLine *line;
} Pass;

static Symbol *find_symbol(Assembly *result, const char *name)
{
    size_t i;
    for (i = 0; i < result->symbol_count; ++i)
        if (same(result->symbols[i].name,name)) return &result->symbols[i];
    return NULL;
}

static Value lookup(void *user, const char *name)
{
    Pass *pass = user;
    Symbol *symbol = find_symbol(pass->result,name);
    if (symbol == NULL) return (Value){0,0,0};
    if (symbol->equation != NULL) {
        Expression context = {pass,lookup,symbol->equation_pc,pass->pass == 1,symbol->source};
        if (symbol->resolving) {
            if (pass->pass == 1) return (Value){0,0,0};
            fail(symbol->source,"circular EQU involving '%s'",name);
        }
        if (++pass->equ_depth > 128) fail(symbol->source,"EQU dependency depth exceeds 128");
        symbol->resolving = 1;
        symbol->value = expression(symbol->equation,&context);
        symbol->resolving = 0;
        --pass->equ_depth;
    }
    return symbol->value;
}

static Value evaluate(Pass *pass, const char *text, int unknown)
{
    Expression context = {pass,lookup,pass->page*PAGE_SIZE+pass->offset[pass->page],unknown,pass->line};
    Value value;
    while (isspace((unsigned char)*text)) ++text;
    if (*text == '#') ++text;
    value = expression(text,&context);
    if (!value.known && !unknown) fail(pass->line,"expression must be known here");
    return value;
}

static int64_t ranged(Pass *pass, const char *text, int64_t low, int64_t high)
{
    Value value = evaluate(pass,text,0);
    if (value.number < low || value.number > high)
        fail(pass->line,"value %" PRId64 " is outside %" PRId64 "..%" PRId64,value.number,low,high);
    return value.number;
}

static void define(Pass *pass, const char *name, const char *equation)
{
    Assembly *result = pass->result;
    Symbol *symbol = find_symbol(result,name);
    Value value = constant(pass->page*PAGE_SIZE+pass->offset[pass->page]);
    value.address = 1;
    if (equation == NULL && pass->offset[pass->page] >= PAGE_SIZE)
        fail(pass->line,"label '%s' is past the end of its page; use ORG or WRAP",name);
    if (pass->pass == 1) {
        if (symbol != NULL) fail(pass->line,"duplicate symbol '%s' (first at %s:%u)",name,symbol->source->file,symbol->source->line);
        if (result->symbol_count == result->symbol_capacity) {
            result->symbol_capacity = result->symbol_capacity ? result->symbol_capacity*2 : 64;
            result->symbols = resize(result->symbols,result->symbol_capacity*sizeof(*result->symbols));
        }
        symbol = &result->symbols[result->symbol_count++];
        memset(symbol,0,sizeof(*symbol));
        symbol->name = copy_text(name);
        symbol->source = pass->line;
        symbol->equation_pc = value.number;
        symbol->equation = equation == NULL ? NULL : copy_text(equation);
        symbol->value = equation == NULL ? value : (Value){0,0,0};
    } else if (equation == NULL && (symbol == NULL || symbol->value.number != value.number || !symbol->value.address)) {
        fail(pass->line,"address of '%s' changed between passes",name);
    }
}

static void emit(Pass *pass, const unsigned char *bytes, size_t count, int initialized)
{
    Assembly *result = pass->result;
    int offset = pass->offset[pass->page];
    size_t i;
    if (count > PAGE_SIZE || (count && offset >= PAGE_SIZE) ||
        (!pass->wrap && count > (size_t)(PAGE_SIZE-offset)))
        fail(pass->line,"emission crosses a page boundary; select PAGE/ORG or explicitly enable WRAP");
    if (pass->pass == 2 && result->listing != NULL) {
        fprintf(result->listing,"%d:%03o  ",pass->page,offset);
        for (i = 0; i < count && i < 8; ++i) {
            if (initialized) fprintf(result->listing,"%02X ",bytes[i]);
            else fputs(".. ",result->listing);
        }
        if (count > 8) fputs("... ",result->listing);
        fprintf(result->listing," %s:%u  %s\n",pass->line->file,pass->line->line,pass->line->text);
        if (pass->line->expansion != NULL) fprintf(result->listing,"         ; expanded from %s\n",pass->line->expansion);
    }
    for (i = 0; i < count; ++i) {
        int address = pass->page*PAGE_SIZE + ((offset+(int)i)&255);
        if (result->claimed[address]) fail(pass->line,"overlapping output at page%d offset%03o",pass->page,address&255);
        result->claimed[address] = 1;
        if (initialized && pass->pass == 2) {
            result->used[address] = 1;
            result->image[address] = bytes[i];
            ++result->emitted;
        }
    }
    pass->offset[pass->page] = pass->wrap ? (offset+(int)count)&255 : offset+(int)count;
}

static int selector(Pass *pass, const char *text, int test)
{
    char prefix = test ? 'T' : 'R';
    int high = test ? 3 : 7;
    if (!test && same(text,"X")) return 7;
    if (toupper((unsigned char)text[0]) == prefix && isdigit((unsigned char)text[1])) ++text;
    return (int)ranged(pass,text,0,high);
}

static unsigned byte_operand(Pass *pass, const char *text)
{
    return (unsigned)ranged(pass,text,0,255);
}

static unsigned same_page(Pass *pass, const char *text)
{
    Value value = evaluate(pass,text,0);
    if (value.number < 0 || value.number >= IMAGE_SIZE) fail(pass->line,"address must be 0..1023");
    if ((value.address || value.number > 255) && (value.number >> 8) != pass->page)
        fail(pass->line,"cross-page target: instruction uses current PG=%d, target is on page%" PRId64
             "; use an appropriate trampoline or explicit LOW() if intentional",pass->page,value.number >> 8);
    return (unsigned)value.number & 255;
}

static void encode(Pass *pass, const Instruction *op, char **args, int argc)
{
    unsigned char bytes[2] = {0,0};
    int expected = op->kind == OP_NONE ? 0 : op->length == 1 ? 1 :
                   op->kind == OP_CALL || op->kind == OP_CONTROL ? 1 : 2;
    if (op->kind == OP_PAGE_BRANCH) {
        if (argc != 1 && argc != 2) fail(pass->line,"%s expects target or page,target",op->name);
    } else if (argc != expected) fail(pass->line,"%s expects %d operands, got %d",op->name,expected,argc);
    if (pass->pass == 1) { emit(pass,bytes,op->length,1); return; }
    bytes[0] = (unsigned char)op->opcode;
    switch (op->kind) {
    case OP_NONE: break;
    case OP_REG: bytes[0] |= (unsigned char)selector(pass,args[0],0); break;
    case OP_CONTROL: bytes[1] = (unsigned char)byte_operand(pass,args[0]); break;
    case OP_CALL: bytes[1] = (unsigned char)same_page(pass,args[0]); break;
    case OP_PAGE_BRANCH: {
        Value target = evaluate(pass,args[argc-1],0);
        unsigned page;
        if (target.number < 0 || target.number >= IMAGE_SIZE) fail(pass->line,"branch target must be 0..1023");
        if (argc == 2) {
            page = (unsigned)ranged(pass,args[0],0,3);
            if ((target.address || target.number > 255) && (unsigned)(target.number >> 8) != page)
                fail(pass->line,"explicit page disagrees with target label/address");
        } else page = target.address || target.number > 255 ? (unsigned)(target.number >> 8) : (unsigned)pass->page;
        bytes[0] |= (unsigned char)page;
        bytes[1] = (unsigned char)(target.number & 255);
        break;
    }
    case OP_TEST_BRANCH:
        bytes[0] |= (unsigned char)selector(pass,args[0],1);
        bytes[1] = (unsigned char)same_page(pass,args[1]);
        break;
    default:
        bytes[0] |= (unsigned char)selector(pass,args[0],0);
        bytes[1] = (unsigned char)((op->kind == OP_IMMEDIATE || op->kind == OP_PORT) ?
                                  byte_operand(pass,args[1]) : same_page(pass,args[1]));
        break;
    }
    emit(pass,bytes,op->length,1);
}

static void data(Pass *pass, char **args, int argc, int word)
{
    unsigned char bytes[PAGE_SIZE];
    size_t count = 0;
    int i;
    if (!argc) fail(pass->line,"data directive needs at least one operand");
    for (i = 0; i < argc; ++i) {
        if (!word && args[i][0] == '"') {
            const char *p = args[i]+1;
            while (*p && *p != '"') {
                if (count == PAGE_SIZE) { fail(pass->line,"data block exceeds one page"); return; }
                bytes[count++] = (unsigned char)escape_byte(&p,pass->line);
            }
            if (*p++ != '"' || *trim((char *)p)) fail(pass->line,"invalid string data");
        } else {
            unsigned value = pass->pass == 1 ? 0 : (unsigned)ranged(pass,args[i],0,word ? 65535 : 255);
            if (count + (word ? 2u : 1u) > PAGE_SIZE) { fail(pass->line,"data block exceeds one page"); return; }
            bytes[count++] = (unsigned char)(value & 255);
            if (word) bytes[count++] = (unsigned char)(value >> 8);
        }
    }
    emit(pass,bytes,count,1);
}

static void run_pass(Pass *pass, const Lines *lines)
{
    size_t i;
    memset(pass->offset,0,sizeof(pass->offset));
    pass->page = 0;
    pass->wrap = 0;
    memset(pass->result->claimed,0,sizeof(pass->result->claimed));
    for (i = 0; i < lines->count; ++i) {
        char *text = trim(without_comment(lines->items[i].text));
        char *op, *label = NULL, *args[MAX_ARGS], *cursor;
        const Instruction *insn;
        int argc;
        pass->line = &lines->items[i];
        if (!*text) continue;
        op = take_name(&text,pass->line);
        text = trim(text);
        if (*text == ':') {
            label = op;
            text = trim(text+1);
            if (!*text) { define(pass,label,NULL); continue; }
            op = take_name(&text,pass->line);
            text = trim(text);
        } else if (*text == '=') { define(pass,op,trim(text+1)); continue; }
        else if (name_start(*text)) {
            char *q = text, *second = take_name(&q,pass->line);
            if (same(second,"EQU") || same(second,".EQU")) { define(pass,op,trim(q)); continue; }
        }
        if (*op == '.') ++op;
        if (same(op,"EQU")) {
            if (label != NULL) define(pass,label,text);
            else {
                if (split_args(text,args,pass->line) != 2) fail(pass->line,"EQU needs name,expression");
                cursor = args[0];
                label = take_name(&cursor,pass->line);
                if (*trim(cursor)) fail(pass->line,"invalid EQU name");
                define(pass,label,args[1]);
            }
            continue;
        }
        if (label != NULL) define(pass,label,NULL);
        argc = split_args(text,args,pass->line);
        insn = instruction(op);
        if (insn != NULL) { encode(pass,insn,args,argc); continue; }
        if (same(op,"PAGE")) {
            if (argc != 1) fail(pass->line,"PAGE needs one page number");
            pass->page = (int)ranged(pass,args[0],0,3);
        } else if (same(op,"ORG") || same(op,"ORGA")) {
            Value origin;
            if (argc != 1) fail(pass->line,"%s needs one offset/address",op);
            origin = evaluate(pass,args[0],0);
            if (same(op,"ORG")) {
                if (origin.address) fail(pass->line,"ORG needs an offset; use LOW(label) or ORGA label");
                pass->offset[pass->page] = (int)ranged(pass,args[0],0,255);
            } else {
                unsigned address = (unsigned)ranged(pass,args[0],0,1023);
                pass->page = (int)(address >> 8);
                pass->offset[pass->page] = (int)(address & 255);
            }
        } else if (same(op,"WRAP")) {
            if (argc != 1 || !(same(args[0],"ON") || same(args[0],"OFF"))) fail(pass->line,"WRAP needs ON or OFF");
            pass->wrap = same(args[0],"ON");
            if (pass->wrap && pass->offset[pass->page] == PAGE_SIZE) pass->offset[pass->page] = 0;
        } else if (same(op,"BYTE") || same(op,"DB") || same(op,"ASCII")) data(pass,args,argc,0);
        else if (same(op,"WORD") || same(op,"DW")) data(pass,args,argc,1);
        else if (same(op,"FILL") || same(op,"RES")) {
            unsigned char bytes[PAGE_SIZE];
            size_t count;
            if (argc < 1 || argc > 2) fail(pass->line,"%s needs count[,value]",op);
            count = (size_t)ranged(pass,args[0],0,PAGE_SIZE);
            memset(bytes,argc == 2 ? (int)ranged(pass,args[1],0,255) : 0,sizeof(bytes));
            emit(pass,bytes,count,!same(op,"RES") || argc == 2);
        } else if (same(op,"ASSERT")) {
            if (argc < 1 || argc > 2) fail(pass->line,"ASSERT needs expression[,message]");
            if (pass->pass == 2 && !evaluate(pass,args[0],0).number)
                fail(pass->line,"assertion failed%s%s",argc == 2 ? ": " : "",argc == 2 ? args[1] : "");
        } else if (same(op,"ERROR")) fail(pass->line,"%s",text);
        else if (same(op,"END")) {
            if (argc) fail(pass->line,"END takes no operands");
            break;
        } else fail(pass->line,"unknown instruction or directive '%s'",op);
    }
}

void assemble(Assembly *result, const Lines *lines)
{
    Pass pass;
    size_t i;
    memset(&pass,0,sizeof(pass));
    pass.result = result;
    pass.pass = 1;
    run_pass(&pass,lines);
    /* Resolve forward EQU chains after all labels/constants are registered. */
    pass.pass = 2;
    for (i = 0; i < result->symbol_count; ++i) {
        pass.line = result->symbols[i].source;
        (void)lookup(&pass,result->symbols[i].name);
    }
    run_pass(&pass,lines);
}
