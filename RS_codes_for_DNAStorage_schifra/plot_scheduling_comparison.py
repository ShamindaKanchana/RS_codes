import matplotlib.pyplot as plt
import numpy as np

# Data
test_cases = ['0 errors/block', '1 error/block', '2 errors/block']
static = [2.52, 2.32, 2.26]
dynamic = [2.56, 2.36, 2.28]
differences = ['+1.6%', '+1.7%', '+0.9%']

# Set up the plot with a white background
plt.style.use('ggplot')
plt.figure(figsize=(10, 6))

# Set the width of the bars
x = np.arange(len(test_cases))
width = 0.35

# Create bars
bars1 = plt.bar(x - width/2, static, width, label='Static', color='#1f77b4', alpha=0.9)
bars2 = plt.bar(x + width/2, dynamic, width, label='Dynamic', color='#4c8bf5', alpha=0.9)

# Add labels, title and custom x-axis tick labels
plt.xlabel('Test Case', fontsize=12, fontweight='bold')
plt.ylabel('Throughput (MB/s)', fontsize=12, fontweight='bold')
plt.title('Static vs Dynamic Scheduling Throughput Comparison\n(10M bases, 4 threads)', fontsize=14, fontweight='bold', pad=15)
plt.xticks(x, test_cases)
plt.legend(loc='upper right', frameon=False)

# Add value labels on top of bars
def add_labels(bars, diffs=None):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        if diffs and i < len(diffs):
            plt.text(bar.get_x() + bar.get_width()/2., height/2,
                    diffs[i], ha='center', va='center', fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='none'))

add_labels(bars1)
add_labels(bars2, differences)

# Add a horizontal grid
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()

# Save the figure
plt.savefig('scheduling_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
