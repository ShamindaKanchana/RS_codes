# Reed-Solomon Error Correction Codes Implementation

## Overview
This project provides a comprehensive implementation of Reed-Solomon (RS) error correction codes, a powerful error-correcting code used in various applications such as data storage, telecommunications, and digital communication. The repository includes both a custom Python implementation and the Schifra Reed-Solomon error correction library in C++.

**Note:** The Schifra library is included for academic and research purposes only, with no commercial intent.

## Project Structure
```
RS_codes/
│
├── RS_codes_main/               # Custom Python implementation
│   ├── main.py                  # Main demonstration script
│   ├── init_tables.py           # Galois Field tables initialization
│   ├── encode.py                # Reed-Solomon encoding functions
│   ├── decode.py                # Reed-Solomon decoding functions
│   └── gf_operations.py         # Galois Field mathematical operations
│
└── schifra/                   # Schifra C++ Reed-Solomon library
    ├── include/                 # Header files
    ├── src/                    # Source files
    └── examples/               # Example usage
```

## Key Components

### 1. Galois Field Operations (`gf_operations.py`)
This module provides low-level mathematical operations for Galois Field computations:

- `gf_add()`: Addition in Galois Field (bitwise XOR)
- `gf_mul()`: Multiplication in Galois Field
- `gf_div()`: Division in Galois Field
- `gf_pow()`: Exponentiation in Galois Field
- `gf_inverse()`: Multiplicative inverse in Galois Field
- `gf_poly_*()`: Polynomial operations in Galois Field
  - `gf_poly_add()`: Polynomial addition
  - `gf_poly_mul()`: Polynomial multiplication
  - `gf_poly_div()`: Polynomial division
  - `gf_poly_eval()`: Polynomial evaluation
- `rs_generator_poly()`: Generate Reed-Solomon generator polynomial

### 2. Tables Initialization (`init_tables.py`)
Initializes logarithm and anti-logarithm tables for efficient Galois Field computations:
- Precomputes lookup tables for fast mathematical operations
- Uses a primitive polynomial (default: 0x11d)
- Creates exponential and logarithm tables

### 3. Encoding (`encode.py`)
Implements Reed-Solomon encoding:
- `rs_encode_msg()`: Encodes input message with error correction symbols
- Uses Extended Synthetic Division algorithm
- Adds redundant error correction symbols

### 4. Decoding (`decode.py`)
Implements Reed-Solomon decoding:
- `rs_correct_msg()`: Corrects errors and erasures in encoded message
- Supports error and erasure correction
- Uses syndrome calculation and error location detection

## Usage Example
```python
from init_tables import init_tables
from encode import rs_encode_msg
from decode import rs_correct_msg

# Initialize Galois Field tables
prim = 0x11d  # Primitive polynomial
n = 20  # Total codeword length
k = 11  # Message length

# Original message
message = "hello world"

# Encode message
encoded_msg = rs_encode_msg([ord(x) for x in message], n-k)

# Simulate transmission errors
encoded_msg[0] = 0
encoded_msg[1] = 2

# Correct errors
corrected_msg, _ = rs_correct_msg(encoded_msg, n-k, erase_pos=[0, 1])
```

## Key Concepts
- **Galois Field**: A finite field used for mathematical operations
- **Primitive Polynomial**: Irreducible polynomial used in field generation
- **Syndrome Calculation**: Method to detect and locate errors
- **Error Correction Capability**: Determined by number of redundant symbols

## Performance Considerations
- Lookup tables for fast mathematical operations
- Optimized polynomial arithmetic
- Supports error and erasure correction

## Limitations
- Maximum message length: 255 symbols
- Error correction limited by redundant symbol count

## Schifra C++ Reed-Solomon Library

### Overview
Schifra is a robust, highly optimized C++ library for Reed-Solomon error correction coding. It provides a comprehensive set of features for implementing RS codes in high-performance applications.

### Key Features
- Support for variable code word lengths and error correction capabilities
- High performance through template metaprogramming and optimization
- Support for both encoding and decoding operations
- Includes utilities for interleaving and block processing
- Comprehensive test suite and examples

