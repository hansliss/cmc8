#include "asm.h"
#include <ctype.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

void fail(const SourceLine *source, const char *format, ...)
{
    va_list args;
    if (source != NULL) fprintf(stderr, "%s:%u: error: ", source->file, source->line);
    else fputs("cmc8asm: error: ", stderr);
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
    if (source != NULL && source->expansion != NULL)
        fprintf(stderr, "  expanded from %s\n", source->expansion);
    exit(EXIT_FAILURE);
}

void *allocate(size_t size)
{
    void *p = calloc(1, size ? size : 1);
    if (p == NULL) fail(NULL, "out of memory");
    return p;
}

void *resize(void *memory, size_t size)
{
    void *p = realloc(memory, size ? size : 1);
    if (p == NULL) fail(NULL, "out of memory");
    return p;
}

char *copy_n(const char *text, size_t length)
{
    char *p = allocate(length + 1);
    memcpy(p, text, length);
    return p;
}

char *copy_text(const char *text) { return copy_n(text, strlen(text)); }

char *trim(char *text)
{
    char *end;
    while (isspace((unsigned char)*text)) ++text;
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) --end;
    *end = '\0';
    return text;
}

int same(const char *a, const char *b)
{
    while (*a && *b) {
        if (toupper((unsigned char)*a++) != toupper((unsigned char)*b++)) return 0;
    }
    return *a == *b;
}

int name_start(int c) { return isalpha((unsigned char)c) || c == '_' || c == '.'; }
int name_char(int c) { return isalnum((unsigned char)c) || c == '_' || c == '.'; }

char *take_name(char **cursor, const SourceLine *source)
{
    char *start = *cursor, *p = start;
    if (!name_start(*p)) fail(source, "expected a name near '%s'", p);
    while (name_char(*p)) ++p;
    if ((size_t)(p - start) > MAX_NAME) fail(source, "name exceeds %d characters", MAX_NAME);
    *cursor = p;
    return copy_n(start, (size_t)(p - start));
}

char *without_comment(const char *text)
{
    char *result = copy_text(text), *p = result;
    int quote = 0;
    for (; *p; ++p) {
        if (quote && *p == '\\' && p[1]) { ++p; continue; }
        if (quote) { if (*p == quote) quote = 0; }
        else if (*p == '\'' || *p == '"') quote = *p;
        else if (*p == ';') { *p = '\0'; break; }
    }
    return result;
}

int split_args(char *text, char **args, const SourceLine *source)
{
    char *start = trim(text), *p = start;
    int count = 0, depth = 0, quote = 0;
    if (!*start) return 0;
    for (;;) {
        int c = (unsigned char)*p;
        if (quote) {
            if (c == '\\' && p[1]) { p += 2; continue; }
            if (c == quote) quote = 0;
            if (!c) fail(source, "unterminated quoted argument");
        } else {
            if (c == '\'' || c == '"') quote = c;
            else if (c == '(') ++depth;
            else if (c == ')' && --depth < 0) fail(source, "unmatched ')'");
            else if ((!c || c == ',') && depth == 0) {
                if (count == MAX_ARGS) fail(source, "too many arguments");
                *p = '\0';
                args[count++] = trim(start);
                if (!*args[count - 1]) fail(source, "empty argument");
                if (!c) return count;
                start = p + 1;
            }
            if (!c) fail(source, "unmatched '('");
        }
        ++p;
    }
}

int escape_byte(const char **cursor, const SourceLine *source)
{
    const char *p = *cursor;
    int value = (unsigned char)*p++;
    if (value == '\\') {
        value = (unsigned char)*p++;
        switch (value) {
        case 'n': value = '\n'; break;
        case 'r': value = '\r'; break;
        case 't': value = '\t'; break;
        case '0': value = 0; break;
        case '\\': case '\'': case '"': break;
        case 'x': {
            int i;
            value = 0;
            for (i = 0; i < 2; ++i) {
                int digit = (unsigned char)*p++;
                if (!isxdigit(digit)) fail(source, "\\x requires exactly two hex digits");
                value = value * 16 + (isdigit(digit) ? digit - '0' : toupper(digit) - 'A' + 10);
            }
            break;
        }
        default: fail(source, "unknown string escape");
        }
    }
    *cursor = p;
    return value;
}

void append_line(Lines *lines, SourceLine line)
{
    if (lines->count >= MAX_EXPANSION) fail(&line, "expanded source exceeds %d lines", MAX_EXPANSION);
    if (lines->count == lines->capacity) {
        lines->capacity = lines->capacity ? lines->capacity * 2 : 128;
        lines->items = resize(lines->items, lines->capacity * sizeof(*lines->items));
    }
    lines->items[lines->count++] = line;
}
