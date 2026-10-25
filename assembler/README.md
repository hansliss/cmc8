# cmc8asm 0.1.0

A standalone **portable C99 macro assembler** for the ASEA-HAFO CMC8.
It supports all 43 instruction families / 239 encodings, absolute 10-bit
addresses, four 256-byte pages, parameterized macros and sparse Intel HEX
or flat binary output. There is no linker or relocation format.

Copying this directory is sufficient to build and use the application.
Python, the processor simulator and the book data files are not runtime
or build dependencies.

## Build and run

```sh
cmake -S . -B build
cmake --build build
./build/cmc8asm examples/macros.asm -o /tmp/macros.hex -l /tmp/macros.lst -m /tmp/macros.map
./build/cmc8asm examples/paging.asm -f bin -o /tmp/paging.bin
```

CMake 3.16 or later and a C99 compiler are required. With multi-configuration
generators, select a configuration using `--config Release`; the executable
will be in `build/Release/`.

Install the executable and manpage with:

```sh
cmake --install build --prefix "$HOME/.local"
man -l cmc8asm.1
```

The installed manual is available as `man cmc8asm` when the install prefix
is on your system's manual search path. The [manpage](cmc8asm.1) documents
the command line, source syntax, directives, macros and paging rules.

Without CMake, compile the seven source files directly:

```sh
cc -std=c99 -O2 -Wall -Wextra -Wpedantic main.c common.c expression.c preprocess.c opcodes.c assemble.c output.c -o cmc8asm
```

This uses only ISO C99 headers and library functions, including fixed-width
integers. No POSIX APIs or third-party libraries are used. The build has
been checked with GCC; other host compilers/platforms have not been tested
in this environment. A modern Windows C compiler can build the same sources;
file output uses binary mode where required.

```text
cmc8asm [options] source.asm
  -o FILE          output; default source basename with .hex or .bin
  -f ihex|bin      sparse Intel HEX (default) or full 1024-byte image
  -l FILE          expanded-source listing, including macro call locations
  -m FILE          sorted absolute symbol map
  -I DIRECTORY     include search directory; repeatable; -Idir also accepted
  --fill NUMBER    binary gap-fill byte; default 0 (NOP)
  -q               suppress the success summary
  -h, --help       usage
  --version        application version
```

Use `-o -` for Intel HEX on standard output. Binary output requires a file,
keeping its byte handling portable across C host runtimes. Listing/map output
can also use `-`, provided output paths remain distinct. Diagnostics and the
success summary use standard error; errors return a nonzero exit code.

## Source syntax

Names, instructions and directives are case-insensitive. Names may contain
letters, digits, `_` and `.`, and must start with a letter, `_` or `.`.
A label has a colon; constants use `NAME EQU expression`, `NAME = expression`,
`EQU NAME,expression` or `NAME: EQU expression`. Labels refer to the location
before the operation on that line; put labels after PAGE/ORG directives.
Semicolons start comments outside quoted strings.

```asm
PORT EQU 4

PAGE 0
ORG 0
start:  LRI R3,#044o
        SRD R3,PORT
        JMP start
```

Registers are `R0`…`R7`, with `X` accepted for R7. Numeric selector expressions
are also accepted. TEST selectors are `T0`…`T3` or numbers 0…3. There is no
fixed `PC` register alias: the processor's PC is the register selected by N.

Numbers are decimal by default, **including leading-zero numbers**. Use
`172o` or `0o172` for octal, `0x7A`, `$7A` or `7Ah` for hexadecimal, and
`0b1010` or `%1010` for binary. A single quoted character such as `'A'` is
a byte value. Immediates may have `#`; it is optional.

Expressions support parentheses, unary `+ - ~ ! < >`, and binary
`* / % + - << >> < <= > >= == != & ^ | && ||`, with conventional precedence
and left associativity. Unary `<` and `>` mean low/high byte. Division
truncates toward zero; shifts require a nonnegative value and count 0…62.
Arithmetic overflow and division by zero are errors. Expressions are eager,
not short-circuit evaluated.

`LOW(expr)` extracts bits 0…7, `HIGH(expr)` bits 8…15, and `PAGEOF(expr)` the
page of an address 0…1023. `$` by itself, or `*` where a value is expected,
is the full current location. Thus `$20` is hex20, while `LOW($)` is the
current offset. Labels and forward EQU chains resolve before byte emission;
PAGE, ORG, ORGA, FILL and RES sizes must already be known in the first pass.

## Paging

A label is an absolute program-image address:

```text
full_address = page × 256 + offset
page0: 000h…0FFh    page1: 100h…1FFh
page2: 200h…2FFh    page3: 300h…3FFh
```

