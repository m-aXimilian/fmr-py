import numpy as np
import matplotlib.pyplot as plt

fname = './measurement/fmr-test-2GHz_2021-12-20_11-14-47.csv'


#res = np.loadtxt('./measurement/cont_t-0GHz_2021-12-17_11-13-08.csv', skiprows=0, delimiter=',')
res= np.genfromtxt(fname, delimiter=',',skip_header=3, names=True)
print(res.shape)

print(res.dtype.names)

plt.plot(res['setfieldm'])
plt.show()