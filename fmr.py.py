import pyvisa as vi
import visa_devices as devs

rm = vi.ResourceManager()

print(rm.list_resources())

rf = devs.HP83508(rm, 'GPIB0::19::INSTR')

rf.setF(3)
