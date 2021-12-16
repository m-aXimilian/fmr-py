import logging
import numpy as np
import yaml
import pyvisa as vi
from time import sleep, strftime
import numpy as np
from nidaqmx import stream_readers

import os, sys

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs



class FMRHandler:
    """
    {
        'rf-freq': 2,
        'rf-p': 0,
        'rf-rm': rm,    # vi resource manager
        'rf-conf': './config/hp83508.yaml',
        'H-set': np.linspace(0,100)/100,
        'N': 10000,
        'rate': 1000,
        'name': 'test',
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
    """
    def __init__(self) -> None:
        self.measurements = []
    

    def single_f_measurement() -> None:
        pass

    
    def sweep_f_measurement() -> None:
        pass


class FMRMeasurement:
    """
    Container for a single measuremnt process (channels, frequency etc. can NOT be reconfigured).
    """
    def __init__(self, _params) -> None:
        """
        _PARAMS dictionary must contain the following
            {
            'rf-freq': 2,
            'rf-p': 0,
            'rf-rm': rm,    # vi resource manager
            'rf-conf': './config/hp83508.yaml',
            'H-set': np.linspace(0,100)/100,
            'N': 10000,
            'rate': 1000,
            'name': 'test',
            'daq-dev': 'Dev1',
            'ai': ['ai0', 'ai1'],
            'ao': ['ao0'],
            'impuls': 'ctr0',
            'trigger': 'Ctr0InternalOutput',
            'mode': TaskMode.TASK_COMMIT,
            'read-edge': Edge.FALLING,
            'write-edge': Edge.RISING,
            'read-timeout': 30,
            } 
        """
        self.params = _params
        self.f_name = './measurement/{n}-{f}GHz_{t}.csv'.format(
            n=self.params['name'],
            f=self.params['rf-freq'],
            t=strftime("%Y-%m-%d_%H-%M-%S"))
        self.daq_tasks = {}

    def setup_rf(self) -> None:
        """Sets up the RF-source with the paramters from self.PARAMS (dict)"""
        self.rf = devs.HP83508(self.params['rf-rm'], self.params['rf-conf'])
        self.rf.setF(self.params['rf-freq'])
        self.rf.setP(self.params['rf-p'])
        

    def setup_daq_inputs(self) -> None:
        """Sets up the DAQ input with the paramters from self.PARAMS (dict)"""
        self.daq_tasks.update(
            {'reader' : devs.NIUSB6259()}
        )

        self.daq_tasks['reader'].add_channels(
            self.params['daq-dev'], self.params['ai'], _type='ai'
        )

        self.daq_tasks['reader'].config_sample_clk(
            self.params['rate'], 
            self.daq_tasks['clock'].trigger, 
            self.params['read-edge'],
            self.params['N']
        )

        self.in_channels = len(self.daq_tasks['reader'].task.channels)
        self.in_stream = stream_readers.AnalogMultiChannelReader(
            self.daq_tasks['reader'].task.in_stream
        )


    def setup_daq_outputs(self) -> None:
        """Sets up the DAQ output with the paramters from self.PARAMS (dict)"""
        self.daq_tasks.update(
            {'writer' : devs.NIUSB6259()}
        )

        self.daq_tasks['writer'].add_channels(
            self.params['daq-dev'], self.params['ao'], _type='ao'
        )

        self.daq_tasks['writer'].config_sample_clk(
            self.params['rate'], 
            self.daq_tasks['clock'].trigger, 
            self.params['write-edge'],
            self.params['N']
        )


    def setup_daq_clk(self) -> None:
        """Sets up the DAQ clock and trigger with the paramters from self.PARAMS (dict)"""
        self.daq_tasks.update(
            {'clock' : devs.NIUSB6259()}
        )

        self.daq_tasks['clock'].config_clk(
            self.params['daq-dev'],
            self.params['impuls'],
            self.params['rate'],
            self.params['N'],
            self.params['mode']
        )

        self.daq_tasks['clock'].set_trigger(
            self.params['daq-dev'],
            self.params['trigger'])


    def start_measurement(self) -> None:
        """Start a measurement. Depends on :func:`~self.setup_daq_inputs`
        :func:`~self.setup_daq_outputs` and :func:`~self.setup_daq_clk`.
        I.e. will raise an error if those were not called before."""
        with open('./config/daq_limits.yaml', 'r') as f:
            limits = yaml.safe_load(f)
            if max(abs(self.params['H-set'])) > limits['max-v-output']:
                raise ValueError('Set field exeeds limits!')
                
        self.daq_tasks['writer'].analog_write(self.params['H-set'])

        self.daq_tasks['reader'].start()
        self.daq_tasks['writer'].start()
        self.daq_tasks['clock'].start()

        out = self.daq_tasks['reader'].analog_read_n(
            self.params['N'],
            self.params['read-timeout']
        )

        self.write_results(out)


    def write_results(self, _arr):
        """Writes the array _ARR to the file path provided in """
        meta = 'H-field ramp:\t{hlow} to {hup}\n \
                f:\t{f}\n \
                samples:\t{n}'.format(
                    hlow=min(self.params['H-set']),
                    hup=min(self.params['H-set']),
                    f=self.params['rf-freq'],
                    n=self.params['N']
                )
        
        np.savetxt(self.f_name, 
            np.array(_arr), delimiter=',',
            header=meta)
        


