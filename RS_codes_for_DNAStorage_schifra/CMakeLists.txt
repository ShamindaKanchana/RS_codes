cmake_minimum_required(VERSION 3.10)
project(schifra VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Create a shared library for DNA storage
add_library(schifra_dna_storage SHARED
    src/dna_storage.cpp
)
target_include_directories(schifra_dna_storage
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)
target_compile_features(schifra_dna_storage PUBLIC cxx_std_17)

# Install the DNA storage library
install(TARGETS schifra_dna_storage
    EXPORT schifra-targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# Create the interface library for external use
add_library(schifra INTERFACE)
target_link_libraries(schifra INTERFACE 
    schifra_dna_storage
)
target_include_directories(schifra 
    INTERFACE 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Print sources for debugging
message(STATUS "Building with sources: ${SOURCES}")

# Enable testing
enable_testing()

# Build examples if requested
option(BUILD_EXAMPLES "Build example programs" ON)
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Install rules
include(GNUInstallDirs)
install(
    DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)

# Install the interface library
target_include_directories(schifra INTERFACE
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

install(TARGETS schifra
    EXPORT schifra-targets
)

# Package configuration
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/schifra-config-version.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Create and install the config file
configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/schifra-config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/schifra-config.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/schifra
)

# Create the export targets file
export(EXPORT schifra-targets
    FILE ${CMAKE_CURRENT_BINARY_DIR}/schifra-targets.cmake
    NAMESPACE schifra::
)

# Install the config and targets files
install(
    EXPORT schifra-targets
    FILE schifra-targets.cmake
    NAMESPACE schifra::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/schifra
)

install(
    FILES
        ${CMAKE_CURRENT_BINARY_DIR}/schifra-config.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/schifra-config-version.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/schifra
)
