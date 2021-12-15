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
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/test.log', filemode='w', level=logging.DEBUG)
    logging.info('Started in main()')
    #rm = vi.ResourceManager()
    #rf = devs.HP83508(rm, config['devices']['rf-generator']['id'])

    with daq.Task() as reader, daq.Task() as writer, daq.Task() as clock:
        
        rate = 1000
        N = 40000
        clock.co_channels.add_co_pulse_chan_freq(format_channel(
                config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ctr']['impuls-1']),
            freq=rate)
            
        clock.timing.cfg_implicit_timing(samps_per_chan=N)
        clock.control(TaskMode.TASK_COMMIT)
        trigger = '/{}'.format(format_channel(
                config['devices']['daq-card']['id'],
                config['devices']['daq-card']['trigger']['impuls-1']))
        
        writer.ao_channels.add_ao_voltage_chan(format_channel(
            config['devices']['daq-card']['id'],
            config['devices']['daq-card']['ao']['set-value-small']))
        writer.timing.cfg_samp_clk_timing(rate, source=trigger, active_edge=Edge.RISING, samps_per_chan=N)

        reader.ai_channels.add_ai_voltage_chan(format_channel(
            config['devices']['daq-card']['id'],
            config['devices']['daq-card']['ai']['field-set-measure']))
        reader.timing.cfg_samp_clk_timing(rate, source=trigger, active_edge=Edge.FALLING, samps_per_chan=N)
        
        setH = np.linspace(0,100,N)/100

        writer.write(setH)        
        
        reader.start()
        writer.start()
        clock.start()
        
        read = reader.read(number_of_samples_per_channel=N, timeout=40)
        
        np.savetxt('./measurement/test_{}.csv'
            .format(strftime("%Y-%m-%d_%H-%M-%S")), 
            np.array(read), delimiter=',',
            header='H-Field from {hmin} to {hmax} at {hf} and sampled \
            with {hs}'.format(hmin=setH[0], hmax=setH[-1], hf=10, hs=100)
        )

    
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