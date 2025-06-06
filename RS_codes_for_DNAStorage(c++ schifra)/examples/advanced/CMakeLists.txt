# Advanced Reed-Solomon examples
add_executable(rs_advanced05 schifra_reed_solomon_example05.cpp)
target_link_libraries(rs_advanced05 PRIVATE schifra)

add_executable(rs_advanced06 schifra_reed_solomon_example06.cpp)
target_link_libraries(rs_advanced06 PRIVATE schifra)

add_executable(rs_advanced07 schifra_reed_solomon_example07.cpp)
target_link_libraries(rs_advanced07 PRIVATE schifra)

add_executable(rs_advanced09 schifra_reed_solomon_example09.cpp)
target_link_libraries(rs_advanced09 PRIVATE schifra)

# Temporarily disabled - file not found
# add_executable(rs_gencodec_example ${CMAKE_SOURCE_DIR}/schifra_reed_solomon_gencodec_example.cpp)
# target_link_libraries(rs_gencodec_example PRIVATE schifra)
