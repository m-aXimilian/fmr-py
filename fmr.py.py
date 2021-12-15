from os import device_encoding, execlp
import logging
import numpy as np
import pyvisa as vi
import src.visa_devices as devs
import yaml
import nidaqmx as daq
import time


def main():
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.DEBUG)
    logging.info('Started in main()')
    rm = vi.ResourceManager()
    rf = devs.HP83508(rm,'./config/hp83508.yaml')
    rf.setF(4)
    
    
    
def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


if __name__ == '__main__':
    main()