
import time
import usbtmc
from decimal import *
import socket


try:
    scope = usbtmc.Instrument(0x1ab1, 0x04ce)

except socket.timeout:
    import sys

    sys.exit("Not able to connect to the scope. Please investigate...")
scope.timeout=60
print("Setting the Default Settings")

# print("Connected to: ", scope.idn)      #Shows the Status of the Connection of the scope
# print("Currently displayed channels: ", str(scope.displayed_channels))

# Set Language
scope.write("SYSTEM:LANGUAGE ENGLISH")

# Set scope variable
scope.open()                        #Initialize the Oscilloscope to operation
scope.write("*RST")
time.sleep(0.25)

scope.write("SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE 0.1")
scope.write("SOURCE1:FREQUENCY:FIXED 100")

ampl = scope.ask("SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE?")
ampl =Decimal(ampl)
print("Check if its 100 mv, amplitude :", ampl)

scope.write("SOURCE1:OUTPUT1:STATE ON")


if ampl >= 0.3:
    scope.write(":STOP")
    print("Amplitude exceed the limit Stop the scope as ampl is",ampl)
    exit()

# Setting the AC Coupling
scope.write("CHANnel1:COUPling AC")

# Setting The BandWidth limit
scope.write(":CHANnel1:BWLimit 20M ")

# Setting Channel Probe
print("Setting the Channel Probe")
scope.write("CHAN1:PROBe 1")
print("Channel Probe set to 1")

scope.write(":TRIGger:EDGe:LEVel 0")

scope.write(":RUN")
scope.write("SOURCE1:OUTPUT1:STATE OFF")

print("Oscilloscope set to Default Settings!! Now you can connect the Source to the Shaker Table to EXTERNAL SOURCE IN")
scope.close()