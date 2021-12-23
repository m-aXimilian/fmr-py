import numpy as np
import matplotlib.pyplot as plt
import os
import re

# fname = './measurement/fmr-test_2-5GHz_sweep/fmr-test-2.0GHz_2021-12-21_10-40-56.csv'
f = './measurement/AMa09_4-10GHz_sweep/'

data = []
fil = re.compile('[0-9\.]*[A-Z]Hz$')

test = ['2021', '12', '22_17', '45', '38_AMa09', '9.0GHz']

o_str = list(filter(fil.match, test))

print(o_str)

for d in os.listdir(f):
    data.extend((np.genfromtxt(f + d, delimiter=',', skip_header=3, names=True)))

print(data.shape)
print(type(data[0]))

for d in os.listdir(f):
    tmp = list(filter(fil.match, (os.path.splitext(d)[0]).split('-')))
    if tmp:
        lab = tmp[0]
    else:
        lab = ''
    
    plt.plot((np.genfromtxt(f + d, delimiter=',', skip_header=3, names=True))['xvaluelockin'], label=lab)
    

plt.legend(loc='upper left')
plt.show()





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