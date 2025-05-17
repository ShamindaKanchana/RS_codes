# Reed-Solomon Codes for DNA Storage

This implementation adapts Reed-Solomon error correction specifically for DNA data storage applications. It provides specialized encoding and decoding capabilities that work with DNA sequences (A, C, G, T bases) while leveraging the power of Reed-Solomon codes for error correction.

## Features

- DNA-specific encoding and decoding
- Support for DNA alphabet (A, C, G, T)
- Configurable message length (k) and codeword length (n)
- Error correction capabilities for:
  - Substitution errors (base changes)
  - Known erasure positions
  - Multiple error types

## Usage

The implementation consists of several key components:

1. `dna_utils.py`: Utility functions for DNA sequence handling
2. `dna_rs_encoder.py`: DNA-specific Reed-Solomon encoder
3. `dna_rs_decoder.py`: DNA-specific Reed-Solomon decoder
4. `example.py`: Example usage and demonstration

### Basic Example

```python
from dna_rs_encoder import DNAReedSolomonEncoder
from dna_rs_decoder import DNAReedSolomonDecoder

# Initialize with desired parameters
encoder = DNAReedSolomonEncoder(n=255, k=223)
decoder = DNAReedSolomonDecoder(n=255, k=223)

# Encode DNA sequence
dna_sequence = "ATCGATCGTAGCTACGATCGATCG"
encoded_dna, ecc_symbols = encoder.encode(dna_sequence)

# Decode (with error correction)
corrected_dna = decoder.decode(received_dna, ecc_symbols)
```

## Parameters

- `n`: Codeword length (must be less than 256 for GF(256))
- `k`: Message length (must be less than n)
- The difference `n-k` determines the error correction capability

## Error Correction Capability

The implementation can correct up to `t` errors and `e` erasures where:
```
2t + e <= n-k
```

For example, with n=255 and k=223:
- Can correct up to 16 errors
- Or up to 32 erasures
- Or a combination (e.g., 8 errors and 16 erasures)

## Dependencies

This implementation builds upon the base Reed-Solomon implementation from the parent directory and requires:
- Python 3.6+
- Base Reed-Solomon implementation modules
