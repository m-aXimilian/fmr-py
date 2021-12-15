import unittest
import os, sys

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs
import src.measurement as m

class FMRMeasureTest(unittest.TestCase):

    #@unittest.skip()
    def test_init(self):
        self.assertIsNotNone(m.FMRMeasure)
    
    def test_config_right(self):
        meas = m.FMRMeasure('./config/fmr_1.yaml')
        self.assertIsNotNone(meas.cfg)

    def test_filename(self):
        meas = m.FMRMeasure('./config/fmr_1.yaml')
        self.assertIsNotNone(meas.f_name)


if __name__ == '__main__':
    unittest.main()