#include "asm.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

#define MAX_DEPTH 32
#define MAX_REPEAT 10000

typedef struct {
    char *name;
    char **parameters;
    int parameter_count;
    Lines body;
} Macro;

typedef struct { char *name; Value value; } PreConstant;
typedef struct {
    Macro *macros;
    size_t macro_count;
    PreConstant *constants;
    size_t constant_count;
    const char **include_dirs;
    size_t dir_count;
    unsigned serial;
    int ended;
    Lines output;
} Preprocessor;

typedef struct { char *label, *op, *rest; } Head;

static Head head(const SourceLine *line)
{
    char *p = trim(without_comment(line->text));
    Head result = {NULL,NULL,NULL};
    if (!*p) return result;
    if (p[0] == '%' && p[1] == '%') p += 2; /* Scan unexpanded macro-local labels. */
    if (!name_start(*p)) return result;
    result.op = take_name(&p, line);
    p = trim(p);
    if (*p == ':') {
        result.label = result.op;
        p = trim(p + 1);
        if (!*p) { result.op = NULL; return result; }
        result.op = take_name(&p, line);
    }
    result.rest = trim(p);
    if (result.op[0] == '.') {
        static const char *commands[] = {"MACRO","ENDM","REPT","ENDR","IF","IFDEF",
                                         "IFNDEF","ELSE","ENDIF","INCLUDE","EQU","END"};
        size_t i;
        for (i = 0; i < sizeof(commands)/sizeof(commands[0]); ++i)
            if (same(result.op+1,commands[i])) { ++result.op; break; }
    }
    return result;
}

static int reserved(const char *name)
{
    static const char *names[] = {"ORG","ORGA","PAGE","BYTE","DB","ASCII","WORD","DW",
        "EQU","WRAP","FILL","RES","ASSERT","ERROR","END","INCLUDE","MACRO",
        "ENDM","IF","IFDEF","IFNDEF","ELSE","ENDIF","REPT","ENDR"};
    size_t i;
    if (*name == '.') ++name;
    if (instruction(name) != NULL) return 1;
    for (i = 0; i < sizeof(names)/sizeof(names[0]); ++i)
        if (same(name,names[i])) return 1;
    return 0;
}

static Macro *find_macro(Preprocessor *p, const char *name)
{
    size_t i;
    for (i = 0; i < p->macro_count; ++i)
        if (same(name, p->macros[i].name)) return &p->macros[i];
    return NULL;
}

static Value find_constant(void *user, const char *name)
{
    Preprocessor *p = user;
    size_t i;
    for (i = 0; i < p->constant_count; ++i)
        if (same(name,p->constants[i].name)) return p->constants[i].value;
    return (Value){0,0,0};
}

static Value pre_expression(Preprocessor *p, const char *text, const SourceLine *line, int unknown)
{
    Expression context = {p,find_constant,-1,unknown,line};
    Value value = expression(text,&context);
    if (!value.known && !unknown) fail(line,"preprocessing expression must already be known");
    return value;
}

static void remember_constant(Preprocessor *p, Head h, const SourceLine *line)
{
    char *name = NULL, *expr = NULL;
    if (same(h.op,"EQU")) {
        if (h.label != NULL) { name = h.label; expr = h.rest; }
        else {
            char *args[MAX_ARGS];
            if (split_args(h.rest,args,line) != 2) fail(line,"EQU needs name, expression");
            name = args[0]; expr = args[1];
        }
    } else if (*h.rest == '=') { name = h.op; expr = trim(h.rest + 1); }
    else if (name_start(*h.rest)) {
        char *q = h.rest, *second = take_name(&q,line);
        if (same(second,"EQU") || same(second,".EQU")) { name = h.op; expr = trim(q); }
    }
    if (name != NULL) {
        Value value = pre_expression(p,expr,line,1);
        if (value.known) {
            p->constants = resize(p->constants,(p->constant_count+1)*sizeof(*p->constants));
            p->constants[p->constant_count++] = (PreConstant){copy_text(name),value};
        }
    }
}

static char *join_path(const char *directory, const char *name)
{
    size_t length = strlen(directory) + strlen(name) + 2;
    char *path = allocate(length);
    snprintf(path,length,"%s/%s",directory,name);
    return path;
}

