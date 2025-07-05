
import matplotlib.pyplot as plt

thread_counts = [1, 2, 4, 8]
processing_time_0_errors = [14863.33, 7562.24, 3922.91, 3829.03]
processing_time_1_error = [16870.78, 8459.96, 4701.89, 4084.75]
processing_time_2_errors = [16969.24, 8632.07, 4463.11, 4221.32]

plt.figure(figsize=(10, 6))
plt.plot(thread_counts, processing_time_0_errors, marker='o', label='0 errors/block')
plt.plot(thread_counts, processing_time_1_error, marker='o', label='1 error/block')
plt.plot(thread_counts, processing_time_2_errors, marker='o', label='2 errors/block')

plt.xlabel('Number of Threads')
plt.ylabel('Total Processing Time (ms)')
plt.title('Processing Time vs. Thread Count for 10M Bases')
plt.xticks(thread_counts)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()