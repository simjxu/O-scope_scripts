from json import dumps
from dwfconstants import *
import time
from math import*
import sys
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
dev1 = c_int(0)             # device 1: 1 input only
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

def acquire_samples(device, channel, sampling_rate, nSamples):
# Acquire samples from device, channel and for however many samples
    cSamples = 0; cLost = c_int(); cCorrupted = c_int(); fLost = 0; fCorrupted = 0; cAvailable = c_int()
    sts = c_byte(); rgpy = [0.0] * nSamples
    # set up acquisition for device 0 channel 0
    dwf.FDwfAnalogInChannelEnableSet(device, channel, c_bool(True))      # Enable Analog in channel
    dwf.FDwfAnalogInChannelRangeSet(device, channel, c_double(8.0))      # Configure channel range
    dwf.FDwfAnalogInAcquisitionModeSet(device, acqmodeRecord)            # Perform acquisition for length of time RecordLengthSet
    dwf.FDwfAnalogInFrequencySet(device, sampling_rate)                          # Set sample rate of device
    dwf.FDwfAnalogInChannelOffsetSet(device, channel, c_double(0.0))     # Configure offset for channel
    # Define RecordLengthSet
    dwf.FDwfAnalogInRecordLengthSet(device, c_double(float(nSamples) / sampling_rate.value))
    dwf.FDwfAnalogInConfigure(device, c_bool(True), c_bool(True))
    time.sleep(0.3)                 # Wait for acquisition to settle
    # Temporary samples array
    tmpSamples = (c_double * int(nSamples))()  # creates array
    while cSamples < nSamples:
        dwf.FDwfAnalogInStatus(device, c_bool(True), byref(sts))
        if cSamples == 0 and (sts == DwfStateConfig or sts == DwfStatePrefill or sts == DwfStateArmed):
            # Acquisition not yet started.
            continue
        dwf.FDwfAnalogInStatusRecord(device, byref(cAvailable), byref(cLost), byref(cCorrupted))
        cSamples += cLost.value
        if cLost.value:
            fLost = 1
        if cCorrupted.value:
            fCorrupted = 1
        if cAvailable.value == 0:
            print("third if")
            continue
        if cSamples + cAvailable.value > nSamples:
            cAvailable = c_int(nSamples - cSamples)
        # get samples
        dwf.FDwfAnalogInStatusData(device, channel, byref(tmpSamples, cSamples * 8), cAvailable)
        cSamples += cAvailable.value
    if fLost:
        print(
        "Samples were lost! Reduce frequency")
    if cCorrupted:
        print(
        "Samples could be corrupted! Reduce frequency")
    # Save the values
    for i in range(0, nSamples):
        rgpy[i] = tmpSamples[i]
    # dwf.FDwfAnalogInConfigure(device, c_bool(False), c_bool(False))
    # dwf.FDwfAnalogInChannelEnableSet(device, channel, c_bool(False))
    return rgpy
# ------------ END acquire_samples() -------------------------------------------------------

def get_reference_values(collected_samples, freqarr, sampling_rate, num_samples, axis):
    # new_samples = collected_samples - np.mean(collected_samples)
    # print("new average:", np.mean(new_samples))

    # Divide by Reference 832M1 Sensitivities -----
    if axis == 1:
        volt = 0.059749
    elif axis == 2:
        volt = 0.042193
    elif axis == 3:
        # volt = 0.059289
        volt = 0.05166 # vot for 832m1 5581-044
    elif axis == 4:
        # This is an extra one for the shaker table
        volt = 0.01
    elif axis == 5:
        # This is the extra accel 832m1
        volt = 0.05166
    else:
        volt = 0.1

    new_samples = np.divide(collected_samples, volt)
    plt.plot(new_samples)
    plt.show()
    print("RMS:", np.sqrt(np.mean(np.square(new_samples))))

    # Calculate spectrum
    f, yf = welch(
        new_samples,
        sampling_rate,
        nperseg=num_samples,
        noverlap=0,
        window='flattop',
        scaling='spectrum'
    )
    yf = np.sqrt(2 * yf) * len(yf)
    yf = 2.0 / num_samples * np.abs(yf)
    # Determine the maximum at each frequency in frequency array
    reference_values = [0.0 for i in range(len(freqarr))]
    # reference_values = dict()
    bin_size = sampling_rate / num_samples


    for i in range(len(freqarr)):
        start = int((freqarr[i] - 30) / bin_size)
        stop = int((freqarr[i] + 30) / bin_size)
        reference_values[i] = max(yf[start:stop])

    print(reference_values)
    plt.plot(f, yf)
    plt.show()
    return reference_values