`PAGE n` selects the assembly page. Each page has its own saved location
counter, initially 0, so returning to a page resumes where assembly left it.
`ORG offset` sets that page's offset 0…255. `ORGA address` selects the page
and offset from a full absolute address 0…1023. Neither directive emits code
or changes the processor's hardware PG register.

```asm
PAGE 0
ORG 0
        JMP worker          ; Assembles JMP3,020o automatically.

PAGE 3
ORG 020o
worker: LRI R3,#0x69
        JMP worker
```

For `JMP`, `BZ0/BZ1` and `BL0/BL1`, a label supplies both the encoded page
and operand byte. `JMP 3,worker` is also accepted and checks that the page
agrees with the label. A raw numeric target 0…255 denotes an offset in the
current assembly page; a numeric target 256…1023 is a full address. To name
page0 explicitly from elsewhere, use a page0 label or `JMP 0,offset`.

For `JSR`, `BB0/BB1`, `BT0/BT1` and the ordinary program/storage-memory
loads/stores, symbolic/full targets must lie on the current page: these
instructions cannot encode a page change. Numeric offsets remain usable.
`LOW(label)` deliberately discards page information if you need the raw byte;
that override is explicit. I/O ports and immediate values must fit in a byte.

Arithmetic with one address preserves address provenance; the difference
of two addresses is a scalar. Extraction and bit operations also produce scalars. Consequently
a page0 label cannot accidentally become a raw offset merely because its
numeric value happens to be below 256.

JSR and RSR do not save/restore PG. A cross-page call therefore needs an
explicit convention. [The paging example](examples/paging.asm) uses a
same-page JSR trampoline, a JMP to the other page, and a JMP back to a
same-page return stub before RSR. Its assembled code is tested on the
processor simulator; no page-stack mechanism is invented by the assembler.

### End-of-page wrapping

Assembly never silently continues into the next page. A final byte at 255
is legal, but further emission requires repositioning. A two-byte instruction
at 255 is rejected unless you explicitly enable the CPU's wrap behavior:

```asm
PAGE 3
WRAP ON
ORG 255
entry:  LRI R3,#42           ; Opcode at3FFh, operand at300h.
        JMP entry           ; Starts at301h.
WRAP OFF
```

WRAP applies to emitted blocks within the current page. One block cannot
exceed 256 bytes. Overlapping emitted **or reserved** locations are errors,
including overlaps caused by wrapping. WRAP is initially OFF and remains
in effect across PAGE selections until changed.

