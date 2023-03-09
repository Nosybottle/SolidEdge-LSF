import win32com.client
from solidedge.comwrapper import COMWrapper

# Load libraries
seConstants = win32com.client.gencache.EnsureModule("{C467A6F5-27ED-11D2-BE30-080036B4D502}", 0, 1, 0).constants
seGeometry = win32com.client.gencache.EnsureModule('{3E2B3BE1-F0B9-11D1-BDFD-080036B4D502}', 0, 1, 0)

# Connect to Solid Edge
app = win32com.client.GetActiveObject("SolidEdge.Application")

# Wrap COM objects
seConstants = COMWrapper(seConstants)
seGeometry = COMWrapper(seGeometry)
app = COMWrapper(app)
