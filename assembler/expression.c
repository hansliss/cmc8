#include "asm.h"
#include <ctype.h>
#include <inttypes.h>
#include <limits.h>
#include <string.h>

/* A precedence-climbing parser. Address provenance survives label+offset;
   LOW/HIGH and bit operations deliberately produce ordinary scalar values. */
typedef struct { const char *p; Expression *context; unsigned depth; } Parser;

typedef struct { const char *text; int precedence; } Operator;
static const Operator operators[] = {
    {"||",1}, {"&&",2}, {"|",3}, {"^",4}, {"&",5},
    {"==",6}, {"!=",6}, {"<=",7}, {">=",7}, {"<",7}, {">",7},
    {"<<",8}, {">>",8}, {"+",9}, {"-",9}, {"*",10}, {"/",10}, {"%",10}
};

Value constant(int64_t number)
{
    Value result = {0,1,0};
    result.number = number;
    return result;
}

static void skip(Parser *p) { while (isspace((unsigned char)*p->p)) ++p->p; }
static Value parse(Parser *p, int minimum);

static Value number(Parser *p)
{
    const char *start = p->p, *end, *digits;
    int base = 10;
    uint64_t value = 0;
    if (*p->p == '$') { base = 16; ++p->p; }
    else if (*p->p == '%') { base = 2; ++p->p; }
    else if (p->p[0] == '0' && strchr("xXoObB", p->p[1]) != NULL && p->p[1]) {
        int prefix = toupper((unsigned char)p->p[1]);
        base = prefix == 'X' ? 16 : prefix == 'O' ? 8 : 2;
        p->p += 2;
    }
    digits = p->p;
    while (isalnum((unsigned char)*p->p)) ++p->p;
    end = p->p;
    if (base == 10 && end > digits && strchr("oOhH", end[-1]) != NULL) {
        base = toupper((unsigned char)end[-1]) == 'O' ? 8 : 16;
        --end;
    }
    if (digits == end) fail(p->context->source, "expected digits near '%s'", start);
    for (; digits < end; ++digits) {
        int c = toupper((unsigned char)*digits);
        int digit = isdigit(c) ? c - '0' : c - 'A' + 10;
        if (digit < 0 || digit >= base) fail(p->context->source, "invalid base-%d number near '%s'", base, start);
        if (value > ((uint64_t)INT64_MAX - (unsigned)digit) / (unsigned)base)
            fail(p->context->source, "integer constant overflow");
        value = value * (unsigned)base + (unsigned)digit;
    }
    return constant((int64_t)value);
}

static Value primary(Parser *p);

static Value primary_impl(Parser *p)
{
    Value result;
    char name[MAX_NAME + 1];
    size_t length = 0;
    int unary;
    skip(p);
    unary = (unsigned char)*p->p;
    if (strchr("+-~!<>", unary) != NULL && unary) {
        ++p->p;
        result = primary(p);
        if (!result.known) return result;
        if (unary == '-') {
            if (result.number == INT64_MIN) fail(p->context->source, "negation overflow");
            result.number = -result.number;
        } else if (unary == '~') result.number = ~result.number;
        else if (unary == '!') result.number = !result.number;
        else if (unary == '<') result.number = (int64_t)((uint64_t)result.number & 255);
        else if (unary == '>') result.number = (int64_t)(((uint64_t)result.number >> 8) & 255);
        if (unary == '~' || unary == '!' || unary == '<' || unary == '>') result.address = 0;
        return result;
    }
    if (*p->p == '(') {
        ++p->p;
        result = parse(p, 1);
        skip(p);
        if (*p->p++ != ')') fail(p->context->source, "expected ')' in expression");
        return result;
    }
    if (*p->p == '\'') {
        ++p->p;
        if (!*p->p || *p->p == '\'') fail(p->context->source, "empty character literal");
        result = constant(escape_byte(&p->p, p->context->source));
        if (*p->p++ != '\'') fail(p->context->source, "character literal must contain one byte");
        return result;
    }
    if (*p->p == '*' || (*p->p == '$' && !isxdigit((unsigned char)p->p[1]))) {
        ++p->p;
        result = constant(p->context->pc);
        result.known = p->context->pc >= 0;
        result.address = 1;
        return result;
    }
    if (isdigit((unsigned char)*p->p) || *p->p == '$' || *p->p == '%') return number(p);
    if (!name_start(*p->p)) fail(p->context->source, "expected expression near '%s'", p->p);
    while (name_char(*p->p)) {
        if (length == MAX_NAME) fail(p->context->source, "expression name too long");
        name[length++] = *p->p++;
    }
    name[length] = '\0';
    skip(p);
    if (*p->p == '(') {
        ++p->p;
        result = parse(p, 1);
        skip(p);
        if (*p->p++ != ')') fail(p->context->source, "expected ')' after %s", name);
        if (!(same(name,"LOW") || same(name,"HIGH") || same(name,"PAGEOF")))
            fail(p->context->source, "unknown expression function '%s'", name);
        if (result.known) {
            if (same(name,"LOW")) result.number = (int64_t)((uint64_t)result.number & 255);
            else if (same(name,"HIGH")) result.number = (int64_t)(((uint64_t)result.number >> 8) & 255);
            else {
                if (result.number < 0 || result.number >= IMAGE_SIZE)
                    fail(p->context->source, "PAGEOF needs an address in 0..1023");
                result.number >>= 8;
            }
        }
        result.address = 0;
        return result;
    }
    result = p->context->lookup != NULL ? p->context->lookup(p->context->user, name) : (Value){0,0,0};
    if (!result.known && !p->context->allow_unknown)
        fail(p->context->source, "undefined symbol '%s'", name);
    return result;
}