The page/origin distinction follows the familiar bank+origin organization
used by [WLA-DX](https://wla-dx.readthedocs.io/en/latest/asmdiv.html), adapted
to CMC8's shared PG and eight-bit PC. This tool is its own small dialect,
not a compatibility mode for WLA-DX or another assembler.

## Instructions

| Form | Instructions |
| --- | --- |
| No operands | NOP, EIN, DIN, SEL, REL, SEZ, REZ, RSR |
| `op Rn` | CPY, INR, DCR, AND, XOR, EXR, ROR, SHR, RRL, JCR, LRX, LSX, SRX, SSX |
| `op Rn,#byte` | LRI, XRI, ANI |
| `op Rn,address` | LRM, LRS, SRM, SRS |
| `op Rn,port` | LRD, SRD |
| `op Rn,target` | BB0, BB1 |
| `op Tn,target` | BT0, BT1 |
| `op target` or `op page,target` | JMP, BZ0, BZ1, BL0, BL1 |
| `JSR target` | Same-page subroutine call |
| `op #byte` | SCS, SCW |

AND/XOR write X, CPY copies its selected register to X, and EXR exchanges
with X: the assembly operands follow the actual one-register encodings.
The assembler does not substitute additional register moves or change
instruction semantics.

## Macros, includes and conditional assembly

```asm
MACRO COUNTDOWN count
        LRI R4,#\count
%%loop: DCR R4
        BZ0 %%loop
ENDM

        COUNTDOWN 3
        COUNTDOWN 7
```

Parameters use `\name` or positional `\1`, `\2`, etc. Expansion is textual:
parenthesize parameters in a macro expression when precedence matters.
`%%name` becomes a unique label for each invocation. `\@` produces the
invocation number, useful for constructed names. The `__M` namespace is
reserved for generated local names. Macro calls may have a leading label,
and macros may invoke other macros. Definitions must precede their calls;
nested macro definitions are not supported.

Substitution does not occur inside quoted strings or character literals.
Pass a quoted string as a parameter and use `BYTE \parameter` to emit it.
Comments are not part of the assembly text, although listings retain source
comments. Macro names cannot replace an instruction or directive.

`INCLUDE "file.inc"` searches relative to the source/definition file first,
then the `-I` directories. Included files can contain definitions or code.
[The I/O include](examples/io.inc) demonstrates an include guard and OUT macro.

```asm
COUNT EQU 3
IF COUNT == 3
    REPT COUNT
        NOP
    ENDR
ELSE
    ERROR "unexpected configuration"
ENDIF
```

`IF`, `ELSE`, `ENDIF`, `IFDEF`, `IFNDEF` and `REPT` are preprocessing
operations. Conditions/counts can use numeric expressions, substituted macro
arguments and previously known numeric EQU constants; they cannot depend on
assembly addresses or forward definitions. IFDEF/IFNDEF test known numeric
constants and macro definitions. Skipped branches do not open include files.
`%%` names also receive unique IDs in a standalone REPT body; inside a macro,
its local names belong to that macro invocation, so use a helper macro for
fresh labels on each nested repetition.

Directives may have a leading dot. Named macros and symbols retain their
actual spelling, including any leading dot.

## Data and checks

| Directive | Effect |
| --- | --- |
| `BYTE` / `DB` / `ASCII` | Bytes and quoted strings |
| `WORD` / `DW` | Unsigned 16-bit words, little-endian; a data convention, not a CPU instruction |
| `RES count` | Reserve locations without HEX output |
| `FILL count[,value]` | Emit repeated bytes; value defaults to0 |
| `RES count,value` | Reserve and initialize those locations |
| `ASSERT expr[,"message"]` | Check an expression after symbol resolution |
| `ERROR "message"` | Stop with an error |
| `END` | End the translation unit, including further preprocessing |

Strings and characters accept `\n`, `\r`, `\t`, `\0`, `\\`, `\'`, `\"` and
`\xHH` (exactly two hex digits). A character literal contains one byte.

The output image is program memory. Storage-memory variables or device
addresses can be named with EQU constants; no separate initialized storage
image or relocation records are emitted. Uninitialized RES locations still
participate in overlap checks.

## Output format

Intel HEX output uses absolute addresses0000h…03FFh, data records of at most
16 bytes and a final EOF record. Only explicitly initialized bytes are
written; holes remain absent. Checksums follow the standard
[Intel HEX format](https://www.keil.com/support/docs/1584/default.htm).
No extended-address or relocation records are necessary.

Binary output is always 1024 bytes. Byte `page*256+offset` holds that program
cell. Holes, including uninitialized RES ranges, use `--fill` (default 00).
For example, an optional Python simulator consumer can load a binary image
with `Memory(program=dict(enumerate(Path("program.bin").read_bytes())))`.
That consumer is not needed to assemble a program.

Output files are opened only after assembly succeeds, so source errors do
not overwrite a previous result. Paths are checked for lexical collisions
with source/include files and other outputs. Listings show page:octal-offset
addresses, hex bytes, source locations and macro call context. Symbol maps
include resolved EQU values and absolute label addresses. No entry-point
record is emitted; the CPU's reset entry is page0, offset 0.

## Implementation and validation

- `preprocess.c`: source loading, includes, macros, local names and conditions.
- `expression.c`: checked integer expressions and address provenance.
- `opcodes.c`: the complete instruction encoding table.
- `assemble.c`: symbol resolution, page-aware checks and byte emission.
- `output.c`: Intel HEX, binary and symbol maps.
- `main.c`, `common.c`, `asm.h`: application interface and shared utilities.

Forward EQU chains resolve recursively between the two assembly passes.
Source/expansion metadata has translation-unit lifetime; this is a batch
application rather than a library with reusable assembler sessions.
Limits are 4095 bytes per physical source line, 65535 per expanded line,
100,000 expanded lines/invocations, 32 levels of preprocessing nesting,
128 levels of expression/EQU nesting, 64 operands/parameters, and 10,000 REPT
iterations. UTF-8 BOMs and CRLF line endings are accepted.

In the research repository, run `python3 -m unittest tests.test_macro_assembler`.
The 20 assembler tests build the C application through CMake with strict warnings and independently
check all 239 opcode variants, the book traffic program, macros/includes,
expressions, page rules, wrapping, diagnostics and formats. The traffic
source assembles to all 75 literal bytes. Wrapping and a cross-page call
trampoline are also executed on the existing processor simulator.

Strict C99 warning checks and address/undefined-behavior sanitizer runs also
pass, along with 1,000 independently evaluated random expression cases.

The complete repository suite has **363 passing tests** for this pass. A
copy of this directory was also built and run outside the repository,
confirming that the application and its included examples stand alone.
