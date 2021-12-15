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

    """
    with daq.Task() as reader, daq.Task() as writer:
        writer.ao_channels.add_ao_voltage_chan('Dev1/'+ config['devices']['daq-card']['ao']['set-value-small'])
        reader.ai_channels.add_ai_voltage_chan('Dev1/'+ config['devices']['daq-card']['ai']['field-set-measure'])
        setH = list(range(0,100))
        setH = np.array([(lambda n: n/100)(e) for e in setH])
        rate=100000

        read = []
        for v in setH:
            writer.write(v)
            time.sleep(1/rate)
            read.append(reader.read())
        
        np.savetxt('./measurement/test2.csv', np.array(read), delimiter=',',
        header='H-Field from {hmin} to {hmax} at {hf} and sampled \
            with {hs}'.format(hmin=setH[0], hmax=setH[-1], hf=10, hs=100)
        )




    daq_card1 = devs.NIUSB6259()
    daq_card2 = devs.NIUSB6259()
    
    
    daq_card1.add_channels(
        config['devices']['daq-card']['id'],
        config['devices']['daq-card']['ai'],
        _type='ai')

    daq_card2.add_channels(
        config['devices']['daq-card']['id'],
        config['devices']['daq-card']['ao']['set-value-small'],
        _type='ao')

    daq_card1.config_clk(1000)
    daq_card2.config_clk(1000)
    
    setH = np.linspace(0, 99, 19000, 100)/100
    
    out = daq_card1.analog_read_n(19000)
    daq_card2.analog_wirte(setH)
    
    np.savetxt('./measurement/test.csv', out, delimiter=',',
        header='H-Field from {hmin} to {hmax} at {hf} and sampled \
            with {hs}'.format(hmin=setH[0], hmax=setH[-1], hf=10, hs=100)
        )
    """
    
    
    
def load_config(file_path):
    with open(file_path,"r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


if __name__ == '__main__':
    main()