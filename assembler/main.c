#include "asm.h"
#include <stdlib.h>
#include <string.h>

static void usage(FILE *output)
{
    fputs("cmc8asm 0.1.0 -- absolute CMC8 macro assembler (portable C99)\n"
          "Usage: cmc8asm [options] source.asm\n"
          "  -o FILE          Output path; '-' writes text to standard output\n"
          "  -f ihex|bin      Intel HEX (default) or flat 1024-byte image\n"
          "  -l FILE          Expanded-source listing\n"
          "  -m FILE          Absolute symbol map\n"
          "  -I DIRECTORY     Additional include search directory (repeatable)\n"
          "  --fill NUMBER    Binary gap-fill byte (default 0, NOP)\n"
          "  -q               Omit the success summary\n"
          "  -h, --help       Show this help\n"
          "  --version        Show the application version\n",output);
}

static const char *option_value(int argc, char **argv, int *index)
{
    if (++*index >= argc) fail(NULL,"missing value for '%s'",argv[*index-1]);
    return argv[*index];
}

static char *default_output(const char *input, int binary)
{
    const char *p, *dot = NULL;
    char *name;
    size_t length;
    for (p = input; *p; ++p) {
        if (*p == '/' || *p == '\\') dot = NULL;
        else if (*p == '.') dot = p;
    }
    length = dot != NULL ? (size_t)(dot-input) : strlen(input);
    name = allocate(length+5);
    memcpy(name,input,length);
    strcpy(name+length,binary ? ".bin" : ".hex");
    return name;
}

/* Lexical comparison catches ./ and ../ aliases without POSIX realpath().
   Symlinks/hard links are outside this portable filename-only check. */
static char *normalized_path(const char *path)
{
    char *copy = copy_text(path), **parts = allocate((strlen(path)+1)*sizeof(char *));
    char *p = copy, *start, *result = allocate(strlen(path)+3);
    size_t count = 0, length = 0, i;
    int absolute;
    for (; *p; ++p) if (*p == '\\') *p = '/';
    absolute = copy[0] == '/';
    p = copy;
    while (*p) {
        while (*p == '/') ++p;
        if (!*p) break;
        start = p;
        while (*p && *p != '/') ++p;
        if (*p) *p++ = '\0';
        if (strcmp(start,".") == 0) continue;
        if (strcmp(start,"..") == 0 && count && strcmp(parts[count-1],"..") != 0 &&
            strchr(parts[count-1],':') == NULL) --count;
        else if (strcmp(start,"..") != 0 || !absolute) parts[count++] = start;
    }
    if (absolute) result[length++] = '/';
    for (i = 0; i < count; ++i) {
        size_t n = strlen(parts[i]);
        if (length && result[length-1] != '/') result[length++] = '/';
        memcpy(result+length,parts[i],n);
        length += n;
    }
    if (!length) result[length++] = '.';
    result[length] = '\0';
    free(parts);
    free(copy);
    return result;
}

static int equal_path(const char *a, const char *b)
{
    char *left = normalized_path(a), *right = normalized_path(b);
#ifdef _WIN32
    int equal = same(left,right);
#else
    int equal = strcmp(left,right) == 0;
#endif
    free(left);
    free(right);
    return equal;
}

static FILE *open_output(const char *path, const char *mode)
{
    FILE *output;
    if (strcmp(path,"-") == 0) return stdout;
    output = fopen(path,mode);
    if (output == NULL) fail(NULL,"cannot create output '%s'",path);
    return output;
}

static void close_output(FILE *output, const char *path)
{
    int error = ferror(output);
    if (output == stdout) error |= fflush(output) == EOF;
    else error |= fclose(output) == EOF;
    if (error) fail(NULL,"error writing '%s'",path);
}

