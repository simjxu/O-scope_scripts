import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import welch

jfile = open("C:\Petasense\Data\DataIntegrityCheck\Calibration\p8_calibration_data_832m1.json", "r")
json_dict = json.loads(jfile.read())

collected_samples = json_dict['VM2-01040']['data']['100']['data_z']
plt.plot(json_dict['VM2-01040']['data']['1700']['data_z'], 'b')
plt.show()
# plt.plot(json_dict['VM2-01040']['data']['2300']['data_z'], 'b')
# plt.show()

# print("reference values")
# for i in range(100,1500,100):
#     print(json_dict['VM2-01030']['data'][str(i)]['rms_z'])

freqarr = [100 * (i + 1) + 0 for i in range(15)]
sampling_rate = 20000
num_samples = len(collected_samples)
# print("num samples:", num_samples)


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




# Determine the maximum at each frequency in frequency array
reference_values = [0.0 for i in range(len(freqarr))]
# reference_values = dict()
bin_size = sampling_rate / num_samples
print("bin size:", bin_size)

for i in range(len(freqarr)):
    start = int((freqarr[i] - 30) / bin_size)
    stop = int((freqarr[i] + 30) / bin_size)
    print(i)
    print(start, "-", stop)
    reference_values[i] = max(yf[start:stop])

print(reference_values)
plt.plot(xf, yf)
plt.show()
