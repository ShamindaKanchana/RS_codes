
import matplotlib.pyplot as plt

thread_counts = [1, 2, 4, 8]
throughput_0_errors = [0.64, 1.26, 2.43, 2.49]
throughput_1_error = [0.57, 1.13, 2.03, 2.33]
throughput_2_errors = [0.56, 1.10, 2.14, 2.26]

plt.figure(figsize=(10, 6))
plt.plot(thread_counts, throughput_0_errors, marker='o', label='0 errors/block')
plt.plot(thread_counts, throughput_1_error, marker='o', label='1 error/block')
plt.plot(thread_counts, throughput_2_errors, marker='o', label='2 errors/block')

plt.xlabel('Number of Threads')
plt.ylabel('Throughput (MB/s)')
plt.title('Throughput vs. Thread Count for 10M Bases')
plt.xticks(thread_counts)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()