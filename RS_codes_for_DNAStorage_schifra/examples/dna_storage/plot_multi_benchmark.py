import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
sizes_mb = [1, 2, 5, 10]
colors = ['b', 'g', 'r', 'm']  # Different colors for each size
markers = ['o', 's', '^', 'd']  # Different markers for each size

plt.figure(figsize=(12, 7))

# Plot ideal speedup
threads = [1, 2, 4, 8]
plt.plot(threads, threads, 'k--', label='Ideal Speedup', linewidth=1)

# Plot results for each size
for size_mb, color, marker in zip(sizes_mb, colors, markers):
    try:
        # Read data from file
        filename = f'benchmark_results_{size_mb}MB.txt'
        with open(filename, 'r') as f:
            lines = f.readlines()[1:]  # Skip header
            
        # Parse data
        data = [line.strip().split('\t') for line in lines]
        threads = [int(row[0]) for row in data]
        speedups = [float(row[2].replace('x', '')) for row in data]
        
        # Plot
        plt.plot(threads, speedups, 
                marker=marker, 
                color=color, 
                linewidth=2,
                markersize=8,
                label=f'{size_mb}MB')
        
        # Add data labels
        for i, (t, s) in enumerate(zip(threads, speedups)):
            plt.annotate(f'{s:.2f}x', 
                        (t, s),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center',
                        fontsize=9,
                        color=color)
    except Exception as e:
        print(f"Error processing {filename}: {e}")

# Customize the plot
plt.title('Parallel Processing Speedup vs Number of Threads', fontsize=14, pad=20)
plt.xlabel('Number of Threads', fontsize=12)
plt.ylabel('Speedup (vs. Single Thread)', fontsize=12)
plt.xticks(threads)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='Sequence Size', loc='upper left')
plt.tight_layout()

# Save the plot
plt.savefig('parallel_speedup_comparison.png', dpi=300, bbox_inches='tight')
print("Plot saved as 'parallel_speedup_comparison.png'")

# Show the plot
plt.show()
