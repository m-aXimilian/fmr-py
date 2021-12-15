import logging
import numpy as np
import yaml

import os, sys

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.measurement as m


class FMRMeasure:
    def __init__(self, _path) -> None:
        try:
            with open(_path, 'r') as f:
                self.cfg = yaml.safe_load(f)
            logging.info('loaded config file from {}'.format(_path))
        except yaml.YAMLError as e:
            logging.error('failed to load config from {}. Error: {}'.format(_path, e))


