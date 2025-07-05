import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import ScalarFormatter

# Data from benchmark results
sequence_sizes = [10000, 100000, 1000000, 10000000]  # in bases
sequence_sizes_mb = [x / (1024*1024) for x in sequence_sizes]  # Convert to MB

# Processing times (ms) for 4 threads [0, 1, 2 errors per block]
processing_times = {
    '0 errors': [3.82, 39.28, 389.68, 3890.05],
    '1 error': [6.66, 43.12, 432.40, 4231.73],
    '2 errors': [8.10, 44.44, 447.40, 4390.29]
}

# Throughput (MB/s) for 4 threads [0, 1, 2 errors per block]
throughput = {
    '0 errors': [2.49, 2.43, 2.45, 2.45],
    '1 error': [1.43, 2.21, 2.21, 2.25],
    '2 errors': [1.18, 2.15, 2.13, 2.17]
}

# Error correction rates [0, 1, 2 errors per block]
error_rates = {
    '0 errors': [100, 100, 100, 100],
    '1 error': [75.82, 73.52, 73.39, 73.37],
    '2 errors': [68.52, 70.42, 70.15, 70.12]
}

# Scaling data (4 threads vs 1 thread)
scaling_data = {
    'Sequence Size (MB)': [s/1024 for s in [10000, 100000, 1000000, 10000000]],
    'Speedup (0 errors)': [1.0, 3.87, 3.91, 3.82],
    'Speedup (1 error)': [1.0, 3.74, 3.75, 3.81],
    'Speedup (2 errors)': [1.0, 3.77, 3.76, 3.82]
}

def plot_processing_times():
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(sequence_sizes_mb))
    width = 0.25
    
    for i, (label, times) in enumerate(processing_times.items()):
        plt.bar(x + i*width, times, width, label=label)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Processing Time (ms)')
    plt.title('Processing Time vs Sequence Size (4 Threads)')
    plt.xticks(x + width, [f"{size:.2f}" for size in sequence_sizes_mb])
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('processing_time_vs_size.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_throughput():
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(sequence_sizes_mb))
    
    for label, data in throughput.items():
        plt.plot(sequence_sizes_mb, data, 'o-', label=label, markersize=8, linewidth=2)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Throughput (MB/s)')
    plt.title('Throughput vs Sequence Size (4 Threads)')
    plt.xscale('log')
    plt.xticks(sequence_sizes_mb, [f"{size:.4f}" if size < 0.1 else f"{size:.2f}" for size in sequence_sizes_mb])
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig('throughput_vs_size.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_error_correction():
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(sequence_sizes_mb))
    
    for label, rates in error_rates.items():
        if label != '0 errors':  # Skip 0 errors as it's always 100%
            plt.plot(sequence_sizes_mb, rates, 'o-', label=label, markersize=8, linewidth=2)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Error Correction Rate (%)')
    plt.title('Error Correction Rate vs Sequence Size (4 Threads)')
    plt.xscale('log')
    plt.xticks(sequence_sizes_mb, [f"{size:.4f}" if size < 0.1 else f"{size:.2f}" for size in sequence_sizes_mb])
    plt.ylim(65, 105)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig('error_correction_rate.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_scaling():
    plt.figure(figsize=(12, 6))
    
    df = pd.DataFrame(scaling_data)
    
    plt.plot(df['Sequence Size (MB)'], df['Speedup (0 errors)'], 'o-', label='0 errors', markersize=8, linewidth=2)
    plt.plot(df['Sequence Size (MB)'], df['Speedup (1 error)'], 's-', label='1 error', markersize=8, linewidth=2)
    plt.plot(df['Sequence Size (MB)'], df['Speedup (2 errors)'], 'd-', label='2 errors', markersize=8, linewidth=2)
    
    # Ideal scaling line (4x speedup)
    plt.axhline(y=4, color='r', linestyle='--', label='Ideal Scaling (4x)', alpha=0.5)
    
    plt.xlabel('Sequence Size (MB)')
    plt.ylabel('Speedup (vs 1 Thread)')
    plt.title('Parallel Scaling (4 Threads vs 1 Thread)')
    plt.xscale('log')
    plt.xticks(df['Sequence Size (MB)'], [f"{size:.4f}" if size < 0.1 else f"{size:.2f}" for size in df['Sequence Size (MB)']])
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig('parallel_scaling.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    print("Generating visualizations...")
    
    # Create all plots
    plot_processing_times()
    plot_throughput()
    plot_error_correction()
    plot_scaling()
    
    print("Visualizations saved as:")
    print("- processing_time_vs_size.png")
    print("- throughput_vs_size.png")
    print("- error_correction_rate.png")
    print("- parallel_scaling.png")

if __name__ == "__main__":
    main()
