#!/bin/bash

# Update include paths in all header files
find include -type f -name "*.hpp" -exec sed -i 's/#include "schifra_galois_field.hpp"/#include "schifra\/core\/galois_field\/field.hpp"/g' {} \;
find include -type f -name "*.hpp" -exec sed -i 's/#include "schifra_galois_field_element.hpp"/#include "schifra\/core\/galois_field\/element.hpp"/g' {} \;
find include -type f -name "*.hpp" -exec sed -i 's/#include "schifra_galois_field_polynomial.hpp"/#include "schifra\/core\/galois_field\/polynomial.hpp"/g' {} \;
find include -type f -name "*.hpp" -exec sed -i 's/#include "schifra_reed_solomon_/"#include "schifra\/reed_solomon\/schifra_reed_solomon_/g' {} \;

# Fix any double slashes that might have been introduced
find include -type f -name "*.hpp" -exec sed -i 's/"schifra\/\//"schifra\//g' {} \;
