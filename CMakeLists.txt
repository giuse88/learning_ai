cmake_minimum_required(VERSION 3.25)
project(learning_ai LANGUAGES CXX)

if(PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
  message(FATAL_ERROR
    "In-source builds are not allowed. Use: cmake -B build\n"
    "Then remove the generated CMakeCache.txt and CMakeFiles/ from the source dir.")
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)
endif()

# Write build/compile_commands.json so clangd knows the exact compile flags
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Dependencies, downloaded at configure time into build/_deps.
# SYSTEM keeps warnings from their headers out of our -Wall output.
include(FetchContent)

# cpp-httplib: HTTP(S) client; HTTPS needs OpenSSL (apt install libssl-dev)
set(HTTPLIB_REQUIRE_OPENSSL ON)
FetchContent_Declare(httplib
  GIT_REPOSITORY https://github.com/yhirose/cpp-httplib
  GIT_TAG v0.62.0
  GIT_SHALLOW TRUE
  SYSTEM)

# nlohmann/json: JSON parse/serialize
FetchContent_Declare(json
  URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  SYSTEM)

FetchContent_MakeAvailable(httplib json)

add_executable(simple_harness harness/simple_harness.cpp)
target_compile_options(simple_harness PRIVATE -Wall -Wextra -Wpedantic)
target_link_libraries(simple_harness PRIVATE httplib::httplib nlohmann_json::nlohmann_json)
