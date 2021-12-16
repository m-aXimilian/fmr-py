import os, sys
import logging
from nidaqmx.constants import Edge, TaskMode
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


def main():
    clock = devs.NIUSB6259()
    write = devs.NIUSB6259()
    read = devs.NIUSB6259()
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/test.log', filemode='w', level=logging.DEBUG)

    rate, N = 1000, 10000
    bufsize = 1000

    meas_time = N/rate
    
    clock.config_clk(_dev=config['devices']['daq-card']['id'],
                _ch=config['devices']['daq-card']['ctr']['impuls-1'],
                _r=rate, _t=N, _m=TaskMode.TASK_COMMIT)
    clock.set_trigger(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['trigger']['impuls-1'])

    write.add_channels(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ao']['set-value-small'], _type='ao')
    write.config_sample_clk(rate, clock.trigger, Edge.RISING, N)

    read.add_channels(config['devices']['daq-card']['id'],
                config['devices']['daq-card']['ai']['field-set-measure'], _type='ai')
    read.config_sample_clk(rate, clock.trigger, Edge.FALLING, N)

    #read.task.in_stream.input_buf_size = samples_per_buffer * 10

    in_stream = stream_readers.AnalogSingleChannelReader(read.task.in_stream)
    out_stream = stream_writers.AnalogSingleChannelWriter(read.task.out_stream)

    setH = np.linspace(0,100,N)/100

    write.analog_write(setH)

    results = {'samples': []}
    
    def read_callback(task_handle, event_type, num_samples, callback_data=None):
        #buff=np.zeros(num_samples*10, dtype=np.float32)
        #in_stream.read_many_sample(buff, num_samples, timeout=constants.WAIT_INFINITELY)
        #read.task.in_stream.readinto(buff)
        #data =  buff.T.astype(np.float32)
        #results['samples'].extend(data)

        data = read.task.read(num_samples)
        results['samples'].extend(data)
        print('{}\n{}\n'.format(len(results['samples']), len(data)))
        return 0
    
    read.task.register_every_n_samples_acquired_into_buffer_event(bufsize, read_callback)

    read.start()
    write.start()
    clock.start()

    print('measurement will take {}s\n'.format(meas_time))
    sleep(meas_time)

    plt.plot(results['samples'])
    plt.show()
    

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