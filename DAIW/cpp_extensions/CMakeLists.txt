# DAIW C++ Performance Extensions
# Ultra-low latency audio, MIDI, network, and rendering
cmake_minimum_required(VERSION 3.15)
project(daiw_extensions VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native")
endif()

# Find dependencies
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG)

if(NOT pybind11_FOUND)
    # Fallback to pip-installed pybind11
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    find_package(pybind11 REQUIRED PATHS ${pybind11_DIR})
endif()

# Optional dependencies (graceful degradation if not found)
find_package(FFTW3 QUIET)
find_package(OpenGL QUIET)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# ============================================================================
# Module 1: Audio Engine
# ============================================================================
pybind11_add_module(audio_engine
    src/daiw_audio.cpp
    src/pitch_detection.cpp
)

if(FFTW3_FOUND)
    target_link_libraries(audio_engine PRIVATE FFTW3::fftw3f)
    target_compile_definitions(audio_engine PRIVATE HAVE_FFTW3)
endif()

# Platform-specific SIMD optimizations
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64|amd64")
    if(MSVC)
        target_compile_options(audio_engine PRIVATE /arch:AVX2)
    else()
        target_compile_options(audio_engine PRIVATE -mavx2 -mfma -msse4.2)
    endif()
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64")
    target_compile_options(audio_engine PRIVATE -march=armv8-a+simd)
endif()

set_target_properties(audio_engine PROPERTIES
    OUTPUT_NAME "audio_engine"
    PREFIX ""
)

# ============================================================================
# Module 2: MIDI Processor
# ============================================================================
pybind11_add_module(midi_processor
    src/daiw_midi.cpp
)

# Lock-free queue requires atomic operations
target_compile_options(midi_processor PRIVATE -std=c++17)

set_target_properties(midi_processor PROPERTIES
    OUTPUT_NAME "midi_processor"
    PREFIX ""
)

# ============================================================================
# Module 3: Network Core
# ============================================================================
pybind11_add_module(network_core
    src/daiw_network.cpp
    src/serialization.cpp
)

# Optional: Link LZ4 for compression
find_library(LZ4_LIBRARY lz4)
if(LZ4_LIBRARY)
    target_link_libraries(network_core PRIVATE ${LZ4_LIBRARY})
    target_compile_definitions(network_core PRIVATE HAVE_LZ4)
endif()

set_target_properties(network_core PROPERTIES
    OUTPUT_NAME "network_core"
    PREFIX ""
)

# ============================================================================
# Module 4: Render Engine
# ============================================================================
if(OpenGL_FOUND)
    pybind11_add_module(render_engine
        src/daiw_render.cpp
        src/particles_gpu.cpp
    )

    target_link_libraries(render_engine PRIVATE OpenGL::GL)

    # Platform-specific GL loaders
    if(UNIX AND NOT APPLE)
        # Linux: use GLEW or glad
        find_package(GLEW QUIET)
        if(GLEW_FOUND)
            target_link_libraries(render_engine PRIVATE GLEW::GLEW)
        endif()
    endif()

    set_target_properties(render_engine PROPERTIES
        OUTPUT_NAME "render_engine"
        PREFIX ""
    )
else()
    message(WARNING "OpenGL not found, render_engine will not be built")
endif()

# ============================================================================
# Installation
# ============================================================================
# Install to Python site-packages/daiw/cpp_extensions/
install(TARGETS audio_engine midi_processor network_core
    LIBRARY DESTINATION daiw/cpp_extensions
    RUNTIME DESTINATION daiw/cpp_extensions
)

if(TARGET render_engine)
    install(TARGETS render_engine
        LIBRARY DESTINATION daiw/cpp_extensions
        RUNTIME DESTINATION daiw/cpp_extensions
    )
endif()

# ============================================================================
# Testing
# ============================================================================
enable_testing()

# Add C++ unit tests (requires Catch2 or Google Test)
find_package(Catch2 QUIET)
if(Catch2_FOUND)
    add_executable(test_audio_engine tests/test_audio_engine.cpp src/pitch_detection.cpp)
    target_link_libraries(test_audio_engine PRIVATE Catch2::Catch2)
    add_test(NAME AudioEngineTests COMMAND test_audio_engine)
endif()

# Python integration tests
add_test(
    NAME PythonIntegrationTests
    COMMAND ${Python3_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_cpp_extensions.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/..
)

# ============================================================================
# Build Info
# ============================================================================
message(STATUS "")
message(STATUS "DAIW C++ Extensions Configuration:")
message(STATUS "  Python: ${Python3_EXECUTABLE}")
message(STATUS "  pybind11: ${pybind11_VERSION}")
message(STATUS "  FFTW3: ${FFTW3_FOUND}")
message(STATUS "  OpenGL: ${OpenGL_FOUND}")
message(STATUS "  LZ4: ${LZ4_LIBRARY}")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  CXX Flags: ${CMAKE_CXX_FLAGS_RELEASE}")
message(STATUS "")
