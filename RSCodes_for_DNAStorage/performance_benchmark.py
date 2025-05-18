import sys
import os
import time
import random
import math

import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from the main script
from large_dna_example import (
    encode_large_file, 
    decode_large_file, 
    introduce_random_errors
)

# Custom function to generate random DNA sequence
def generate_random_dna_sequence(length):
    """Generate a random DNA sequence of specified length"""
    # Convert float to integer, rounding up to ensure minimum size
    length = math.ceil(length)
    return ''.join(random.choice('ACGT') for _ in range(length))

# Reed Solomon parameters
n = 255  # Total symbols in a block
k = 223  # Number of data symbols
error_rate = 0.1  # 10% error rate

def run_performance_benchmark(file_sizes_mb):
    """
    Run performance benchmark for different file sizes
    
    Args:
        file_sizes_mb (list): List of file sizes in MB to test
    
    Returns:
        dict: Performance metrics for each file size
    """
    results = {
        'file_sizes': file_sizes_mb,
        'encode_times': [],
        'decode_times': [],
        'total_times': []
    }
    
    for size_mb in file_sizes_mb:
        # Generate test data
        test_data = generate_random_dna_sequence(size_mb * 1024 * 1024)
        
        # Encode benchmark
        encode_start = time.time()
        encoded_data, ecc_symbols_list = encode_large_file(test_data, n, k)
        encode_time = time.time() - encode_start
        
        # Introduce errors
        corrupted_data = introduce_random_errors(encoded_data, error_rate)
        
        # Decode benchmark
        decode_start = time.time()
        corrected_data, _ = decode_large_file(corrupted_data, ecc_symbols_list, n, k)
        decode_time = time.time() - decode_start
        
        results['encode_times'].append(encode_time)
        results['decode_times'].append(decode_time)
        results['total_times'].append(encode_time + decode_time)
    
    return results

def plot_performance_benchmark(results):
    """
    Create performance visualization
    
    Args:
        results (dict): Performance benchmark results
    """
    plt.figure(figsize=(10, 6))
    plt.plot(results['file_sizes'], results['encode_times'], 
             marker='o', label='Encoding Time')
    plt.plot(results['file_sizes'], results['decode_times'], 
             marker='s', label='Decoding Time')
    plt.plot(results['file_sizes'], results['total_times'], 
             marker='^', label='Total Processing Time')
    
    plt.title('Reed-Solomon Encoding/Decoding Performance\nfor DNA Storage')
    plt.xlabel('File Size (MB)')
    plt.ylabel('Processing Time (seconds)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('performance_benchmark.png')
    plt.close()

def main():
    file_sizes = [0.1, 0.2, 0.5, 1.0, 1.5, 2.0]
    benchmark_results = run_performance_benchmark(file_sizes)
    plot_performance_benchmark(benchmark_results)
    
    # Print detailed results
    for size, encode_time, decode_time, total_time in zip(
        benchmark_results['file_sizes'],
        benchmark_results['encode_times'],
        benchmark_results['decode_times'],
        benchmark_results['total_times']
    ):
        print(f"Size: {size} MB")
        print(f"  Encode Time: {encode_time:.4f} s")
        print(f"  Decode Time: {decode_time:.4f} s")
        print(f"  Total Time:  {total_time:.4f} s\n")

if __name__ == "__main__":
    main()