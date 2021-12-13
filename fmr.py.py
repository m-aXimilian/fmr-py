from os import execlp
import logging
import pyvisa as vi
import visa_devices as devs
import yaml
import nidaqmx


def main():
    config = load_config('./config/init.yaml')
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.INFO)
    logging.info('Started in main()')
    rm = vi.ResourceManager()
    print(config)
    rf = devs.HP83508(rm, config['devices']['rf-generator']['id'])
    #rf.setF(3)

def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

if __name__ == '__main__':
    main()