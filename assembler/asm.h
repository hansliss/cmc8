#ifndef CMC8_ASM_H
#define CMC8_ASM_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define IMAGE_SIZE 1024
#define PAGE_SIZE 256
#define MAX_ARGS 64
#define MAX_NAME 127
#define MAX_EXPANSION 100000

typedef struct {
    char *text;
    char *file;
    unsigned line;
    char *expansion;              /* Definition/call context for macro errors. */
} SourceLine;

typedef struct {
    SourceLine *items;
    size_t count, capacity;
} Lines;

typedef struct {
    int64_t number;
    int known;
    int address;                  /* A label/address, rather than a raw offset. */
} Value;

typedef struct {
    void *user;
    Value (*lookup)(void *user, const char *name);
    int64_t pc;
    int allow_unknown;
    const SourceLine *source;
} Expression;

typedef enum {
    OP_NONE, OP_REG, OP_IMMEDIATE, OP_MEMORY, OP_PORT,
    OP_BIT_BRANCH, OP_TEST_BRANCH, OP_PAGE_BRANCH, OP_CALL, OP_CONTROL
} OperandKind;

typedef struct {
    const char *name;
    unsigned opcode, length;
    OperandKind kind;
} Instruction;

typedef struct {
    char *name;
    Value value;
    char *equation;
    int64_t equation_pc;
    const SourceLine *source;
    int resolving;
} Symbol;

typedef struct {
    unsigned char image[IMAGE_SIZE];
    unsigned char used[IMAGE_SIZE];
    unsigned char claimed[IMAGE_SIZE];
    Symbol *symbols;
    size_t symbol_count, symbol_capacity;
    FILE *listing;
    unsigned emitted;
} Assembly;

void *allocate(size_t size);
void *resize(void *memory, size_t size);
char *copy_text(const char *text);
char *copy_n(const char *text, size_t length);
char *trim(char *text);
int same(const char *a, const char *b);
int name_start(int c);
int name_char(int c);
char *take_name(char **cursor, const SourceLine *source);
char *without_comment(const char *text);
int split_args(char *text, char **args, const SourceLine *source);
int escape_byte(const char **cursor, const SourceLine *source);
void append_line(Lines *lines, SourceLine line);
void fail(const SourceLine *source, const char *format, ...);

Value expression(const char *text, Expression *context);
Value constant(int64_t number);
const Instruction *instruction(const char *name);

Lines preprocess(const char *path, const char **include_dirs, size_t dir_count);
void assemble(Assembly *result, const Lines *lines);
void write_hex(FILE *output, const Assembly *result);
void write_binary(FILE *output, const Assembly *result, unsigned fill);
void write_symbols(FILE *output, Assembly *result);

#endif