static char *relative_path(const char *file, const char *name)
{
    const char *a = strrchr(file,'/'), *b = strrchr(file,'\\'), *slash = a;
    char *directory;
    if (name[0] == '/' || (name[0] && name[1] == ':')) return copy_text(name);
    if (b != NULL && (slash == NULL || b > slash)) slash = b;
    if (slash == NULL) return copy_text(name);
    directory = copy_n(file,(size_t)(slash-file));
    return join_path(directory,name);
}

static Lines read_file(const char *path, const SourceLine *caller)
{
    Lines result = {NULL,0,0};
    FILE *input = fopen(path,"r");
    char buffer[4096];
    unsigned number = 0;
    if (input == NULL) fail(caller,"cannot open source '%s'",path);
    while (fgets(buffer,sizeof(buffer),input) != NULL) {
        SourceLine line;
        size_t length = strlen(buffer);
        ++number;
        if (length && buffer[length-1] != '\n' && !feof(input)) {
            int next = fgetc(input);
            if (next != EOF) fail(caller,"%s:%u: source line exceeds 4095 bytes",path,number);
        }
        while (length && (buffer[length-1] == '\n' || buffer[length-1] == '\r')) buffer[--length] = '\0';
        line = (SourceLine){copy_text(number == 1 && length >= 3 &&
                            (unsigned char)buffer[0] == 0xEF && (unsigned char)buffer[1] == 0xBB &&
                            (unsigned char)buffer[2] == 0xBF ? buffer+3 : buffer),copy_text(path),number,
                            caller == NULL ? NULL : caller->expansion};
        append_line(&result,line);
    }
    if (ferror(input)) fail(caller,"error reading source '%s'",path);
    fclose(input);
    if (result.count == 0)
        append_line(&result,(SourceLine){copy_text(""),copy_text(path),1,NULL});
    return result;
}

static void put(char **buffer, size_t *length, size_t *capacity, const char *text, size_t count)
{
    if (*length + count + 1 > 65536) fail(NULL,"macro expansion line exceeds 65535 bytes");
    if (*length + count + 1 > *capacity) {
        *capacity = (*length + count + 1)*2;
        *buffer = resize(*buffer,*capacity);
    }
    memcpy(*buffer + *length,text,count);
    *length += count;
    (*buffer)[*length] = '\0';
}

static char *substitute(const char *text, const Macro *macro, char **args, unsigned serial,
                        const SourceLine *call)
{
    char *buffer = NULL;
    size_t length = 0, capacity = 0;
    int quote = 0;
    while (*text) {
        if (quote) {
            put(&buffer,&length,&capacity,text,1);
            if (*text == '\\' && text[1]) { ++text; put(&buffer,&length,&capacity,text,1); }
            else if (*text == quote) quote = 0;
            ++text;
        } else if (*text == '\'' || *text == '"') {
            quote = *text;
            put(&buffer,&length,&capacity,text++,1);
        } else if (*text == ';') {
            put(&buffer,&length,&capacity,text,strlen(text));
            break;
        } else if (*text == '\\') {
            char replacement[64], *name;
            const char *start;
            int index = -1, i;
            ++text;
            if (*text == '@') {
                snprintf(replacement,sizeof(replacement),"%u",serial);
                put(&buffer,&length,&capacity,replacement,strlen(replacement));
                ++text;
                continue;
            }
            start = text;
            while (name_char(*text)) ++text;
            if (text == start) fail(call,"expected macro parameter after backslash");
            name = copy_n(start,(size_t)(text-start));
            if (isdigit((unsigned char)*name)) {
                char *end;
                long position = strtol(name,&end,10);
                if (*end == '\0' && position > 0 && position <= macro->parameter_count) index = (int)position-1;
            } else for (i = 0; i < macro->parameter_count; ++i)
                if (same(name,macro->parameters[i])) index = i;
            if (index < 0) fail(call,"unknown macro parameter '%s'",name);
            put(&buffer,&length,&capacity,args[index],strlen(args[index]));
        } else if (text[0] == '%' && text[1] == '%') {
            char prefix[64];
            text += 2;
            if (!name_start(*text)) fail(call,"expected local label name after %%" );
            snprintf(prefix,sizeof(prefix),"__M%u_",serial);
            put(&buffer,&length,&capacity,prefix,strlen(prefix));
            while (name_char(*text)) put(&buffer,&length,&capacity,text++,1);
        } else put(&buffer,&length,&capacity,text++,1);
    }
    return buffer != NULL ? buffer : copy_text("");
}