int main(int argc, char **argv)
{
    const char *input = NULL, *output = NULL, *listing = NULL, *map = NULL;
    const char **include_dirs = allocate((size_t)argc*sizeof(*include_dirs));
    size_t dir_count = 0;
    int binary = 0, quiet = 0, i;
    unsigned fill = 0;
    Lines lines;
    Assembly result;
    FILE *file;
    memset(&result,0,sizeof(result));
    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (strcmp(arg,"-h") == 0 || strcmp(arg,"--help") == 0) { usage(stdout); return EXIT_SUCCESS; }
        if (strcmp(arg,"--version") == 0) { puts("cmc8asm 0.1.0"); return EXIT_SUCCESS; }
        if (strcmp(arg,"-o") == 0) output = option_value(argc,argv,&i);
        else if (strcmp(arg,"-l") == 0) listing = option_value(argc,argv,&i);
        else if (strcmp(arg,"-m") == 0) map = option_value(argc,argv,&i);
        else if (strcmp(arg,"-I") == 0) include_dirs[dir_count++] = option_value(argc,argv,&i);
        else if (strncmp(arg,"-I",2) == 0 && arg[2]) include_dirs[dir_count++] = arg+2;
        else if (strcmp(arg,"-q") == 0) quiet = 1;
        else if (strcmp(arg,"-f") == 0) {
            const char *format = option_value(argc,argv,&i);
            if (same(format,"bin")) binary = 1;
            else if (same(format,"ihex") || same(format,"hex")) binary = 0;
            else fail(NULL,"unknown output format '%s'",format);
        } else if (strcmp(arg,"--fill") == 0) {
            Expression context = {NULL,NULL,-1,0,NULL};
            Value value = expression(option_value(argc,argv,&i),&context);
            if (!value.known || value.number < 0 || value.number > 255) fail(NULL,"fill byte must be 0..255");
            fill = (unsigned)value.number;
        } else if (arg[0] == '-') fail(NULL,"unknown option '%s'",arg);
        else if (input != NULL) fail(NULL,"one source file is required; use INCLUDE for additional files");
        else input = arg;
    }
    if (input == NULL) { usage(stderr); return EXIT_FAILURE; }
    if (output == NULL) output = default_output(input,binary);
    if (binary && strcmp(output,"-") == 0)
        fail(NULL,"portable binary output requires a file; use Intel HEX for stdout");
    {
        const char *paths[3] = {output,listing,map};
        int a,b;
        for (a = 0; a < 3; ++a) if (paths[a] != NULL) {
            if (equal_path(paths[a],input)) fail(NULL,"output would overwrite the source file");
            for (b = 0; b < a; ++b)
                if (paths[b] != NULL && equal_path(paths[a],paths[b])) fail(NULL,"output paths must be distinct");
        }
    }
    lines = preprocess(input,include_dirs,dir_count);
    {
        const char *paths[3] = {output,listing,map};
        size_t line;
        int index;
        for (index = 0; index < 3; ++index) if (paths[index] != NULL)
            for (line = 0; line < lines.count; ++line)
                if (equal_path(paths[index],lines.items[line].file))
                    fail(NULL,"output would overwrite source '%s'",lines.items[line].file);
    }
    if (listing != NULL) {
        result.listing = tmpfile();
        if (result.listing == NULL) fail(NULL,"cannot create temporary listing stream");
    }
    /* No requested output file is opened until both assembly passes succeed. */
    assemble(&result,&lines);
    file = open_output(output,binary ? "wb" : "w");
    if (binary) write_binary(file,&result,fill);
    else write_hex(file,&result);
    close_output(file,output);
    if (map != NULL) {
        file = open_output(map,"w");
        write_symbols(file,&result);
        close_output(file,map);
    }
    if (listing != NULL) {
        int c;
        file = open_output(listing,"w");
        rewind(result.listing);
        while ((c = fgetc(result.listing)) != EOF) fputc(c,file);
        if (ferror(result.listing)) fail(NULL,"error reading temporary listing");
        fclose(result.listing);
        close_output(file,listing);
    }
    if (!quiet) fprintf(stderr,"Assembled %u bytes, %zu symbols -> %s\n",result.emitted,result.symbol_count,output);
    return EXIT_SUCCESS;
}
