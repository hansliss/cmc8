cmake_minimum_required(VERSION 3.16)
project(cmc8asm VERSION 0.1.0 LANGUAGES C)

add_executable(cmc8asm
    main.c
    common.c
    expression.c
    preprocess.c
    opcodes.c
    assemble.c
    output.c
    asm.h
)
set_target_properties(cmc8asm PROPERTIES
    C_STANDARD 99
    C_STANDARD_REQUIRED YES
    C_EXTENSIONS NO
)
if(MSVC)
    target_compile_options(cmc8asm PRIVATE /W4)
elseif(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(cmc8asm PRIVATE -Wall -Wextra -Wpedantic)
endif()

include(GNUInstallDirs)
install(TARGETS cmc8asm RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES cmc8asm.1 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)
