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
    clock = devs.NIUSB6259()
    write = devs.NIUSB6259()
    read = devs.NIUSB6259()
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/test.log', filemode='w', level=logging.DEBUG)

    rate, N, timeout = 1000, 20000, 30
    
    
    clock.config_clk(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ctr']['impuls-1'],
                rate, N, TaskMode.TASK_COMMIT)
    clock.set_trigger(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['trigger']['impuls-1'])

    write.add_channels(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ao']['set-value-small'], _type='ao')
    write.config_sample_clk(rate, clock.trigger, Edge.RISING, N)

    read.add_channels(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ai']['field-set-measure'], _type='ai')
    read.config_sample_clk(rate, clock.trigger, Edge.FALLING, N)

    setH = np.linspace(0,100,N)/100

    read.start()
    write.start()
    clock.start()

    out = read.analog_read_n(N, timeout)

    np.savetxt('./measurement/test_{}.csv'
        .format(strftime("%Y-%m-%d_%H-%M-%S")), 
        np.array(out), delimiter=',',
        header='H-Field from {hmin} to {hmax} at {hf} and sampled \
        with {hs}'.format(hmin=setH[0], hmax=setH[-1], hf=10, hs=100)
    )

def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

if __name__ == '__main__':
    main()