#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "schifra::schifra_dna_storage" for configuration ""
set_property(TARGET schifra::schifra_dna_storage APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(schifra::schifra_dna_storage PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libschifra_dna_storage.so"
  IMPORTED_SONAME_NOCONFIG "libschifra_dna_storage.so"
  )

list(APPEND _cmake_import_check_targets schifra::schifra_dna_storage )
list(APPEND _cmake_import_check_files_for_schifra::schifra_dna_storage "${_IMPORT_PREFIX}/lib/libschifra_dna_storage.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
