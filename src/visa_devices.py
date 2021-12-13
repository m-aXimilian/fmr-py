from nidaqmx.task import Task
import pyvisa as vi
import numpy as np
import logging
import nidaqmx as daq

class HP83508:
    """Wrapper for HP83508 RF-source functions"""

    def __init__(self, _rm, _id='') -> None:
        """Open a resource from the _ID string and the resource manager 
        _RM and save the resource object to ID."""
        if _id == '': 
            return
        logging.info('RF-Generator with ID {} generated'.format(_id))
        self.id = _rm.open_resource(_id)
    

    
    def setF(self, _f) -> None:
        """Takes a desired set-frequency _F (GHz) and sends it to the device."""
        if _f < 2 or _f > 26:
            return
        logging.info('Set f to {}GHz'.format(_f))
        self.id.write("cw {} GZ".format(round(_f, 4)))



    def setP(self, _p) -> None:
        """Takes a desired set-power _P (dBm) and sends it to the device."""
        if _p < -10 or _p > 10:
            return
        logging.info('Set P to {}dBm'.format(_p))
        self.id.write("pl {} DM".format(round(_p,1)))



class NIUSB6259:
    def __init__(self) -> None:
        pass



    def ai_volt_mult(self, _dev, _ch, _s) -> np.array:
        """Read _S samples of analog voltage for each of the channels passed in the 
        _CH dir on device _DEV."""
        if isinstance(_ch, str):
            logging.debug('A dictionary of channels must be passed to function {}'.
                format(self.ai_volt_mult.__name__))
            return
        
        with daq.Task() as task:
            for c in _ch.values():
                task.ai_channels.add_ai_voltage_chan(
                    '{dev}/{ch}'.format(
                        dev = _dev,
                        ch = c)
                )
            dat = task.read(number_of_samples_per_channel=_s)
        logging.debug('generated {} numpy array'.format(np.array(dat).shape))
        self.last_ai_read = np.array(dat)
        
        return self.last_ai_read



    def ai_volt_single(self, _dev, _ch, _s) -> np.array:
        """Read _S samples of analog voltage for the channel passed in _CH on device _DEV."""
        if not isinstance(_ch, str):
            logging.debug('A string must be passed to the channel in function {}'
                .format(self.ai_volt_single.__name__))
            return
        
        with daq.Task() as task:
            task.ai_channels.add_ai_voltage_chan(
                '{dev}/{ch}'.format(dev = _dev, ch = _ch)
            )
            dat = task.read(number_of_samples_per_channel=_s)
        self.last_ai_read = np.array(dat)

        return self.last_ai_read