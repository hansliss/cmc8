#include "asm.h"
#include <ctype.h>
#include <inttypes.h>
#include <stdlib.h>

void write_hex(FILE *output, const Assembly *result)
{
    unsigned address = 0;
    while (address < IMAGE_SIZE) {
        unsigned start, count = 0, checksum, i;
        while (address < IMAGE_SIZE && !result->used[address]) ++address;
        if (address == IMAGE_SIZE) break;
        start = address;
        while (address < IMAGE_SIZE && result->used[address] && count < 16 &&
               (address >> 8) == (start >> 8)) { ++address; ++count; }
        checksum = count + (start >> 8) + (start & 255);
        fprintf(output,":%02X%04X00",count,start);
        for (i = 0; i < count; ++i) {
            unsigned byte = result->image[start+i];
            checksum += byte;
            fprintf(output,"%02X",byte);
        }
        fprintf(output,"%02X\n",(0u-checksum)&255);
    }
    fputs(":00000001FF\n",output);
}

void write_binary(FILE *output, const Assembly *result, unsigned fill)
{
    unsigned address;
    for (address = 0; address < IMAGE_SIZE; ++address)
        fputc(result->used[address] ? result->image[address] : (int)fill,output);
}

static int compare_symbols(const void *left, const void *right)
{
    const unsigned char *a = (const unsigned char *)((const Symbol *)left)->name;
    const unsigned char *b = (const unsigned char *)((const Symbol *)right)->name;
    while (*a && *b && toupper(*a) == toupper(*b)) { ++a; ++b; }
    return toupper(*a)-toupper(*b);
}

void write_symbols(FILE *output, Assembly *result)
{
    size_t i;
    if (result->symbol_count > 1)
        qsort(result->symbols,result->symbol_count,sizeof(*result->symbols),compare_symbols);
    fputs("; Absolute symbols: name, decimal value, page:octal offset when an address, definition\n",output);
    for (i = 0; i < result->symbol_count; ++i) {
        const Symbol *symbol = &result->symbols[i];
        fprintf(output,"%-28s %12" PRId64 " ",symbol->name,symbol->value.number);
        if (symbol->value.address && symbol->value.number >= 0 && symbol->value.number < IMAGE_SIZE)
            fprintf(output,"%d:%03o ",(int)(symbol->value.number >> 8),(unsigned)symbol->value.number&255);
        else fputs("      ",output);
        fprintf(output,"%s:%u\n",symbol->source->file,symbol->source->line);
    }
}