static Value primary(Parser *p)
{
    Value result;
    if (++p->depth > 128) fail(p->context->source,"expression nesting exceeds 128");
    result = primary_impl(p);
    --p->depth;
    return result;
}

static Value calculate(Parser *p, const char *op, Value a, Value b)
{
    int64_t x = a.number, y = b.number, result = 0;
    Value value = {0,0,0};
    if (!a.known || !b.known) return value;
    if (strcmp(op,"+") == 0) {
        if ((y > 0 && x > INT64_MAX-y) || (y < 0 && x < INT64_MIN-y)) goto overflow;
        result = x+y;
        value.address = a.address || b.address;
    } else if (strcmp(op,"-") == 0) {
        if ((y < 0 && x > INT64_MAX+y) || (y > 0 && x < INT64_MIN+y)) goto overflow;
        result = x-y;
        value.address = a.address != b.address;
    } else if (strcmp(op,"*") == 0) {
        if (x && y && ((x == -1 && y == INT64_MIN) || (y == -1 && x == INT64_MIN) ||
            (x > 0 ? (y > 0 ? x > INT64_MAX/y : y < INT64_MIN/x) :
                      (y > 0 ? x < INT64_MIN/y : x < INT64_MAX/y)))) goto overflow;
        result = x*y;
        value.address = a.address || b.address;
    } else if (strcmp(op,"/") == 0 || strcmp(op,"%") == 0) {
        if (!y) fail(p->context->source, "division by zero");
        if (x == INT64_MIN && y == -1) goto overflow;
        result = *op == '/' ? x/y : x%y;
        value.address = a.address || b.address;
    } else if (strcmp(op,"<<") == 0 || strcmp(op,">>") == 0) {
        if (x < 0 || y < 0 || y > 62) fail(p->context->source, "shifts need a nonnegative value and count 0..62");
        if (*op == '<') {
            if (x > (INT64_MAX >> y)) goto overflow;
            result = x << y;
        } else result = x >> y;
    } else if (strcmp(op,"&") == 0) result = x&y;
    else if (strcmp(op,"|") == 0) result = x|y;
    else if (strcmp(op,"^") == 0) result = x^y;
    else if (strcmp(op,"&&") == 0) result = x && y;
    else if (strcmp(op,"||") == 0) result = x || y;
    else if (strcmp(op,"==") == 0) result = x == y;
    else if (strcmp(op,"!=") == 0) result = x != y;
    else if (strcmp(op,"<=") == 0) result = x <= y;
    else if (strcmp(op,">=") == 0) result = x >= y;
    else if (strcmp(op,"<") == 0) result = x < y;
    else if (strcmp(op,">") == 0) result = x > y;
    value.number = result;
    value.known = 1;
    return value;
overflow:
    fail(p->context->source, "integer expression overflow");
    return value;
}

static const Operator *next_operator(const char *text)
{
    const Operator *best = NULL;
    size_t i, longest = 0;
    for (i = 0; i < sizeof(operators)/sizeof(operators[0]); ++i) {
        size_t length = strlen(operators[i].text);
        if (length > longest && strncmp(text, operators[i].text, length) == 0) {
            best = &operators[i];
            longest = length;
        }
    }
    return best;
}

static Value parse(Parser *p, int minimum)
{
    Value left = primary(p);
    for (;;) {
        const Operator *op;
        Value right;
        skip(p);
        op = next_operator(p->p);
        if (op == NULL || op->precedence < minimum) return left;
        p->p += strlen(op->text);
        right = parse(p, op->precedence + 1);
        left = calculate(p, op->text, left, right);
    }
}

Value expression(const char *text, Expression *context)
{
    Parser parser = {text, context, 0};
    Value result = parse(&parser, 1);
    skip(&parser);
    if (*parser.p) fail(context->source, "unexpected text in expression: '%s'", parser.p);
    return result;
}
