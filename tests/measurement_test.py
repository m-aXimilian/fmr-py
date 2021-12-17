import os, sys
import numpy as np
import pyvisa as vi
import logging
from nidaqmx.constants import Edge, TaskMode


parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.measurement as m

def main() -> None:
    logging.basicConfig(filename='./log/test.log', filemode='w', level=logging.DEBUG)

    rm = vi.ResourceManager()
    
    param = {
        'rf-freq': 2,
        'rf-p': 0,
        'rf-rm': rm,    # vi resource manager
        'rf-conf': './config/hp83508.yaml',
        'H-set': np.linspace(0,100,10000)/100,
        'N': 200000,
        'rate': 1000,
        'name': 'fmr-test',
        'daq-dev': 'Dev1',
        'ai': ['ai0', 'ai1'],
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


if __name__ == '__main__':
    main()