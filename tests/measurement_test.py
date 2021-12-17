import unittest
import os, sys
import numpy as np
import pyvisa as vi
import logging
from nidaqmx.constants import Edge, TaskMode


parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.measurement as m

class FMRComposedTest(unittest.TestCase):

    def output(self) -> None:
        logging.basicConfig(filename='./log/test.log', filemode='w', level=logging.DEBUG)

        rm = vi.ResourceManager()
        
        param = {
            'rf-freq': 2,
            'rf-p': 0,
            'rf-rm': rm,    # vi resource manager
            'rf-conf': './config/hp83508.yaml',
            'H-set': np.linspace(0,100,2000)/100,
            'N': 2000,
            'rate': 1000,
            'name': 'fmr-test',
            'daq-dev': 'Dev1',
            'ai': {'set-field-m':'ai1', 'garbage':'ai0'},
            'ao': ['ao0'],
            'impuls': 'ctr0',
            'trigger': 'Ctr0InternalOutput',
            'mode': TaskMode.TASK_COMMIT,
            'read-edge': Edge.FALLING,
            'write-edge': Edge.RISING,
            'read-timeout': 30,
            'buffer-size': 200
        }

        self.meas = m.FMRMeasurement(param)
        self.meas.cfg_measurement()
        self.meas.start_measurement()

        
    def test_output(self):
        self.output()
        self.assertTrue(os.path.isfile(self.meas.f_name),
            "Measurement file created.")        

if __name__ == '__main__':
    unittest.main()