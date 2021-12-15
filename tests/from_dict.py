import os, sys
import logging
from nidaqmx.constants import Edge, TaskMode
import numpy as np
import pyvisa as vi
import yaml
import nidaqmx as daq
from time import sleep, strftime

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs

def main():
    
    rm = vi.ResourceManager()

    t = {
        'rm': rm,
        'conf': './config/hp83508.yaml',
    }
    
    rf = devs.HP83508(t['rm'], t['conf'])

    rf.setF(2)

if __name__ == '__main__':
    main()