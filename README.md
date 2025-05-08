# Reed-Solomon Error Correction Codes Implementation

## Overview
This project provides a comprehensive implementation of Reed-Solomon (RS) error correction codes, a powerful error-correcting code used in various applications such as data storage, telecommunications, and digital communication.

## Project Structure
```
RS_codes_main/
│
├── main.py               # Main demonstration script
├── init_tables.py        # Galois Field tables initialization
├── encode.py             # Reed-Solomon encoding functions
├── decode.py             # Reed-Solomon decoding functions
└── gf_operations.py      # Galois Field mathematical operations
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

## References
- [Reed-Solomon Error Correction](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)
- [Galois Field Arithmetic](https://www.cs.utsa.edu/~wagner/laws/FFM.html)

