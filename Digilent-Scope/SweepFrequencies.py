from dwfconstants import *
import time
import sys
from math import*
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch
# Loading library for connecting to device
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")
# Declare ctype variables
IsInUse = c_bool()
dev0 = c_int(0)             # device 0: outputs 1 signal, 2 inputs
# dev1 = c_int(0)             # device 1: 1 input only
cdevices = c_int()
def custom_waveform(freqarr, shiftarr, amplitude, simulated_sampling_rate, time_length):
    # choose some high number for simulated sampling rate, we will create 0.01 seconds worth, or whatever time_length is
    # Define the waveform for 100Hz - 1500Hz ------------------------------
    simulated_num_samples = int(simulated_sampling_rate * time_length)
    rgdSamples = (c_double * simulated_num_samples)()
    # For a 100-1500Hz section, e.g., each cycle will be time_length seconds long
    # Sample rate = frequency * number of samples
    for t in range(simulated_num_samples):
        sumfreq = 0
        for j in range(len(shiftarr)):
            sumfreq += amplitude * sin(2 * pi * freqarr[j] * t / simulated_sampling_rate + shiftarr[j])
        rgdSamples[t] = sumfreq
        # t = [i/simulated_sampling_rate for i in range(simulated_num_samples)]
        # plt.plot(t, rgdSamples)
        # plt.show()
    return rgdSamples
def generate_samples(device, channel, rgdSamples, time_length):
    dwf.FDwfAnalogOutNodeEnableSet(device, channel, AnalogOutNodeCarrier, c_bool(True))
    dwf.FDwfAnalogOutNodeFunctionSet(device, channel, AnalogOutNodeCarrier, funcCustom)
    dwf.FDwfAnalogOutNodeDataSet(device, channel, AnalogOutNodeCarrier, rgdSamples, c_int(len(rgdSamples)))
    dwf.FDwfAnalogOutNodeFrequencySet(device, channel, AnalogOutNodeCarrier, c_double(1 / time_length))
    dwf.FDwfAnalogOutNodeAmplitudeSet(device, channel, AnalogOutNodeCarrier, c_double(1))
    dwf.FDwfAnalogOutConfigure(device, channel, c_bool(True))  # TURNS ON SIG GEN.

# Turn off the source output on the signal generator
def signal_off(channel):
    if channel == 0:
        dwf.FDwfAnalogOutConfigure(dev0, c_int(0), c_bool(False))
    elif channel == 1:
        dwf.FDwfAnalogOutConfigure(dev0, c_int(1), c_bool(False))
    resp = {
        "message": "Signal generator turned off for channel %s" % (channel)
    }
    return dumps(resp)
# START SCRIPT -----------------------------------------------------------------------------
# Show Devices Available
# Declare string variables
serialnum = create_string_buffer(16)
# Print DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: ", version.value)
# Enumerate and print device information
dwf.FDwfEnum(c_int(0), byref(cdevices))
print("Number of Devices: ", str(cdevices.value))
for i in range(0, cdevices.value):
    dwf.FDwfEnumSN(c_int(i), serialnum)
    print("------------------------------")
    print("Device ", str(i), " : ")
    print(str(serialnum.value))
    dwf.FDwfEnumDeviceIsOpened(c_int(i), byref(IsInUse))
    # Define device by serial number
    if str(serialnum.value) == "b'SN:210321A67C47'":
        dwf.FDwfDeviceOpen(c_int(i), byref(dev0))
print("------------------------------")
# Device 0: outputting signal from Device
if dev0.value == hdwfNone.value:
    print("failed to open 1st device")
    quit()
else:
    print("Device Connected! Waiting for signal...")

print("Generating signal...")
amp = 0.8
for freq in range(100,5000,10):
    rgdSamples = custom_waveform(freq, 0, amplitude=amp, simulated_sampling_rate=100000, time_length=0.01)
    generate_samples(dev0, c_int(0), rgdSamples, time_length=0.01)
    time.sleep(10)