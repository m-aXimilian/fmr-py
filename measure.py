import numpy as np
import matplotlib.pyplot as plt

res = np.loadtxt('./measurement/test_2021-12-14_19-44-16.csv', skiprows=1, delimiter=',')
print(res.shape)

plt.plot(res)
plt.show()