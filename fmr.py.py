from os import execlp
import logging
import numpy as np
import pyvisa as vi
import src.visa_devices as devs
import yaml
import nidaqmx as daq


def main():
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.DEBUG)
    logging.info('Started in main()')
    #rm = vi.ResourceManager()
    #rf = devs.HP83508(rm, config['devices']['rf-generator']['id'])
    daq_card1 = devs.NIUSB6259()
    daq_card2 = devs.NIUSB6259()

    daq_card1.ai_volt_mult(
        config['devices']['daq-card']['id'],
        config['devices']['daq-card']['ai'],
        3,
        1000
    )

    print(daq_card1.last_ai_read)

    daq_card2.ai_volt_mult(
        config['devices']['daq-card']['id'],
        config['devices']['daq-card']['ai'],
        6,
        1000
    )

    print(daq_card2.last_ai_read)

      
def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


if __name__ == '__main__':
    main()