from re import L
from nidaqmx import constants
from nidaqmx.constants import TaskMode
from nidaqmx.task import Task
import pyvisa as vi
import numpy as np
import logging
import nidaqmx as daq
import yaml


class HP83508:
    """Wrapper for HP83508 RF-source functions. Open a resource from the _ID string and the resource manager 
        _RM and save the resource object to ID.

        Args:
            _rm (pyvisa.ResourceManager): resource manager for the HP83508 visa device
            _path (str): config-file for setting the name and the limits of the device.
        
        Raises:
            yaml.YAMLError: if the config file cannot be read properly
        """
    def __init__(self, _rm, _path) -> None:
        
        with open(_path,'r') as f:
            try:
                tmp = yaml.safe_load(f)
                self.boundaries = tmp['boundaries']
                logging.info('RF-Generator boundaries set to {}'.format(self.boundaries))
                self.id = _rm.open_resource(tmp['id'])
                logging.info('RF-Generator with ID {} generated'.format(self.id))
            except yaml.YAMLError as e:
                logging.debug('in HP83508 __init__ code: {}'.format(e))
    

    def setF(self, _f) -> None:
        """Takes a desired set-frequency and sends it to the device.

        Args:
            _f (float): set frequency in GHz
        """
        if _f < self.boundaries['f-min'] or _f > self.boundaries['f-max']:
            logging.info('Set-frequency {}GHz outside boundaries'.format(_f))
            return
        logging.info('Set f to {}GHz'.format(_f))
        self.id.write("cw {} GZ".format(round(_f, 4)))


    def setP(self, _p) -> None:
        """Takes a desired set-power and sends it to the device.

        Args:
            _p (float): set power in dBm
        """
        if _p < self.boundaries['p-min'] or _p > self.boundaries['p-max']:
            logging.info('Set-power {}dBm outside boundaries'.format(_p))
            return
        logging.info('Set P to {}dBm'.format(_p))
        self.id.write("pl {} DM".format(round(_p,1)))



class NIUSB6259:
    """Wrapper for the NI USB6259 DAQ card.
    """
    def __init__(self) -> None:
        self.task = daq.Task()

    
    def start(self) -> None:
        """Start a task. 
        """
        self.task.start()


    def __format_channel(self, _dev, _ch) -> str:
        """Compose a string for passing to the nidaqmx-API functions from 
        the device ID and the channel name.

        Args:
            _dev (str): device name
            _ch (str): channel name

        Returns:
            str: [description]
        """
        return '{dev}/{ch}'.format(dev = _dev, ch = _ch)
    
    
    def __get_add_channel(self, _type='ai'):
        """Returns the appropriate function for adding a channel to 
        the task based on the type of the channel.

        Args:
            _type (str, optional): type of the channel to add. Defaults to 'ai'.

        Returns:
            func: appropriate fuction for adding the channel
        """
        if _type == 'ai':
            return self.task.ai_channels.add_ai_voltage_chan
        if _type == 'ao':
            return self.task.ao_channels.add_ao_voltage_chan
        if _type == 'di':
            return self.task.di_channels.add_di_chan
        if _type == 'do':
            return self.task.do_channels.add_do_chan


    def add_channels(self, _dev, _ch, _type='ai') -> None:
        """Contents are added as voltage_channels of the specified type to the device.

        Args:
            _dev (str): device name
            _ch (str, dict, list): channels can be string, dictionary or list!
            _type (str, optional): channel type. Defaults to 'ai'.
        """

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


    def config_clk(self, _dev, _ch, _r, _t=1000, _m=TaskMode.TASK_COMMIT) -> None:
        """For a clock channel, set the sample rate _R (Hz) for device _DEV at channel _CH.
        Sets the implicit timing _T (=sample number per channel) and task mode _M as well.

        Args:
            _dev (str): device name
            _ch (str): channel name
            _r (float): sample rate (Hz)
            _t (int, optional): sample number per channel. Defaults to 1000.
            _m (nidaqmx.Task.TaskMode, optional): clock task mode. Defaults to TaskMode.TASK_COMMIT.
        """
        if not isinstance(_ch, str): return
        
        self.task.co_channels.add_co_pulse_chan_freq(
            self.__format_channel(_dev, _ch),
            freq=_r)
        
        self.task.timing.cfg_implicit_timing(samps_per_chan=_t)
        self.task.control(_m)


    def set_trigger(self, _dev, _ch) -> None:
        self.trigger = '/{}'.format(self.__format_channel(_dev, _ch))


    def config_sample_clk(self, _r, _trig, _edge, _s, _m=constants.AcquisitionType.FINITE) -> None:
        """Configure the the trigger and clock for IO-channels of task self.task.

        Args:
            _r (float): sample rate (Hz)
            _trig (str): trigger source channel
            _edge (nidaqmx.Edge): e.g. RISING or FALLING
            _s (int): number of samples
            _m (nidaqmx.constants.AquisitionType, optional): finite or continuous. Defaults to constants.AcquisitionType.FINITE.
        """
        self.rate = _r
        self.task.timing.cfg_samp_clk_timing(_r, source=_trig, active_edge=_edge, samps_per_chan=_s, sample_mode=_m)


    def analog_read_n(self, _s, _t) -> np.array:
        """Read _S numbers of samples from the configured input channels with timeout _T and return
        them in an array.

        Args:
            _s (int): number of samples
            _t (int): timeout (s)

        Returns:
            np.array: [description]
        """
        if not self.task.channel_names:
            logging.debug('No channels added to read from. {}'.format(self.analog_read.__name__))
            return
        
        print('Read will take {}ms'.format(_s / self.rate * 1000))
        tmp = self.task.read(number_of_samples_per_channel=_s, timeout=_t)
        return np.array(tmp)


    def analog_write(self, _arr) -> None:
        """Write the array to the specified output channel.

        Args:
            _arr (array): output array
        """
        self.task.write(_arr)



