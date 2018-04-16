import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch
import json



arr = []

# # For JSON file
# jfile = open('C:\\Users\Simon\Downloads\calibration_data_30000c2a691055a8-2.json','r')
# json_dict = json.loads(jfile.read())
# arr = json_dict['data_832m1']['1000']['data_z']

# Grab waveform from csv file
file = csv.reader(open('C:\Petasense\\100Hz.csv', 'r'))
for row in file:
    arr.append(float(row[0]))

# arr = arr[:9000]
print("RMS before compensation:", np.sqrt(np.mean(np.square(arr))))

freqarr = [i for i in range(0,6100,100)]
cal_val_1017 = [1.027, 1.02	,0.99,	1,	1.03	,1.04	,1.08	,1.04	,1.01	,1.03	,1.04	,1.04	,1.05	,1.02	\
    ,1.11	,0.96	,0.96	,0.91	,1.21	,1.14	,1.16	,1.25	,1.22	,1.2	,1.2	,1.2	,1.19	,1.21	\
    ,1.27	,1.26	,1.27	,1.17	,1.16	,1.16	,1.2	,1.25	,1.23	,1.28	,1.31	,1.26	,1.13	,0.96	\
    ,0.88	,0.89	,0.93	,0.97	,1.01	,1.04	,1.06	,1.09	,1.09	,1.09	,1.12	,1.09	,1.11	,1.09	\
    ,1.08	,1.12	,1.14	,1.17	,1.16]


# # Forr real 1017
# cal_val_1017 = [0.8833,0.94	,0.91	,0.87	,0.87	,0.87	,0.84	,0.83	,0.78	,0.71	,0.67	,0.64	,0.66	,0.62	\
#     ,0.67	,0.57	,0.57	,0.48	,0.71	,0.64	,0.67	,0.65	,0.64	,0.61	,0.6	,0.58	,0.56	\
#     ,0.54	,0.57	,0.6	,0.71	,0.73	,0.72	,0.71	,0.72	,0.74	,0.72	,0.71	,0.74	,0.66	\
#     ,0.51	,0.49	,0.51	,0.53	,0.55	,0.57	,0.58	,0.59	,0.59	,0.59	,0.58	,0.59	,0.58	\
#     ,0.6	,0.61	,0.62	,0.63	,0.63	,0.64	,0.63	,0.61]


sampling_rate = 20000
num_samples = len(arr)
print(num_samples)
bin_size = sampling_rate/num_samples

# Calculate spectrum
f, yf = welch(
    arr,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='flattop',
    scaling='spectrum'
)
yf = np.sqrt(yf*2)          # power spect needs to be multiplied by 2 because it's single sided
plt.plot(f, yf)             # This is an amplitude spectrum before compensation
plt.show()

# Calculate interpolated gain values and compensate amplitudes on amplitude spectrum
gain_values = np.interp(f, freqarr, cal_val_1017)
amps_compensated = [0 for i in range(len(yf))]
for i in range(len(yf)):
    amps_compensated[i] = yf[i]/gain_values[i]

plt.plot(f, amps_compensated)             # This is an amplitude spectrum after compensation
plt.show()

# Convert this to a PSD so you can calculate RMS
newyf = np.array(amps_compensated)
newyf = newyf**2/2
newyf = newyf/(bin_size*1.5)   # 1.5 is npbw of Hann window

corrected_RMS_PSD = np.sqrt(sum(np.multiply(bin_size, newyf)))
print("RMS PSD corrected:", corrected_RMS_PSD)


#
# f, yf = welch(
#     arr,
#     sampling_rate,
#     nperseg=num_samples,
#     noverlap=0,
#     window='hanning',
#     scaling='spectrum',
#     return_onesided=True
# )
#
# yf = np.sqrt(yf*2)
#
# freqarr = [i for i in range(0,6100,100)]
# freqarr.append(10000)
#
#
#
# gain_values = np.interp(f, freqarr, cal_val_1017)
#
# amps_compensated = [0 for i in range(len(yf))]
# for i in range(len(yf)):
#     amps_compensated[i] = yf[i]/gain_values[i]
#
#
# # newyf = np.divide(amps_compensated,2)
# newyf = np.array(amps_compensated)
# newyf = newyf**2/2
# newyf = newyf/(bin_size*1.5)   # 3.77 is npbw of flat top
#
# corrected_RMS_PSD = np.sqrt(sum(np.multiply(bin_size, newyf)))
# print("RMS PSD corrected:", corrected_RMS_PSD)
#
#
