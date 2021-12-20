from os import device_encoding, execlp
import logging
import numpy as np
import pyvisa as vi
import src.visa_devices as devs
import src.measurement as m
import yaml
import nidaqmx as daq
import time
from nidaqmx.constants import Edge, TaskMode
import threading

def measure():
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.DEBUG)
    logging.info('Started in main()')
    
    rm = vi.ResourceManager()
    
    param = {
        'rf-freq': 2,
        'rf-p': 0,
        'rf-rm': rm,    # vi resource manager
        'rf-conf': './config/hp83508.yaml',
        'h-max': 150,
        'N': 2000,
        'rate': 1000,
        'name': 'fmr-test',
        'daq-dev': 'Dev1',
        'ai': {'field-set-measure':'ai1', 'field-is-measure': 'ai2', 'x-value-lockin':'ai0', 'y-value-lockin': 'ai4', },
        'ao': ['ao0'],
        'impuls': 'ctr0',
        'trigger': 'Ctr0InternalOutput',
        'mode': TaskMode.TASK_COMMIT,
        'read-edge': Edge.FALLING,
        'write-edge': Edge.RISING,
        'read-timeout': 30,
        'buffer-size': 200
    }

    meas = m.FMRMeasurement(param)
    meas.cfg_measurement()
    meas.start_measurement()
    


def main():
    tr = threading.Thread(target=measure)
    tr.start()
    
    
def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


if __name__ == '__main__':
    main()