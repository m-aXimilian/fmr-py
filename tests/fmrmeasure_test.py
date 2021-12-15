import unittest
import os, sys
import numpy as np
import visa as vi
from nidaqmx.constants import Edge, TaskMode


parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs
import src.measurement as m

class FMRMeasureTest(unittest.TestCase):
    rm = vi.ResourceManager()
    par = {
        'rf-freq': 3,
        'rf-p': 0,
        'rf-rm': rm,    # vi resource manager
        'rf-conf': './config/hp83508.yaml',
        'H-set': np.linspace(0,100,1000)/100,
        'N': 1000,
        'rate': 1000,
        'name': 'test',
        'daq-dev': 'Dev1',
        'ai': ['ai1'],
        'ao': ['ao0'],
        'impuls': 'ctr0',
        'trigger': 'Ctr0InternalOutput',
        'mode': TaskMode.TASK_COMMIT,
        'read-edge': Edge.FALLING,
        'write-edge': Edge.RISING,
        'read-timeout': 30,
    }
    meas = m.FMRMeasurement(par)
    #@unittest.skip()
    def test_init(self):
        self.assertIsNotNone(m.FMRMeasurement)
    
    def test_config_right(self):
        self.assertIsNotNone(self.meas.params)

    def test_filename(self):
        self.assertIsNotNone(self.meas.f_name)

    def test_setup_rf(self):
        # won't pass when RF-generator is not connected and running!
        self.assertIsNone(self.meas.setup_rf())

    def test_setup_daq_inputs(self):
        self.meas.setup_daq_clk()
        self.assertIsNone(self.meas.setup_daq_inputs())

    def test_setup_daq_outputs(self):
        self.meas.setup_daq_clk()
        self.assertIsNone(self.meas.setup_daq_outputs())

    def test_setup_daq_clk(self):
        self.assertIsNone(self.meas.setup_daq_clk())
    
    def test_start_measurement(self):
        self.meas.setup_daq_clk()
        self.meas.setup_daq_inputs()
        self.meas.setup_daq_outputs()
        self.assertIsNone(self.meas.start_measurement())




if __name__ == '__main__':
    unittest.main()