static void expand(Preprocessor *p, const Lines *input, size_t first, size_t last, int depth);

static void invoke(Preprocessor *p, const Macro *macro, char **args, const SourceLine *call, int depth)
{
    Lines expanded = {NULL,0,0};
    size_t i, length = strlen(call->file)+strlen(macro->name)+80;
    char *context;
    unsigned serial;
    if (p->serial == MAX_EXPANSION) fail(call,"macro/repetition invocations exceed %d",MAX_EXPANSION);
    serial = ++p->serial;
    if (call->expansion != NULL) length += strlen(call->expansion);
    context = allocate(length);
    snprintf(context,length,"%s:%u (%s)%s%s",call->file,call->line,macro->name,
             call->expansion == NULL ? "" : " <- ",call->expansion == NULL ? "" : call->expansion);
    for (i = 0; i < macro->body.count; ++i) {
        SourceLine line = macro->body.items[i];
        line.text = substitute(line.text,macro,args,serial,call);
        line.expansion = context;
        append_line(&expanded,line);
    }
    expand(p,&expanded,0,expanded.count,depth+1);
}

static size_t block_end(const Lines *input, size_t first, size_t last,
                        const char *open, const char *close, size_t *alternative)
{
    size_t i;
    int depth = 1;
    if (alternative != NULL) *alternative = last;
    for (i = first+1; i < last; ++i) {
        Head h = head(&input->items[i]);
        if (h.op == NULL) continue;
        if (same(h.op,open) || (same(open,"IF") && (same(h.op,"IFDEF") || same(h.op,"IFNDEF")))) ++depth;
        else if (same(h.op,close)) {
            if (h.label != NULL || *h.rest) fail(&input->items[i],"%s takes no label or operands",close);
            if (--depth == 0) return i;
        } else if (alternative != NULL && depth == 1 && same(h.op,"ELSE")) {
            if (h.label != NULL || *h.rest) fail(&input->items[i],"ELSE takes no label or operands");
            if (*alternative != last) fail(&input->items[i],"duplicate ELSE");
            *alternative = i;
        }
    }
    fail(&input->items[first],"missing %s",close);
    return last;
}

