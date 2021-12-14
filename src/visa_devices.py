from nidaqmx.task import Task
import pyvisa as vi
import numpy as np
import logging
import nidaqmx as daq
import yaml

class HP83508:
    """Wrapper for HP83508 RF-source functions"""
    def __init__(self, _rm, _id='') -> None:
        """Open a resource from the _ID string and the resource manager 
        _RM and save the resource object to ID."""
        if _id == '': 
            return
        logging.info('RF-Generator with ID {} generated'.format(_id))
        self.id = _rm.open_resource(_id)
        with open('./config/hp83508.yaml','r') as f:
            try:
                self.boundaries = yaml.safe_load(f)['boundaries']
            except yaml.YAMLError as e:
                logging.debug('in HP83508 __init__ code: {}'.format(e))
    

    def setF(self, _f) -> None:
        """Takes a desired set-frequency _F (GHz) and sends it to the device."""
        if _f < self.boundaries['f-min'] or _f > self.boundaries['f-max']:
            logging.info('Set-frequency {}GHz outside boundaries'.format(_f))
            return
        logging.info('Set f to {}GHz'.format(_f))
        self.id.write("cw {} GZ".format(round(_f, 4)))


    def setP(self, _p) -> None:
        """Takes a desired set-power _P (dBm) and sends it to the device."""
        if _p < self.boundaries['p-min'] or _p > self.boundaries['p-max']:
            logging.info('Set-power {}dBm outside boundaries'.format(_p))
            return
        logging.info('Set P to {}dBm'.format(_p))
        self.id.write("pl {} DM".format(round(_p,1)))



class NIUSB6259:
    """Wrapper for the NI USB6259 DAQ card."""
    def __init__(self) -> None:
        self.task = daq.Task()


    def __del__(self) -> None:
        self.task.close()
    

    def __format_channel(self, _dev, _ch) -> str:
        """Compose a string for passing to the nidaqmx-API functions from 
        the device ID _DEV and the channel _CH."""
        return '{dev}/{ch}'.format(dev = _dev, ch = _ch)
    
    
    def __get_add_channel(self, _type='ai'):
        """Returns the appropriate function for adding a channel to 
        the task based on the type _TYPE of the channel."""
        if _type == 'ai':
            return self.task.ai_channels.add_ai_voltage_chan
        if _type == 'ao':
            return self.task.ao_channels.add_ao_voltage_chan
        if _type == 'di':
            return self.task.di_channels.add_di_chan
        if _type == 'do':
            return self.task.do_channels.add_do_chan


    def add_channels(self, _dev, _ch, _type='ai') -> None:
        """_CH can be of type dict, list or string. Contents are added as 
        ai_voltage_channels to the device _DEV."""

        add_fun = self.__get_add_channel(_type)
                               
        if isinstance(_ch, str):
            tmp_c = self.__format_channel(_dev, _ch)
            add_fun(tmp_c)
            logging.debug('Channel {} added'.format(_ch))
            return

        t = type(_ch)
        if issubclass(t, dict):
            channels = _ch.values()
        if issubclass(t, list):
            channels = _ch
         
        for c in channels:
            tmp_c = self.__format_channel(_dev, c)
            logging.debug('adding channel {}'.format(tmp_c))
            add_fun(tmp_c)


    def config_clk(self, _r) -> None:
        """Set the sample rate _R (Hz)."""
        if not self.task.channel_names:
            logging.debug('No channels added to set a clock for')
            return
        self.rate = _r
        logging.debug('Sample rate set to {} Hz'.format(_r))
        self.task.timing.cfg_samp_clk_timing(_r)

    
    def analog_read_n(self, _s) -> np.array:
        """Read _S numbers of samples from the configured input channels and return
        them in an array."""
        if not self.task.channel_names:
            logging.debug('No channels added to read from. {}'.format(self.analog_read.__name__))
            return
        
        print('Read will take {}ms'.format(_s / self.rate * 1000))
        tmp = self.task.read(number_of_samples_per_channel=_s)
        return np.array(tmp)
    
    def analog_wirte(self, _arr) -> None:
        print('writing {}'.format(_arr))
        self.task.write(_arr, auto_start=True)

       

    