### Example Usage
```cpp
#include <schifra/schifra_reed_solomon.hpp>

// Initialize the Reed-Solomon codec
const std::size_t code_length = 255;
const std::size_t fec_length = 32;
const std::size_t data_length = code_length - fec_length;

schifra::reed_solomon::codec<code_length, fec_length> rs_encoder;

// Encode data
std::string message = "Hello, World!";
std::vector<schifra::galois::field_symbol> encoded_data(code_length);

// ... (encoding and decoding operations)
```

### Building and Running the DNA Storage Example

#### Prerequisites
- C++17 compatible compiler (g++ 7+ or clang++ 6+)
- Make

#### Compilation
```bash
# Navigate to the DNA storage example directory
cd RS_codes_for_DNAStorage_schifra/examples/dna_storage/

# Compile with g++
g++ -std=c++17 -I ../../include test_dna_storage.cpp -o test_dna_storage

# Make the binary executable
chmod +x test_dna_storage
```

#### Running the Example
```bash
./test_dna_storage
```

#### Expected Output
```
=== Testing Schifra DNA Storage ===

Original DNA: ACGTACGTACG
Encode returned: 1
Block after encoding: 00 01 02 03 00 01 02 03 00 01 02 09 02 05 09 
Encoded DNA (data only): ACGTACGTACG
ECC (4 symbols): 09 02 05 09 
Block before decoding: 00 01 02 03 00 01 02 03 00 01 02 09 02 05 09 
Decoded DNA: ACGTACGTACG

✅ Test 1/2 PASSED: Error-free decoding successful

Corrupted DNA: AAGTAGGTACG (introduced 2 errors)
Block before decoding: 00 00 02 03 00 02 02 03 00 01 02 09 02 05 09 
Corrected DNA: ACGTACGTACG

✅ Test 2/2 PASSED: Error correction successful
```

### Customizing the Example

To use different RS parameters, modify the `dna_storage` template parameters in `test_dna_storage.cpp`:

```cpp
// Format: schifra::dna_storage<code_length, fec_length, data_length>
// Where: fec_length = code_length - data_length
// Example: RS(15,11) with t=2 error correction capability
using dna_storage_type = schifra::dna_storage<15, 4, 11>;

// For RS(30,20) with t=5 error correction capability:
// using dna_storage_type = schifra::dna_storage<30, 10, 20>;
```

### Building Schifra (Full Library)
Refer to the `schifra/README` for detailed build instructions and requirements for the full library.

## Academic Use
This repository is intended for academic and research purposes only. The inclusion of the Schifra library is meant to facilitate research and education in error correction coding. Please ensure proper attribution and compliance with the original library's license terms for any derivative works.

## Additional Resources

### Troubleshooting

1. **Header Not Found Error**
   ```
   fatal error: schifra/dna_storage.hpp: No such file or directory
   ```
   - Ensure the `-I` flag points to the directory containing the `schifra` folder
   - Verify the file exists at `include/schifra/dna_storage.hpp`

2. **C++ Version Error**
   ```
   error: #error This file requires compiler and library support for the ISO C++ 2017 standard
   ```
   - Add `-std=c++17` flag to your compilation command
   - Update your compiler if needed

## Additional Resources

### Troubleshooting

1. **Header Not Found Error**
   ```
   fatal error: schifra/dna_storage.hpp: No such file or directory
   ```
   - Ensure the `-I` flag points to the directory containing the `schifra` folder
   - Verify the file exists at `include/schifra/dna_storage.hpp`

2. **C++ Version Error**
   ```
   error: #error This file requires compiler and library support for the ISO C++ 2017 standard
   ```
   - Add `-std=c++17` flag to your compilation command
   - Update your compiler if needed

## References
- [Reed-Solomon Error Correction](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)
- [Galois Field Arithmetic](https://www.cs.utsa.edu/~wagner/laws/FFM.html)
- [Schifra Library](https://github.com/ArashPartow/schifra) - Original Schifra RS library

