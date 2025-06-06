@PACKAGE_INIT@

include(CMakeFindDependencyMacro)

include("${CMAKE_CURRENT_LIST_DIR}/schifra-targets.cmake")

# Add the targets file
get_filename_component(SCHIFRA_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
set(SCHIFRA_INCLUDE_DIRS "${SCHIFRA_CMAKE_DIR}/../../../include")

check_required_components(schifra)
