cmake_minimum_required(VERSION 3.20)
option(X7_HOST_TESTS "Build native tests and screenshot/trace tools" OFF)
set(X7_SDK "${CMAKE_CURRENT_LIST_DIR}/../x7_app_sdk" CACHE PATH "X7 starter SDK directory")
get_filename_component(X7_SDK "${X7_SDK}" ABSOLUTE)
if(NOT EXISTS "${X7_SDK}/sdk/platform/crt.c")
    message(FATAL_ERROR "Set X7_SDK to the supplied X7 SDK")
endif()
if(NOT X7_HOST_TESTS AND NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    set(CMAKE_TOOLCHAIN_FILE "${X7_SDK}/cmake/x7-mips-toolchain.cmake" CACHE FILEPATH "X7 compiler")
endif()
project(cmc8_x7_midahs LANGUAGES C ASM)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(X7_APP_ID "midahs")
set(X7_APP_TITLE "Midahs")
option(X7_DEBUG_LOG "Enable bounded platform logging" OFF)
set(GENERATED "${CMAKE_CURRENT_BINARY_DIR}/generated")
file(MAKE_DIRECTORY "${GENERATED}")
configure_file("${X7_SDK}/app/paths.h.in" "${GENERATED}/paths.h" @ONLY)
configure_file("${X7_SDK}/app/app.desktop.in" "${GENERATED}/${X7_APP_ID}.desktop" @ONLY)
set(PORTABLE core/midahs.c core/panel.c app/demo.c)
set(APP_INCLUDES app core "${GENERATED}" "${X7_SDK}" "${X7_SDK}/app")
if(X7_HOST_TESTS)
    enable_testing()
    add_executable(test-midahs ${PORTABLE} tests/test.c)
    add_executable(midahs-host ${PORTABLE} tests/host.c)
    add_executable(test-assets ${PORTABLE} app/assets.c tests/assets.c)
    target_compile_definitions(test-assets PRIVATE X7_HOST_TEST=1)
    add_test(NAME assets COMMAND test-assets)
    add_executable(test-platform ${PORTABLE} app/platform.c app/assets.c tests/platform.c
        "${X7_SDK}/app/audio.c" "${X7_SDK}/sdk/platform/timing.c"
        "${X7_SDK}/sdk/platform/fb_video.c" "${X7_SDK}/sdk/common/volume.c")
    target_compile_definitions(test-platform PRIVATE X7_HOST_TEST=1 X7_SHARED_VOLUME=1
        X7_DEBUG_LOG=0 X7_ENABLE_AUDIO=0)
    foreach(scenario RANGE 0 7)
        add_test(NAME platform-${scenario} COMMAND test-platform ${scenario})
    endforeach()
    foreach(target test-midahs midahs-host test-platform test-assets)
        target_include_directories(${target} PRIVATE ${APP_INCLUDES})
        target_compile_features(${target} PRIVATE c_std_11)
        target_compile_options(${target} PRIVATE -Wall -Wextra -Werror -UNDEBUG)
    endforeach()
    option(X7_SANITIZERS "ASan/UBSan on host tests" ON)
    if(X7_SANITIZERS AND CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
        foreach(target test-midahs test-platform test-assets)
            target_compile_options(${target} PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer -g)
            target_link_options(${target} PRIVATE -fsanitize=address,undefined)
        endforeach()
    endif()
    add_test(NAME midahs COMMAND test-midahs)
    set_tests_properties(midahs assets platform-0 platform-1 platform-2 platform-3 platform-4 platform-5 platform-6 platform-7 PROPERTIES ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;UBSAN_OPTIONS=halt_on_error=1")
    return()
endif()
if(NOT CMAKE_SYSTEM_PROCESSOR STREQUAL "mips")
    message(FATAL_ERROR "Use the SDK toolchain or configure -DX7_HOST_TESTS=ON")
endif()
add_executable(x7-app ${PORTABLE} app/platform.c app/assets.c "${X7_SDK}/app/audio.c"
    "${X7_SDK}/sdk/syscalls.c" "${X7_SDK}/sdk/common/volume.c"
    "${X7_SDK}/sdk/platform/crt.c" "${X7_SDK}/sdk/platform/runtime.c"
    "${X7_SDK}/sdk/platform/timing.c" "${X7_SDK}/sdk/platform/fb_video.c"
    "${X7_SDK}/sdk/platform/app_stubs.S" "${X7_SDK}/sdk/platform/ui_stubs.S"
    "${X7_SDK}/sdk/platform/input_stubs.S" "${X7_SDK}/sdk/platform/audio_stubs.S")
set_target_properties(x7-app PROPERTIES OUTPUT_NAME "${X7_APP_ID}" SUFFIX ".app")
target_include_directories(x7-app PRIVATE ${APP_INCLUDES})
target_compile_options(x7-app PRIVATE -EL -mabi=32 -march=24kec -O2 -G0 -mno-abicalls -fno-pic
    "$<$<COMPILE_LANGUAGE:C>:-ffreestanding;-fno-builtin;-fno-stack-protector;-fno-unwind-tables;-fno-asynchronous-unwind-tables;-std=c11;-Wall;-Wextra;-Werror>")
target_compile_definitions(x7-app PRIVATE X7_SHARED_VOLUME=1 X7_DEBUG_LOG=$<BOOL:${X7_DEBUG_LOG}> X7_ENABLE_AUDIO=0)
target_link_options(x7-app PRIVATE -EL -mabi=32 -march=24kec -nostdlib -no-pie
    "-Wl,--build-id=none,-n,-T${X7_SDK}/sdk/platform/app.ld,--defsym=APP_BASE=0x69800000")
set_property(TARGET x7-app APPEND PROPERTY LINK_DEPENDS "${X7_SDK}/sdk/platform/app.ld")
add_custom_command(TARGET x7-app POST_BUILD
    COMMAND "${Python3_EXECUTABLE}" "${X7_SDK}/tools/check_elf.py" "$<TARGET_FILE:x7-app>" VERBATIM)
add_custom_target(card ALL
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/stage.py"
        "$<TARGET_FILE:x7-app>" "${GENERATED}/${X7_APP_ID}.desktop"
        "${CMAKE_CURRENT_BINARY_DIR}/card"
    DEPENDS x7-app tools/stage.py VERBATIM)
