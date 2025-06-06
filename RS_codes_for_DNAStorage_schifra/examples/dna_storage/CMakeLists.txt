# Add DNA storage example
add_executable(schifra_dna_storage_example
    schifra_dna_storage_example.cpp
)

# Add DNA storage test program
add_executable(test_dna_storage
    test_dna_storage.cpp
)

# Link with the schifra_dna_storage library
target_link_libraries(schifra_dna_storage_example PRIVATE schifra_dna_storage)
target_link_libraries(test_dna_storage PRIVATE schifra_dna_storage)

# Set include directories for both targets
foreach(target schifra_dna_storage_example test_dna_storage)
    target_include_directories(${target} 
        PRIVATE 
            ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    )

    target_compile_features(${target} PRIVATE cxx_std_17)

    # Ensure we're using the same compiler flags as the main library
    target_compile_options(${target} 
        PRIVATE 
            $<TARGET_PROPERTY:schifra_dna_storage,COMPILE_OPTIONS>
    )
    
    # Enable more warnings for the test program
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /WX)
    else()
        target_compile_options(${target} PRIVATE -Wall -Wextra -Werror -pedantic)
    endif()
endforeach()

