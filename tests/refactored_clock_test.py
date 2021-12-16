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
import matplotlib.animation as anima
import threading


parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs


def main():
    clock = devs.NIUSB6259()
    write = devs.NIUSB6259()
    read = devs.NIUSB6259()
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/test.log', filemode='w', level=logging.DEBUG)

    rate, N = 1000, 1000
    bufsize = 200
    interval = rate/bufsize

    fname = './measurement/{n}-{f}GHz_{t}.csv'.format(
                n='cont_t',
                f=0,
                t=strftime("%Y-%m-%d_%H-%M-%S"))

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
                config['devices']['daq-card']['ai'], _type='ai')
    read.config_sample_clk(rate, clock.trigger, Edge.FALLING, N)

    #read.task.in_stream.input_buf_size = samples_per_buffer * 10

    in_stream = stream_readers.AnalogMultiChannelReader(read.task.in_stream)
    

    setH = np.linspace(0,100,N)/100

    write.analog_write(setH)

    results = {'samples': []}
    
    
    def read_callback(task_handle, event_type, num_samples, callback_data=None):
        buf=np.zeros((5,num_samples))
        in_stream.read_many_sample(buf,num_samples)
        write_out(fname,buf.T, 'one,two,three,four,five')
        #data = read.task.read(num_samples)
        #results['samples'].extend(data)
        #write_out(fname, np.array(data).T)
        #print('{}\n{}\n'.format(len(results['samples']), len(data)))
        return 0
    
    read.task.register_every_n_samples_acquired_into_buffer_event(bufsize, read_callback)

    read.start()
    write.start()
    clock.start()

        
    print('measurement will take {}s\n'.format(meas_time))
    print(len(read.task.channels))
    sleep(meas_time)
    

def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

def write_out(_f, _arr, _h):
    with open(_f, 'a') as f:
        np.savetxt(f, _arr, delimiter=',',header=_h)


def live_plt(_f, _i):

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    while not os.path.exists(_f):
        sleep(.5)

    def animate(_i, _arr):
        ax.clear()
        ax.plot(_arr)
    
    with open(_f) as f:
        data = np.loadtxt(_f, delimiter=',')
        an = anima.FuncAnimation(fig, animate, fargs=data, interval=_i)
        plt.show()

    






if __name__ == '__main__':
    main()