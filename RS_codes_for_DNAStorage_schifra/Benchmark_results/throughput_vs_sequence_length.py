import matplotlib.pyplot as plt
import numpy as np

# Data for 0 errors per block
throughput_0_errors = {
    '1_thread': [0.63, 0.63, 0.64, 0.64],
    '2_threads': [1.14, 1.14, 1.25, 1.26],
    '4_threads': [2.13, 2.13, 2.42, 2.43],
    '8_threads': [2.30, 2.30, 2.51, 2.49]
}

# Data for 1 error per block
throughput_1_error = {
    '1_thread': [0.59, 0.59, 0.58, 0.57],
    '2_threads': [1.18, 1.18, 1.15, 1.13],
    '4_threads': [2.21, 2.21, 2.19, 2.03],
    '8_threads': [2.20, 2.20, 2.31, 2.33]
}

# Data for 2 errors per block
throughput_2_errors = {
    '1_thread': [0.55, 0.55, 0.57, 0.56],
    '2_threads': [1.14, 1.14, 1.11, 1.10],
    '4_threads': [2.20, 2.20, 2.12, 2.14],
    '8_threads': [2.31, 2.31, 2.19, 2.26]
}

sequence_lengths = ['10K', '100K', '1M', '10M']
x = np.arange(len(sequence_lengths))
width = 0.2

# Plot for 0 errors per block
plt.figure(figsize=(10, 6))
plt.bar(x - 1.5*width, throughput_0_errors['1_thread'], width, label='1 Thread')
plt.bar(x - 0.5*width, throughput_0_errors['2_threads'], width, label='2 Threads')
plt.bar(x + 0.5*width, throughput_0_errors['4_threads'], width, label='4 Threads')
plt.bar(x + 1.5*width, throughput_0_errors['8_threads'], width, label='8 Threads')

plt.xlabel('Sequence Length (bases)')
plt.ylabel('Throughput (MB/s)')
plt.title('Throughput vs. Sequence Length (0 Errors per Block)')
plt.xticks(x, sequence_lengths)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

# Plot for 1 error per block
plt.figure(figsize=(10, 6))
plt.bar(x - 1.5*width, throughput_1_error['1_thread'], width, label='1 Thread')
plt.bar(x - 0.5*width, throughput_1_error['2_threads'], width, label='2 Threads')
plt.bar(x + 0.5*width, throughput_1_error['4_threads'], width, label='4 Threads')
plt.bar(x + 1.5*width, throughput_1_error['8_threads'], width, label='8 Threads')

plt.xlabel('Sequence Length (bases)')
plt.ylabel('Throughput (MB/s)')
plt.title('Throughput vs. Sequence Length (1 Error per Block)')
plt.xticks(x, sequence_lengths)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

# Plot for 2 errors per block
plt.figure(figsize=(10, 6))
plt.bar(x - 1.5*width, throughput_2_errors['1_thread'], width, label='1 Thread')
plt.bar(x - 0.5*width, throughput_2_errors['2_threads'], width, label='2 Threads')
plt.bar(x + 0.5*width, throughput_2_errors['4_threads'], width, label='4 Threads')
plt.bar(x + 1.5*width, throughput_2_errors['8_threads'], width, label='8 Threads')

plt.xlabel('Sequence Length (bases)')
plt.ylabel('Throughput (MB/s)')
plt.title('Throughput vs. Sequence Length (2 Errors per Block)')
plt.xticks(x, sequence_lengths)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()