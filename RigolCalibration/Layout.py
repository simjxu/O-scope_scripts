import matplotlib.pyplot as plt
import numpy as np
from math import*
from scipy.signal import welch

# Create a dataset with 16384 points
timepts = [i*1.0/20000.0 for i in range(16384)]
freqarr = [100*i for i in range(1,15)]
sinwave = 0
rgdSamples = [0 for i in range(len(timepts))]
print(freqarr)

for t in range(len(timepts)):
    sumfreq = 0
    for j in range(len(freqarr)):
        sumfreq += sin(2 * pi * freqarr[j] * t/20000 + freqarr[j])
    rgdSamples[t] = sumfreq

plt.plot(timepts, rgdSamples)
plt.show()

collected_samples = rgdSamples
num_samples = len(timepts)
sampling_rate = 20000
xf = np.linspace(0.0, sampling_rate/2, num_samples // 2)
# xf = np.linspace(0.0, sampling_rate, num_samples)
_, yf = welch(
    collected_samples,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='flattop',
    scaling='spectrum',
    return_onesided=False
)
yf = np.sqrt(2 * yf) * len(yf)
print("length yf", len(yf))
yf = yf[:len(xf)]
print("length yf 2", len(yf))
yf = 2.0 / num_samples * np.abs(yf)

plt.plot(xf, yf)
plt.show()

# Take first 1639 points instead

collected_samples = rgdSamples[0:1639]
num_samples = len(collected_samples)
sampling_rate = 20000
xf = np.linspace(0.0, sampling_rate/2, num_samples // 2)
# xf = np.linspace(0.0, sampling_rate, num_samples)
_, yf = welch(
    collected_samples,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='flattop',
    scaling='spectrum',
    return_onesided=False
)
yf = np.sqrt(2 * yf) * len(yf)
print("length yf", len(yf))
yf = yf[:len(xf)]
print("length yf 2", len(yf))
yf = 2.0 / num_samples * np.abs(yf)

plt.plot(xf, yf)
plt.show()