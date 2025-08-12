import matplotlib.pyplot as plt
import numpy as np

# Data
threads = [1, 2, 4, 8]
ubuntu_throughput = [1.32, 2.62, 5.15, None]
windows_throughput = [1.44, 2.95, 5.22, 7.78]
ubuntu_speedup = [1.00, 1.98, 3.90, None]
windows_speedup = [1.00, 2.05, 3.62, 5.40]

# Filter out None values for plotting
ubuntu_throughput_clean = [x for x in ubuntu_throughput if x is not None]
windows_throughput_clean = windows_throughput[:len(ubuntu_throughput_clean)]
threads_clean = threads[:len(ubuntu_throughput_clean)]

# Set up the plot with a white background
plt.style.use('ggplot')  # Using ggplot style which is more widely available
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('white')

# Colors
blue1 = '#1f77b4'  # Slightly darker blue
blue2 = '#4c8bf5'  # Lighter blue

# Plot Throughput
x = np.arange(len(threads_clean))
width = 0.35

rects1 = ax1.bar(x - width/2, ubuntu_throughput_clean, width, label='Ubuntu', color=blue1, alpha=0.9)
rects2 = ax1.bar(x + width/2, windows_throughput_clean, width, label='Windows', color=blue2, alpha=0.9)

ax1.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
ax1.set_ylabel('Throughput (MB/s)', fontsize=12, fontweight='bold')
ax1.set_title('Throughput Comparison (1M bases, 0 errors)', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(threads_clean)
ax1.legend(loc='upper left', bbox_to_anchor=(0, 1), frameon=False, ncol=2)

# Add value labels on top of bars
def add_labels(ax, rects):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom', fontsize=10)

add_labels(ax1, rects1)
add_labels(ax1, rects2)

# Plot Speedup
x_speedup = np.arange(len(threads_clean))
rects3 = ax2.bar(x_speedup - width/2, ubuntu_speedup[:len(threads_clean)], width, label='Ubuntu', color=blue1, alpha=0.9)
rects4 = ax2.bar(x_speedup + width/2, windows_speedup[:len(threads_clean)], width, label='Windows', color=blue2, alpha=0.9)

ax2.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
ax2.set_ylabel('Speedup (x)', fontsize=12, fontweight='bold')
ax2.set_title('Speedup Comparison (1M bases, 0 errors)', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x_speedup)
ax2.set_xticklabels(threads_clean)
ax2.legend(loc='upper left', bbox_to_anchor=(0, 1), frameon=False, ncol=2)

add_labels(ax2, rects3)
add_labels(ax2, rects4)

# Add Windows 8-thread data point for throughput
ax1.annotate('Windows 8 threads:\n7.78 MB/s',
             xy=(2.8, 7.78), xycoords='data',
             xytext=(20, 20), textcoords='offset points',
             arrowprops=dict(arrowstyle="->", color=blue2),
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=blue2, alpha=0.9))

# Add Windows 8-thread data point for speedup
ax2.annotate('Windows 8 threads:\n5.40x',
             xy=(2.8, 5.40), xycoords='data',
             xytext=(20, 20), textcoords='offset points',
             arrowprops=dict(arrowstyle="->", color=blue2),
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=blue2, alpha=0.9))

# Adjust layout
plt.tight_layout()

# Save the figure
plt.savefig('throughput_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
