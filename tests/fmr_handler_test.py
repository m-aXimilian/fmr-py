import unittest
import os, sys
import numpy as np
from numpy.core.fromnumeric import shape
import pyvisa as vi
from nidaqmx.constants import Edge, TaskMode
import matplotlib.pyplot as plt
from scipy import signal
import logging

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs
import src.measurement as m

def main():
    
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.DEBUG)

    edges = {'mode': TaskMode.TASK_COMMIT,
            'read-edge': Edge.FALLING,
            'write-edge': Edge.RISING,}
    fmr = m.FMRHandler('./recipes/fmr_1.yaml', edges)
    fmr.start_FMR()
    


if __name__ == '__main__':
    main()