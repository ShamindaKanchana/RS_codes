import matplotlib.pyplot as plt
import numpy as np

# Data
sequences = ['10M', '20M', '50M', '100M', 'Average']
thread_1 = [0.0073, 0.0076, 0.0073, 0.0087, 0.0077]
thread_4 = [0.0022, 0.0023, 0.0024, 0.0026, 0.0024]
thread_8 = [0.0017, 0.0017, 0.0017, 0.0020, 0.0018]
scaling = [4.29, 4.47, 4.29, 4.35, 4.35]

# Set up the figure and primary y-axis
plt.style.use('ggplot')
fig, ax1 = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('white')

# Set the width of the bars
x = np.arange(len(sequences))
width = 0.22

# Plot bars for each thread count
bars1 = ax1.bar(x - width, thread_1, width, label='1 Thread', color='#1f77b4', alpha=0.9)
bars2 = ax1.bar(x, thread_4, width, label='4 Threads', color='#4c8bf5', alpha=0.9)
bars3 = ax1.bar(x + width, thread_8, width, label='8 Threads', color='#a5c8f5', alpha=0.9)

# Add a line plot for scaling on secondary y-axis
ax2 = ax1.twinx()
line = ax2.plot(x, scaling, 'r-', marker='o', label='Scaling (1→8 threads)', linewidth=2.5, markersize=8)

# Customize the primary y-axis (processing time)
ax1.set_ylabel('Processing Time per Block (ms)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 0.01)

# Customize the secondary y-axis (scaling)
ax2.set_ylabel('Scaling Factor (x)', color='r', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='r')
ax2.set_ylim(0, 5)

# Add value labels on top of bars
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.0002,
                f'{height:.4f}', ha='center', va='bottom', fontsize=8)

add_labels(bars1)
add_labels(bars2)
add_labels(bars3)

# Add scaling values on the line
for i, val in enumerate(scaling):
    ax2.text(x[i], val + 0.1, f'{val:.2f}x', color='r', ha='center', va='bottom', fontweight='bold')

# Customize x-ticks and labels
plt.xticks(x, sequences)
plt.xlabel('Sequence Length', fontsize=12, fontweight='bold')

# Add title and legend
title = "Processing Time vs Thread Count for Different Sequence Lengths\n"
title += "(Lower is better, 2 errors per block)"
plt.title(title, fontsize=14, fontweight='bold', pad=20)

# Combine legends from both axes
bars, labels = ax1.get_legend_handles_labels()
line, line_label = ax2.get_legend_handles_labels()
ax1.legend(bars + line, labels + line_label, loc='upper center', 
           bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False)

# Add grid for better readability
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Add a note about the data
plt.figtext(0.5, 0.01, "Note: Scaling shows speedup from 1 to 8 threads. Average scaling: 4.35x", 
            ha="center", fontsize=10, style='italic')

# Adjust layout
plt.tight_layout()

# Save the figure
plt.savefig('sequence_scaling_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
