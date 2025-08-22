cmake_minimum_required(VERSION 3.12)
project(grover_accelerator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(pybind11 REQUIRED)

# Optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -DNDEBUG")
endif()

# Create the pybind11 module
pybind11_add_module(grover_accelerator grover_accelerator.cpp)

# Compiler-specific options
if(MSVC)
    target_compile_options(grover_accelerator PRIVATE /W4)
else()
    target_compile_options(grover_accelerator PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Enable threading support
find_package(Threads REQUIRED)
target_link_libraries(grover_accelerator PRIVATE Threads::Threads)

# Set properties
set_target_properties(grover_accelerator PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    INTERPROCEDURAL_OPTIMIZATION TRUE
)

# Platform-specific optimizations
if(WIN32)
    target_compile_definitions(grover_accelerator PRIVATE WIN32_LEAN_AND_MEAN)
endif()

if(APPLE)
    target_compile_options(grover_accelerator PRIVATE -mmacosx-version-min=10.14)
endif()

# Debug information in debug builds
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(grover_accelerator PRIVATE -g)
endif()
