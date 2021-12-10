import pyvisa as vi

rm = vi.ResourceManager()

print(rm.list_resources())

