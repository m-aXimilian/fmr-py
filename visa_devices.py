import pyvisa as vi

class HP83508:

    def __init__(self, _rm, _id='') -> None:
        if _id == '': 
            return
        self.id = _rm.open_resource(_id)
    
    def setF(self, _f) -> None:
        if _f < 2 or _f > 26:
            return
        self.id.write("cw {} GZ".format(round(_f, 4)))

    def setP(self, _p) -> None:
        if _p < -10 or _p > 10:
            return
        self.id.write("pl {} DM".format(round(_p,1)))

class NIUSB6259:
    def __init__(self, _rm, _id='') -> None:
        pass       

