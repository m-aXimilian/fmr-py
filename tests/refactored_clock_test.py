import os, sys
import logging
from nidaqmx.constants import Edge, TaskMode
from nidaqmx import stream_readers, stream_writers, constants
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
    samples_per_buffer = int(N/100)
    
    
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
    read.config_sample_clk(rate, clock.trigger, Edge.FALLING, N, constants.AcquisitionType.CONTINUOUS)

    read.task.in_stream.input_buf_size = samples_per_buffer * 10

    in_stream = stream_readers.AnalogSingleChannelReader(read.task.in_stream)
    out_stream = stream_writers.AnalogSingleChannelWriter(read.task.out_stream)

    setH = np.linspace(0,100,N)/100

    write.analog_write(setH)

    
    def read_callback(task_handle, event_type, num_samples, callback_data=None):
        buff=np.zeros(num_samples, dtype=np.float32)
        #in_stream.read_many_sample(buff, num_samples, timeout=constants.WAIT_INFINITELY)
        read.task.in_stream.readinto(buff)
        data =  buff.T.astype(np.float32)
        print(data)
        return 0
    
    read.task.register_every_n_samples_acquired_into_buffer_event(samples_per_buffer, read_callback)

    read.start()
    write.start()
    clock.start()

    input('keep it busy\n')

    """
    out = read.analog_read_n(N, timeout)

    np.savetxt('./measurement/test_{}.csv'
        .format(strftime("%Y-%m-%d_%H-%M-%S")), 
        np.array(out), delimiter=',',
        header='H-Field from {hmin} to {hmax} at {hf} and sampled \
        with {hs}'.format(hmin=setH[0], hmax=setH[-1], hf=10, hs=100)
    )
    """
def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

if __name__ == '__main__':
    main()