def set_shaker(frequency):
    nSamples = 40000
    sampling_rate = c_double(20000)

    shiftarr1500 = [2.8300, 3.0000, 0.6700, -0.0410, 2.9730, 4.1420, -0.0480, -0.2870, 2.9900, 0.1500,
                    2.7410, 1.8300, 1.3550, 0.9900, 1.4100]
    shiftarr3000 = [3.0600, 3.5100, 1.0250, -0.1510, 2.6330, 4.0420, 0.0820, -0.2070, 2.9800, 0.2200,
                    2.7100, 2.1300, 1.6100, 1.7300, 1.6600]
    shiftarr4000 = [2.7500, 2.1000, 1.0800, 1.0900, 1.7600, 3.6200, -1.7500, 0.6400, 4.0300, 0.9200]
    shiftarr5000 = [3.5900, 1.5600, 1.2000, 1.8000, 1.4600, 3.3300, -1.2000, 1.3900, 3.9500, 0.2100]
    shiftarr6000 = [3.5500, 3.3600, 1.6200, -1.1100, 1.3700, 0.7800, 1.4700, 3.5700, 0.9100, 1.1500]
    if frequency <= 1500:
        shiftarr = shiftarr1500; amp = 0.2; freqstring = "100-1500Hz"
        freqarr = [100 * (i + 1) + 0 for i in range(len(shiftarr1500))]
    elif 1500 < frequency <= 3000:
        shiftarr = shiftarr3000; amp = 0.2; freqstring = "1600-3000Hz"
        freqarr = [100 * (i + 1) + 1500 for i in range(len(shiftarr3000))]
    elif 3000 < frequency <= 4000:
        shiftarr = shiftarr4000; amp = 0.25; freqstring = "3100-4000Hz"
        freqarr = [100 * (i + 1) + 3000 for i in range(len(shiftarr4000))]
    elif 4000 < frequency <= 5000:
        shiftarr = shiftarr5000; amp = 0.3; freqstring = "4100-5000Hz"
        freqarr = [100 * (i + 1) + 4000 for i in range(len(shiftarr5000))]
    elif 5000 < frequency <= 6000:
        shiftarr = shiftarr6000; amp = 0.25; freqstring = "5100-6000Hz"
        freqarr = [100 * (i + 1) + 5000 for i in range(len(shiftarr6000))]
    else:
        resp = {"message": "Frequency entered is not available"}
        return dumps(resp)
    # BEGIN SIGNAL GEN -----------------------------------------------
    print("Generating signal...")
    rgdSamples = custom_waveform(freqarr, shiftarr, amplitude=amp, simulated_sampling_rate=100000, time_length=0.01)
    generate_samples(dev0, c_int(0), rgdSamples, time_length=0.01)
    # BEGIN ACQUISITION ----------------------------------------------
    print("Acquiring data...")
    time.sleep(0.2)  # Wait for signal to settle...
    dwf.FDwfAnalogInConfigure(dev0, c_bool(True), c_bool(True))  # Configures devices to be on
    # Acquire samples, Device 0 Channel 0
    dev0chan0_values = acquire_samples(dev0, c_int(0), sampling_rate, nSamples)
    dev0chan1_values = acquire_samples(dev0, c_int(1), sampling_rate, nSamples)     # Only enable if doing 2 channels

    dev0chan0_values = dev0chan0_values[len(dev0chan0_values)-1639:]

    # GET REFERENCE VAL ----------------------------------------------
    print("Getting reference values...")
    reference_values1 = get_reference_values(dev0chan0_values, freqarr, sampling_rate=sampling_rate.value,
                                             num_samples=len(dev0chan0_values), axis=3)
    # reference_values2 = get_reference_values(dev0chan1_values, freqarr, sampling_rate=sampling_rate.value,
    #                                          num_samples=nSamples, axis=3)          # Only enable if doing 2 channels

    return reference_values1


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
# RUN COLLECTION SCRIPT ================================================

reference_values = set_shaker(4000)