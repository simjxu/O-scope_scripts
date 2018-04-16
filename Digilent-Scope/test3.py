import math
import numpy as np
from scipy.signal import welch
import matplotlib.pyplot as plt
import random

# Create a set of time points for 832m1, using 1639 points like in calibration
t = np.multiply([i for i in range(1639)],1.0/20000.0)
sampling_rate = 20000
num_samples = len(t)

random_phase_arr = [random.randint(0,1)*math.pi for i in range(5)]

# Simulated Collected samples are samples collected from Mote, or device under test
# Here I used
collected_samples = 1 * np.sin(np.add(np.multiply(2*math.pi*100,t),random_phase_arr[0])) \
                    + 0.9 * np.sin(np.add(np.multiply(2*math.pi*200,t),random_phase_arr[1])) \
                    + 0.85 * np.sin(np.add(np.multiply(2*math.pi*300,t),random_phase_arr[2])) \
                    + 0.7* np.sin(np.add(np.multiply(2 * math.pi * 400, t), random_phase_arr[3])) \
                    + 0.65 * np.sin(np.add(np.multiply(2 * math.pi * 500, t), random_phase_arr[4]))

# Let's say that "correct_samples" are the samples collected from reference accelerometer
correct_samples = 1 * np.sin(np.add(np.multiply(2 * math.pi * 100, t), random_phase_arr[0])) \
                    + 1 * np.sin(np.add(np.multiply(2 * math.pi * 200, t), random_phase_arr[1])) \
                    + 1 * np.sin(np.add(np.multiply(2 * math.pi * 300, t), random_phase_arr[2])) \
                    + 1 * np.sin(np.add(np.multiply(2 * math.pi * 400, t), random_phase_arr[3])) \
                    + 1 * np.sin(np.add(np.multiply(2 * math.pi * 500, t), random_phase_arr[4]))

RMS = np.sqrt(np.mean(np.square(collected_samples)))
print("RMS of Mote samples:", RMS)
correct_RMS = np.sqrt(np.mean(np.square(correct_samples)))
print("Correct RMS from reference accel:", correct_RMS)

bin_size = sampling_rate/num_samples

# Calculate calibration values ----------------------------------
# Calculate spectrum for collected samples
xf = np.linspace(0.0, sampling_rate / 2, num_samples // 2)
_, yf = welch(
    collected_samples,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='flattop',
    scaling='spectrum'
)
yf = np.sqrt(yf*2)
freqarr = [100, 200, 300, 400, 500]
reference_values = []
for i in range(len(freqarr)):
    start = int((freqarr[i] - 30) / bin_size)
    stop = int((freqarr[i] + 30) / bin_size)
    reference_values.append(max(yf[start:stop]))

# Calculate spectrum for correct samples
xf = np.linspace(0.0, sampling_rate / 2, num_samples // 2)
_, yf = welch(
    correct_samples,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='flattop',
    scaling='spectrum'
)
yf = np.sqrt(yf*2)
calibration_values = []
for i in range(len(freqarr)):
    start = int((freqarr[i] - 30) / bin_size)
    stop = int((freqarr[i] + 30) / bin_size)
    calibration_values.append(reference_values[i]/max(yf[start:stop]))
calibration_values = [calibration_values[0]] + calibration_values
calibration_values.append(calibration_values[-1])

# print("Calibration values:", calibration_values)

# Calculate the power spectrum, because compensation will be done on the amplitude spectrum
f, yf = welch(
    collected_samples,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='hanning',
    scaling='spectrum'
)

# Convert the power spectrum to amplitude spectrum
yf = np.sqrt(yf*2)          # power spect needs to be multiplied by 2 because it's single sided
plt.plot(f, yf)             # This is an amplitude spectrum
plt.show()

# Let's say these are the calibration values achieved at each frequency.
frequencies = [0, 100, 200, 300, 400, 500, 20000]

# Calculate interpolated gain values and compensate amplitudes on amplitude specrum
gain_values = np.interp(f, frequencies, calibration_values)
amps_compensated = [0 for i in range(len(yf))]
for i in range(len(yf)):
    amps_compensated[i] = yf[i]/gain_values[i]

plt.plot(f,amps_compensated)        # This is the compensated amplitude spectrum
plt.show()

# Convert this to a PSD so you can calculate RMS
newyf = np.array(amps_compensated)
newyf = newyf**2/2
newyf = newyf/(bin_size*1.5)   # 1.5 is npbw of Hann window

corrected_RMS_PSD = np.sqrt(sum(np.multiply(bin_size, newyf)))
print("RMS PSD corrected:", corrected_RMS_PSD)

print("Percent difference from reference RMS:", abs(corrected_RMS_PSD-correct_RMS)/correct_RMS*100)


print("----- See what happens if we compensate on PSD directly -----")
# Calculate the PSD, because compensation will be done on the PSD
f, yf = welch(
    collected_samples,
    sampling_rate,
    nperseg=num_samples,
    noverlap=0,
    window='hanning',
    scaling='density'
)

# Keep it as PSD
plt.plot(f, yf)             # This is an PSD spectrum
plt.show()

# Let's say these are the calibration values achieved at each frequency.
frequencies = [0, 100, 200, 300, 400, 500, 20000]

# Calculate interpolated gain values and compensate amplitudes on PSD
gain_values = np.interp(f, frequencies, calibration_values)
amps_compensated = [0 for i in range(len(yf))]
for i in range(len(yf)):
    amps_compensated[i] = yf[i]/gain_values[i]

plt.plot(f,amps_compensated)        # This is the compensated power spectrum
plt.show()

corrected_RMS_PSD = np.sqrt(sum(np.multiply(bin_size, amps_compensated)))
print("RMS PSD corrected from PSD:", corrected_RMS_PSD)


# # --- For checking PSD calculation of RMS
# yf = yf/2
# yf = yf**2/2
# yf = yf/(bin_size*1.5)   # 3.77 is npbw of flat top
#
# corrected_RMS_PSD = np.sqrt(sum(np.multiply(bin_size, yf)))
# print("RMS PSD corrected:", corrected_RMS_PSD)
#
# f, yf = welch(
#     collected_samples,
#     sampling_rate,
#     nperseg=num_samples,
#     noverlap=0,
#     window='hanning',
#     scaling='spectrum'
# )
#
# yf = np.sqrt(yf*2)
# yf = yf/3
# yf = yf**2/2
# yf = yf/(bin_size*1.5)   # 1.5 is npbw of Hann
# corrected_RMS_PSD = np.sqrt(sum(np.multiply(bin_size, yf)))
# print("RMS PSD corrected:", corrected_RMS_PSD)
