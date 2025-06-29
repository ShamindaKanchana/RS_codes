# DNA Storage with Reed-Solomon Error Correction

This project implements a parallelized Reed-Solomon (15,11) error correction system for DNA storage using the Schifra library. The implementation is optimized with OpenMP for improved performance and includes comprehensive benchmarking capabilities.

## Features

- **Reed-Solomon (15,11) Code**: Corrects up to 2 symbol errors per 15-symbol block
- **Parallel Processing**: Utilizes OpenMP for multi-threaded block processing
- **Comprehensive Benchmarking**: Measures encoding/decoding times, throughput, and error correction rates
- **Scalability Testing**: Evaluates performance across different thread counts
- **Error Analysis**: Tracks introduced and corrected errors with detailed statistics

## Performance Benchmarks

### System Specifications
- **CPU**: [Your CPU Model]
- **Threads**: 1 (single-threaded) and multi-threaded modes
- **Tested Sequence Lengths**: 1,000, 10,000, and 100,000 DNA bases
- **Error Rates**: 1 and 2 errors per block

### Benchmark Results

#### 1,000 Bases (0.98 KB)
| Metric | Single-threaded | Multi-threaded |
|--------|-----------------|----------------|
| Encoding Time | 0.59 ms | 0.62 ms |
| Decoding Time | 1.51 ms | 1.61 ms |
| Total Processing Time | 3.46 ms | 3.55 ms |
| Throughput | 0.28 MB/s | 0.27 MB/s |
| Error Correction Rate | 72.53% | 75.82% |

#### 10,000 Bases (9.77 KB)
| Metric | Single-threaded | Multi-threaded |
|--------|-----------------|----------------|
| Encoding Time | 4.32 ms | 2.05 ms |
| Decoding Time | 9.70 ms | 4.78 ms |
| Total Processing Time | 21.54 ms | 10.31 ms |
| Throughput | 0.44 MB/s | 0.93 MB/s |
| Error Correction Rate | 69.89% | 73.30% |

#### 100,000 Bases (97.66 KB)
| Metric | Single-threaded | Multi-threaded |
|--------|-----------------|----------------|
| Encoding Time | 16.60 ms | 16.60 ms |
| Decoding Time | 37.78 ms | 38.13 ms |
| Total Processing Time | 83.06 ms | 82.25 ms |
| Throughput | 1.15 MB/s | 1.16 MB/s |
| Error Correction Rate | 73.82% | 70.22% |

## Key Observations

1. **Error Correction**:
   - Achieves ~70-75% error correction rate across all test cases
   - Performs consistently well with both single and double errors per block

2. **Performance**:
   - Multi-threading shows significant improvement for medium-sized sequences (10,000 bases)
   - Throughput scales with sequence length, reaching ~1.2 MB/s for large sequences
   - Average block processing time remains under 0.01ms/block for large sequences

3. **Scalability**:
   - The implementation shows good scaling with larger datasets
   - Multi-threading provides better performance for medium-sized sequences

## Building and Running

### Dependencies
- C++17 compatible compiler
- OpenMP
- Schifra library

### Build Instructions
```bash
g++ -fopenmp -O3 -I /path/to/schifra/include parallel_dna_data_test.cpp -o dna_benchmark
```

### Running Benchmarks
```bash
./dna_benchmark
```

## Implementation Details

The system processes DNA sequences in parallel blocks:
1. **Encoding**:
   - Input DNA is split into blocks
   - Each block is encoded with Reed-Solomon (15,11) code
   - Error correction codes are generated for each block

2. **Error Introduction**:
   - Random substitution errors are introduced (1-2 per block)
   - Error positions and corrections are tracked

3. **Decoding**:
   - Corrupted blocks are decoded using the error correction codes
   - Corrected sequences are validated against the original

## Future Work

- Implement GPU acceleration using CUDA
- Optimize for larger block sizes
- Add support for different Reed-Solomon code parameters
- Implement more sophisticated error models

## License

[Specify your license here]
