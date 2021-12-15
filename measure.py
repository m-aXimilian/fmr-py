import numpy as np
import matplotlib.pyplot as plt

res = np.loadtxt('./measurement/test-3GHz_2021-12-15_17-39-00.csv', skiprows=3, delimiter=',')
print(res.shape)

plt.plot(res)
plt.show()