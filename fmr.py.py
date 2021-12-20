import os
import logging
import numpy as np
import pyvisa as vi
import src.visa_devices as devs
import src.measurement as m
import yaml
import nidaqmx as daq
from time import sleep
import matplotlib.pyplot as plt
from nidaqmx.constants import Edge, TaskMode
import threading

def measure(_meas):
    _meas.cfg_measurement()
    _meas.start_measurement()
    _meas.release_resources()
    
def plotter(_fname, _params):
    to_plot = os.path.isfile(_fname)
    while not to_plot:
        sleep(.2)
        to_plot = os.path.isfile(_fname)
    
    reps = int(_params['N']/_params['buffer-size'])
    plt_pause = _params['buffer-size']/_params['rate']

    plt.axis([0,10,0,1])
    print('plotting {} times'.format(reps))
    for i in range(reps):
        plt.cla()
        r = np.genfromtxt(_fname, delimiter=',', names=True, skip_header=3)
        for name in r.dtype.names:
            plt.plot(r[name], label=name)

        plt.legend(loc='upper left')    
        plt.grid()    
        plt.pause(plt_pause)
    plt.show()

def plotter_subs(_fname, _params):
    to_plot = os.path.isfile(_fname)
    while not to_plot:
        sleep(.2)
        to_plot = os.path.isfile(_fname)
    
    reps = int(_params['N']/_params['buffer-size'])
    plt_pause = _params['buffer-size']/_params['rate']

    fig, (field, lock) = plt.subplots(2, 1)
    
    for i in range(reps):
        field.cla()
        lock.cla()
        r = np.genfromtxt(_fname, delimiter=',', names=True, skip_header=3)
        row_names = r.dtype.names
        field.plot(r[row_names[0]],'g--', label=row_names[0])
        field.plot(r[row_names[1]],'r', label=row_names[1])
        lock.plot(r[row_names[2]], label=row_names[2])
        lock.plot(r[row_names[3]], label=row_names[3])
        field.legend(loc='upper left')
        field.grid()
        lock.legend(loc='upper left')
        lock.grid()
        plt.pause(plt_pause)
    plt.show(block=False)
    plt.pause(2)
    plt.close()

def main():
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.DEBUG)
    logging.info('Started in main()')
    
    rm = vi.ResourceManager()
    wave = m.WaveForm(200, 1000, 0.1)
    saw2 = wave.triangle_10()
    
    param = load_config('./recipes/fmr_1.yaml')
    param.update({'mode': TaskMode.TASK_COMMIT,
            'read-edge': Edge.FALLING,
            'write-edge': Edge.RISING,
            'H-set': saw2,
            'dir': './testmeasure'})
    meas = m.FMRMeasurement(param)
    name, params = meas.f_name, meas.params
    tr = threading.Thread(target=measure, args=(meas,))
    tr.start()
        
    plotter_subs(name, params)
    
    
    
def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


if __name__ == '__main__':
    main()