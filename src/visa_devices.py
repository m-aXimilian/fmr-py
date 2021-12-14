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
        self.task = daq.Task()


    def __del__(self) -> None:
        self.task.close()
    

    def __restart(self) -> None:
        self.task.close()
        self.task = Task()


    def __format_channel(self, _dev, _ch) -> str:
        return '{dev}/{ch}'.format(dev = _dev, ch = _ch)

    


    def ai_volt_mult(self, _dev, _ch, _s, _r) -> np.array:
        """Read _S samples of analog voltage for each of the channels passed in the 
        _CH dir on device _DEV at rate _R (Hz)."""
        if isinstance(_ch, str):
            logging.debug('A dictionary of channels must be passed to function {}'.
                format(self.ai_volt_mult.__name__))
            return

        for c in _ch.values():
            tmp_c = self.__format_channel(_dev, c)

            if (tmp_c in self.task.channel_names): return

            self.task.ai_channels.add_ai_voltage_chan(tmp_c)

        self.task.timing.cfg_samp_clk_timing(_r)
        dat = self.task.read(number_of_samples_per_channel=_s)
        self.last_ai_read = np.array(dat)
        
        logging.debug('generated {} numpy array'.format(self.last_ai_read.shape))
        
        return self.last_ai_read


    def ai_volt_single(self, _dev, _ch, _s, _r) -> np.array:
        """Read _S samples of analog voltage for the channel passed in _CH on device _DEV
        at rate _R (Hz)."""
        if not isinstance(_ch, str):
            logging.debug('A string must be passed to the channel in function {}'
                .format(self.ai_volt_single.__name__))
            return
        
        tmp_c = self.__format_channel(_dev, _ch)

        if not (tmp_c in self.task.channel_names):
            self.task.ai_channels.add_ai_voltage_chan(tmp_c)

        self.task.timing.cfg_samp_clk_timing(_r)
        dat = self.task.read(number_of_samples_per_channel=_s)
        self.last_ai_read = np.array(dat)

        logging.debug('generated {} numpy array'.format(self.last_ai_read.shape))

        return self.last_ai_read


    def ao_write_single(self, _dev, _ch, _s) -> int:
        pass

