import numpy as np
import matplotlib.pyplot as plt
import os 

# fname = './measurement/fmr-test_2-5GHz_sweep/fmr-test-2.0GHz_2021-12-21_10-40-56.csv'
f = './measurement/CoFeB-ref_12-16GHz_sweep'
data = []


for d in os.listdir(f):
    data.extend(np.genfromtxt('./measurement/CoFeB-ref_12-16GHz_sweep/' + d, delimiter=',', skip_header=3, names=True))
    

for element in data:
    plt.plot(element['xvaluelockin'])

#res = np.loadtxt('./measurement/cont_t-0GHz_2021-12-17_11-13-08.csv', skiprows=0, delimiter=',')
# res= np.genfromtxt(fname, delimiter=',',skip_header=3, names=True)
# print(res.shape)
# names = res.dtype.names
# print(res.dtype.names)
# print(len(res.dtype.names))

# # for name in res.dtype.names:
# #     plt.plot(res[name],label=name)

# plt.plot(res[names[0]])
# #plt.legend(loc='upper left')
# plt.show()