static void expand(Preprocessor *p, const Lines *input, size_t first, size_t last, int depth)
{
    size_t i;
    if (depth > MAX_DEPTH) fail(first < last ? &input->items[first] : NULL,"macro/include/repetition depth exceeds %d",MAX_DEPTH);
    if (first == 0 && first < last) {
        SourceLine marker = input->items[first];
        marker.text = copy_text("");
        marker.line = 0;  /* Preserve included filenames even for definitions-only headers. */
        append_line(&p->output,marker);
    }
    for (i = first; i < last && !p->ended; ++i) {
        SourceLine line = input->items[i];
        Head h = head(&line);
        Macro *macro;
        if (h.op == NULL) { append_line(&p->output,line); continue; }
        if (same(h.op,"MACRO")) {
            char *cursor = h.rest, *name = take_name(&cursor,&line), *params[MAX_ARGS];
            size_t end = block_end(input,i,last,"MACRO","ENDM",NULL), j;
            int count = split_args(trim(cursor),params,&line), k;
            Macro definition = {name,NULL,0,{NULL,0,0}};
            if (find_macro(p,name) != NULL || reserved(name))
                fail(&line,"macro name '%s' is already used",name);
            if (h.label != NULL) fail(&line,"label on macro definition");
            definition.parameters = allocate((size_t)count*sizeof(char *));
            definition.parameter_count = count;
            for (k = 0; k < count; ++k) {
                char *q = params[k], *parameter = take_name(&q,&line);
                int n;
                if (*trim(q)) fail(&line,"invalid parameter '%s'",params[k]);
                for (n = 0; n < k; ++n) if (same(definition.parameters[n],parameter)) fail(&line,"duplicate macro parameter");
                definition.parameters[k] = parameter;
            }
            for (j = i+1; j < end; ++j) {
                Head body_head = head(&input->items[j]);
                if (body_head.op != NULL && same(body_head.op,"MACRO")) fail(&input->items[j],"nested macro definitions are not supported");
                append_line(&definition.body,input->items[j]);
            }
            p->macros = resize(p->macros,(p->macro_count+1)*sizeof(*p->macros));
            p->macros[p->macro_count++] = definition;
            i = end;
        } else if (same(h.op,"IF") || same(h.op,"IFDEF") || same(h.op,"IFNDEF")) {
            size_t alternative, end = block_end(input,i,last,"IF","ENDIF",&alternative);
            int condition;
            if (h.label != NULL) fail(&line,"label on conditional directive");
            if (same(h.op,"IF")) condition = pre_expression(p,h.rest,&line,0).number != 0;
            else {
                char *q = h.rest, *name = take_name(&q,&line);
                if (*trim(q)) fail(&line,"expected one name after %s",h.op);
                condition = find_macro(p,name) != NULL || find_constant(p,name).known;
                if (same(h.op,"IFNDEF")) condition = !condition;
            }
            if (condition) expand(p,input,i+1,alternative < end ? alternative : end,depth+1);
            else if (alternative < end) expand(p,input,alternative+1,end,depth+1);
            i = end;
        } else if (same(h.op,"REPT")) {
            size_t end = block_end(input,i,last,"REPT","ENDR",NULL), j;
            int64_t repetitions = pre_expression(p,h.rest,&line,0).number, n;
            Macro repeat = {"REPT",NULL,0,{NULL,0,0}};
            if (h.label != NULL) fail(&line,"label on REPT directive");
            if (repetitions < 0 || repetitions > MAX_REPEAT) fail(&line,"REPT count must be 0..%d",MAX_REPEAT);
            for (j = i+1; j < end; ++j) append_line(&repeat.body,input->items[j]);
            for (n = 0; n < repetitions && !p->ended; ++n) invoke(p,&repeat,NULL,&line,depth);
            i = end;
        } else if (same(h.op,"INCLUDE")) {
            char *name, *path;
            FILE *probe;
            Lines included;
            size_t j;
            if (h.label != NULL || *h.rest != '"') fail(&line,"INCLUDE needs a quoted path");
            name = copy_text(h.rest+1);
            { char *end = strchr(name,'"');
              if (end == NULL || *trim(end+1)) fail(&line,"invalid INCLUDE path");
              *end = '\0'; }
            path = relative_path(line.file,name);
            probe = fopen(path,"r");
            for (j = 0; probe == NULL && j < p->dir_count; ++j) {
                path = join_path(p->include_dirs[j],name);
                probe = fopen(path,"r");
            }
            if (probe == NULL) fail(&line,"cannot find include '%s'",name);
            fclose(probe);
            included = read_file(path,&line);
            expand(p,&included,0,included.count,depth+1);
        } else if (same(h.op,"ENDM") || same(h.op,"ENDR") || same(h.op,"ELSE") || same(h.op,"ENDIF")) {
            fail(&line,"unexpected %s",h.op);
        } else if ((macro = find_macro(p,h.op)) != NULL) {
            char *args[MAX_ARGS];
            int count = split_args(h.rest,args,&line);
            if (count != macro->parameter_count) fail(&line,"macro %s expects %d arguments, got %d",h.op,macro->parameter_count,count);
            if (h.label != NULL) {
                size_t length = strlen(h.label)+2;
                SourceLine label = line;
                label.text = allocate(length);
                snprintf(label.text,length,"%s:",h.label);
                append_line(&p->output,label);
            }
            invoke(p,macro,args,&line,depth);
        } else {
            remember_constant(p,h,&line);
            append_line(&p->output,line);
            if (same(h.op,"END")) p->ended = 1;
        }
    }
}

Lines preprocess(const char *path, const char **include_dirs, size_t dir_count)
{
    Preprocessor state;
    Lines input;
    memset(&state,0,sizeof(state));
    state.include_dirs = include_dirs;
    state.dir_count = dir_count;
    input = read_file(path,NULL);
    expand(&state,&input,0,input.count,0);
    return state.output;
}
