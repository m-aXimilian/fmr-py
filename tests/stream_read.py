import os, sys
import logging
from nidaqmx.constants import AcquisitionType, Edge, TaskMode
from nidaqmx import stream_readers, stream_writers, constants
import numpy as np
import pyvisa as vi
import yaml
import nidaqmx as daq
from time import sleep, strftime
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs

# from https://github.com/ni/nidaqmx-python/blob/master/nidaqmx_examples/every_n_samples_event.py

def main():
    
    read = devs.NIUSB6259()
    read.add_channels('Dev1','ai0')

    read.task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)

    cont = {'samples': []}
    
       
    
    def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        print('callback')
        data = read.task.read(number_of_samples_per_channel=200)
        cont['samples'].extend(data)

        return 0
    
    read.task.register_every_n_samples_acquired_into_buffer_event(200, callback)
    read.start()
    

    input('enter to stop\n')
    
    print(len(cont['samples']))

if __name__ == '__main__':
    main()