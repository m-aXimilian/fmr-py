import pyvisa as vi
import nidaqmx

class HP83508:
    """Wrapper for HP83508 RF-source functions"""

    def __init__(self, _rm, _id='') -> None:
        """Open a resource from the _ID string and the resource manager 
        _RM and save the resource object to ID."""
        if _id == '': 
            return
        self.id = _rm.open_resource(_id)
    
    def setF(self, _f) -> None:
        """Takes a desired set-frequency _F (GHz) and sends it to the device."""
        if _f < 2 or _f > 26:
            return
        self.id.write("cw {} GZ".format(round(_f, 4)))

    def setP(self, _p) -> None:
        """Takes a desired set-power _P (dBm) and sends it to the device."""
        if _p < -10 or _p > 10:
            return
        self.id.write("pl {} DM".format(round(_p,1)))

class NIUSB6259:
    def __init__(self, _rm, _id='') -> None:
        pass

