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
    config = load_config('./config/init.yaml')

    rate, timeout = 1000, 30
    buffsize = 2000

    read = devs.NIUSB6259()
    clock = devs.NIUSB6259()

    clock.task.co_channels.add_co_pulse_chan_freq(format_channel(
                config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ctr']['impuls-1']),
            freq=rate)

    clock.task.timing.cfg_implicit_timing(samps_per_chan=buffsize)
    clock.task.control(TaskMode.TASK_COMMIT)

    trigger = '/{}'.format(format_channel(
                config['devices']['daq-card']['id'],
                config['devices']['daq-card']['trigger']['impuls-1']))

    read.add_channels('Dev1','ai0')

    read.task.timing.cfg_samp_clk_timing(rate, sample_mode=AcquisitionType.CONTINUOUS, source=trigger,
        active_edge=Edge.FALLING)

    cont = {'samples': []}
    
       
    
    def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        print('callback')
        data = read.task.read(number_of_samples_per_channel=200)
        cont['samples'].extend(data)

        return 0
    
    read.task.register_every_n_samples_acquired_into_buffer_event(200, callback)
    read.start()
    clock.start()
    

    input('enter to stop\n')
    
    print(len(cont['samples']))


def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

def format_channel(_dev, _ch) -> str:
        """Compose a string for passing to the nidaqmx-API functions from 
        the device ID _DEV and the channel _CH."""
        return '{dev}/{ch}'.format(dev = _dev, ch = _ch)



if __name__ == '__main__':
    main()