
import matplotlib.pyplot as plt

errors_per_block = [0, 1, 2]
correction_rate_10K = [100.00, 74.73, 71.32]
correction_rate_100K = [100.00, 73.07, 70.49]
correction_rate_1M = [100.00, 73.33, 70.17]
correction_rate_10M = [100.00, 73.28, 70.09]

plt.figure(figsize=(10, 6))
plt.plot(errors_per_block, correction_rate_10K, marker='o', label='10K bases')
plt.plot(errors_per_block, correction_rate_100K, marker='o', label='100K bases')
plt.plot(errors_per_block, correction_rate_1M, marker='o', label='1M bases')
plt.plot(errors_per_block, correction_rate_10M, marker='o', label='10M bases')

plt.xlabel('Errors per Block')
plt.ylabel('Error Correction Rate (%)')
plt.title('Error Correction Rate vs. Errors per Block')
plt.xticks(errors_per_block)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()