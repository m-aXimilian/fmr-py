import numpy as np
import matplotlib.pyplot as plt

res = np.loadtxt('./measurement/cont_t-0GHz_2021-12-16_17-49-58.csv', skiprows=0, delimiter=',')
print(res.shape)

plt.plot(res)
plt.show()