import numpy as np
import matplotlib.pyplot as plt

res = np.loadtxt('./measurement/test2.csv', skiprows=1, delimiter=',')
print(res.shape)

plt.plot(res)
plt.show()