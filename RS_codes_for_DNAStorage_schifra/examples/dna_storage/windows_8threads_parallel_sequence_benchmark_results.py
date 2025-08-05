import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import ScalarFormatter

# Data from Windows benchmark results (8 threads)
sequence_sizes = [10000, 100000, 1000000, 10000000]  # in bases
sequence_sizes_mb = [x / (1024*1024) for x in sequence_sizes]  # Convert to MB

# Processing times (ms) for 8 threads [0, 1, 2 errors per block]
processing_times = {
    '0 errors': [1.16, 10.00, 122.65, 1422.12],
    '1 error': [1.52, 14.88, 144.61, 2102.32],
    '2 errors': [1.55, 15.21, 171.40, 2579.05]
}

# Throughput (MB/s) for 8 threads [0, 1, 2 errors per block]
throughput = {
    '0 errors': [8.25, 9.53, 7.78, 6.71],
    '1 error': [6.28, 6.41, 6.59, 4.54],
    '2 errors': [6.14, 6.27, 5.56, 3.70]
}

# Error correction rates [0, 1, 2 errors per block]
# Note: These are the same as Ubuntu since they're theoretical values
error_rates = {
    '0 errors': [100, 100, 100, 100],
    '1 error': [75.82, 73.52, 73.39, 73.37],
    '2 errors': [68.52, 70.42, 70.15, 70.12]
}

# Scaling data (8 threads vs 1 thread) for 100MB sequence
scaling_data = {
    'Threads': [1, 2, 4, 8],
    'Speedup (0 errors)': [1.0, 1.99, 3.36, 6.04],  # 8589.79/1422.12 ≈ 6.04
    'Speedup (1 error)': [1.0, 1.57, 3.28, 4.43],    # 9318.24/2102.32 ≈ 4.43
    'Speedup (2 errors)': [1.0, 1.59, 2.53, 3.64]    # 9667.51/2579.05 ≈ 3.75
}

def plot_processing_times():
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(sequence_sizes_mb))
    width = 0.25
    
    for i, (label, times) in enumerate(processing_times.items()):
        plt.bar(x + i*width, times, width, label=label)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Processing Time (ms)')
    plt.title('Processing Time vs Sequence Size (Windows 8 Threads)')
    plt.xticks(x + width, [f"{size:.2f}" for size in sequence_sizes_mb])
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('windows_processing_time_vs_size.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_throughput():
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(sequence_sizes_mb))
    
    for label, data in throughput.items():
        plt.plot(sequence_sizes_mb, data, 'o-', label=label, markersize=8, linewidth=2)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Throughput (MB/s)')
    plt.title('Throughput vs Sequence Size (Windows 8 Threads)')
    plt.xscale('log')
    plt.xticks(sequence_sizes_mb, [f"{size:.4f}" if size < 0.1 else f"{size:.2f}" for size in sequence_sizes_mb])
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig('windows_throughput_vs_size.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_error_correction():
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(sequence_sizes_mb))
    
    for label, rates in error_rates.items():
        if label != '0 errors':  # Skip 0 errors as it's always 100%
            plt.plot(sequence_sizes_mb, rates, 'o-', label=label, markersize=8, linewidth=2)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Error Correction Rate (%)')
    plt.title('Error Correction Rate vs Sequence Size (Windows 8 Threads)')
    plt.xscale('log')
    plt.xticks(sequence_sizes_mb, [f"{size:.4f}" if size < 0.1 else f"{size:.2f}" for size in sequence_sizes_mb])
    plt.ylim(65, 105)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig('windows_error_correction_rate.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_scaling():
    plt.figure(figsize=(12, 6))
    
    # Thread scaling data (for 100KB sequence size)
    threads = [1, 2, 4, 8]  # Windows has 8 threads
    speedup_0_errors = [1.0, 1.98, 3.85, 6.12]  # Speedup for 0 errors
    speedup_1_error = [1.0, 1.55, 3.71, 5.92]   # Speedup for 1 error
    speedup_2_errors = [1.0, 1.57, 3.73, 5.95]  # Speedup for 2 errors
    
    plt.plot(threads, speedup_0_errors, 'o-', label='0 errors', markersize=8, linewidth=2)
    plt.plot(threads, speedup_1_error, 's-', label='1 error', markersize=8, linewidth=2)
    plt.plot(threads, speedup_2_errors, 'd-', label='2 errors', markersize=8, linewidth=2)
    
    # Ideal scaling line (8x speedup)
    plt.axline((1, 1), slope=1, color='r', linestyle='--', label='Ideal Scaling', alpha=0.5)
    
    plt.xlabel('Number of Threads')
    plt.ylabel('Speedup (vs 1 Thread)')
    plt.title('Parallel Scaling on Windows (8 Cores/8 Threads)')
    plt.xticks(threads)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('windows_parallel_scaling.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    print("Generating Windows-specific visualizations...")
    
    # Create all plots
    plot_processing_times()
    plot_throughput()
    plot_error_correction()
    plot_scaling()
    
    print("Visualizations saved as:")
    print("- windows_processing_time_vs_size.png")
    print("- windows_throughput_vs_size.png")
    print("- windows_error_correction_rate.png")
    print("- windows_parallel_scaling.png")

if __name__ == "__main__":
    main()
