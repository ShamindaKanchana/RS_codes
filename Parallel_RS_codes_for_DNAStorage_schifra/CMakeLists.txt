cmake_minimum_required(VERSION 3.8)
project(Parallel_RS_codes_for_DNAStorage_schifra CUDA CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find CUDA
find_package(CUDA REQUIRED)
include_directories(${CUDA_INCLUDE_DIRS})

# Add CUDA specific flags
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_50")

# Add source files
set(SOURCES
    src/dna_storage.cpp
    src/dna_storage_cuda.cu
)

# Add header files
set(HEADERS
    include/schifra/dna_storage.hpp
)

# Create library
add_library(schifra_dna_storage STATIC ${SOURCES} ${HEADERS})
target_include_directories(schifra_dna_storage PUBLIC include)

# Add examples
add_executable(test_dna_storage examples/dna_storage/test_dna_storage.cpp)
target_link_libraries(test_dna_storage schifra_dna_storage)

add_executable(test_dna_storage_parallel examples/dna_storage/test_dna_storage_parallel.cpp)
target_link_libraries(test_dna_storage_parallel schifra_dna_storage ${CUDA_LIBRARIES})

# Install targets
install(TARGETS schifra_dna_storage
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
