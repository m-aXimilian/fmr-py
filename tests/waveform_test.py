import unittest
import os, sys
import numpy as np
from numpy.core.fromnumeric import shape
import pyvisa as vi
from nidaqmx.constants import Edge, TaskMode
import matplotlib.pyplot as plt
from scipy import signal

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs
import src.measurement as m

def main():
    wave = m.WaveForm(200, 10000)
    saw = wave.triangle()
    saw2 = wave.triangle_10()
    print(shape(saw))
    print(shape(saw2))
    plt.plot(saw)
    plt.plot(saw2)
    plt.show()
    # inp = np.linspace(0,1,1000)
    # saw = (signal.sawtooth(2*np.pi*inp, 0.5)+1)/2*1.5
    # plt.plot(saw)
    # plt.show()


if __name__ == '__main__':
    main()