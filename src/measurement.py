import logging
import numpy as np
import yaml
from time import sleep, strftime

import os, sys

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.measurement as m


class FMRMeasurement:
    def __init__(self, _path) -> None:
        try:
            with open(_path, 'r') as f:
                self.cfg = yaml.safe_load(f)
            logging.info('loaded config file from {}'.format(_path))
        except yaml.YAMLError as e:
            logging.error('failed to load config from {}. Error: {}'.format(_path, e))
        
        self.f_name = '{name}_{timestamp}'.format(name=self.cfg['name'], timestamp=strftime("%Y-%m-%d_%H-%M-%S"))

    def setup_rf():
        pass

    def setup_daq_inputs(self, _ch):
        pass

    def setup_daq_outpus(self, _ch):
        pass

    def setup_daq_clk(self):
        pass


