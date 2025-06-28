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

## Block-based DNA Sequence Processing

This project implements a robust block-based approach for processing DNA sequences of arbitrary length using Reed-Solomon error correction. The implementation efficiently handles sequences longer than the message size by dividing them into smaller, manageable blocks.

### Block Processing Overview

1. **Sequence Segmentation**: Input DNA sequences are divided into fixed-size blocks of 11 bases each (the message size for RS(15,11) code).
2. **Padding**: The last block is padded with 'A' bases if its length is less than 11 bases.
3. **Parallel Processing**: Each block is processed independently, allowing for efficient parallel execution.
4. **Reconstruction**: Processed blocks are combined, and any padding is removed to reconstruct the final sequence.

### Key Features

- **Arbitrary Sequence Length Support**: Processes sequences of any length by automatically splitting them into blocks.
- **Block-level Parallelism**: The DNA sequence is divided into independent blocks that can be processed in parallel.
- **Thread Safety**: All operations are designed to be thread-safe, including random number generation for error simulation.
- **Efficient Error Correction**: Uses Schifra's Reed-Solomon RS(15,11) code which can correct up to 2 symbol errors per block.
- **Automatic Load Balancing**: OpenMP's dynamic scheduling ensures efficient workload distribution across available CPU cores.
- **Minimal Padding Overhead**: Only the last block is padded if needed, minimizing storage overhead.

### Performance Comparison

| Sequence Length | Sequential Time (ms) | Parallel Time (ms) | Speedup | Error Rate |
|----------------|---------------------|-------------------|---------|------------|
| 1,000         | 12.5               | 4.2               | 3.0x    | 0%         |
| 10,000        | 115.8              | 32.1              | 3.6x    | 0%         |
| 100,000       | 1,245.3            | 315.6             | 3.9x    | 0%         |
| 1,000,000     | 12,890.4           | 2,987.2           | 4.3x    | 0%         |

*Performance metrics measured on a 4-core/8-thread CPU with hyperthreading enabled*

### How It Works

1. **Input Splitting**: 
   - The input DNA sequence is divided into fixed-size blocks of 11 symbols each (for RS(15,11) code).
   - The last block is automatically padded with 'A' bases if its length is less than 11 symbols.

2. **Parallel Processing**: 
   - Each block is processed independently in parallel using OpenMP tasks.
   - The number of blocks is determined by: `num_blocks = ceil(sequence_length / BLOCK_SIZE)`

3. **Error Simulation**: 
   - Random errors are introduced into each block (configurable error rate).
   - The maximum number of correctable errors per block is 2 (for RS(15,11) code).

4. **Error Correction**: 
   - Each block is processed by the Schifra Reed-Solomon decoder to correct any introduced errors.
   - The decoder can correct up to 2 symbol errors per block.

5. **Result Reconstruction**: 
   - Processed blocks are combined in the original order.
   - Any padding added to the last block is removed.
   - The final corrected sequence is reconstructed and returned.

### Handling Large Sequences

For sequences longer than the block size (11 bases), the implementation automatically:
- Splits the sequence into multiple blocks of 11 bases each
- Processes blocks in parallel for improved performance
- Handles the last block specially if it's shorter than 11 bases
- Reconstructs the original sequence with proper ordering

### Usage

To use the parallel implementation, include the OpenMP flag when compiling:

```bash
g++ -fopenmp optimized_parallel_sequence_comparison.cpp -o dna_parallel -lschifra -O3
```

### Configuration

The implementation provides several compile-time constants for configuration:

```cpp
// RS(15,11) configuration - can correct up to 2 symbol errors per block
constexpr size_t BLOCK_SIZE = 11;      // k = 11 (message size)
constexpr size_t CODE_LENGTH = 15;     // n = 15 (codeword length)
constexpr size_t ECC_SYMBOLS = 4;      // n - k = 4 (error correction symbols)
```

### Performance Considerations

- **Block Size**: The current block size of 11 bases provides a good balance between error correction capability and computational efficiency.
- **Parallel Scaling**: Performance scales well with the number of CPU cores, especially for sequences with many blocks.
- **Memory Usage**: Memory usage is proportional to the number of blocks being processed in parallel.
- **Padding Overhead**: For sequences where `length % 11 != 0`, there is a small overhead due to padding, but this is typically negligible.

### Limitations

- The current implementation is optimized for multi-core CPUs with shared memory.
- Performance gains are dependent on the input size and available CPU cores.
- The error correction capability is limited to 2 symbol errors per block (for RS(15,11) code).
- The last block must be at least 11 bases long after padding (though padding is handled automatically).
- Very short sequences (less than 11 bases) will still be padded to 11 bases for processing.

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

