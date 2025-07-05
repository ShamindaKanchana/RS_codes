
import matplotlib.pyplot as plt
import numpy as np

labels = ['0 errors', '1 error', '2 errors']
encoding_times = [6237.89, 6594.78, 6231.37]
decoding_times = [12549.35, 15558.23, 15706.40]

x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, encoding_times, width, label='Encoding Time')
plt.bar(x + width/2, decoding_times, width, label='Decoding Time')

plt.xlabel('Error Scenario')
plt.ylabel('Time (ms)')
plt.title('Encoding/Decoding Time Breakdown for 10M Bases (8 Threads)')
plt.xticks(x, labels)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()