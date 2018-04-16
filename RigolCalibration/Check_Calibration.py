import numpy as np
import json
import matplotlib.pyplot as plt


jfile = open("C:\Petasense\Data\DataIntegrityCheck\Calibration\p8_calibration_data_832m1.json", "r")
json_dict = json.loads(jfile.read())

# json_dict['measurements'][i]['data']['z']['time_domain_features']['rms']
print(len(json_dict))



max_x = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
max_y = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
max_z = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
min_x = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
min_y = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
min_z = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
med_x = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
med_y = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
med_z = [0.0 for i in range(len(json_dict['VM2-01137']['data']))]
argmax_x = ['a' for i in range(len(json_dict['VM2-01137']['data']))]
argmax_y = ['a' for i in range(len(json_dict['VM2-01137']['data']))]
argmax_z = ['a' for i in range(len(json_dict['VM2-01137']['data']))]
argmin_x = ['a' for i in range(len(json_dict['VM2-01137']['data']))]
argmin_y = ['a' for i in range(len(json_dict['VM2-01137']['data']))]
argmin_z = ['a' for i in range(len(json_dict['VM2-01137']['data']))]

freq_range = [str(100*i) for i in range(1, 61)]
freq_range_num = [100*i for i in range(1, 61)]

a = 8
value_matrix_x = np.matrix([[0.0 for col in range(60)] for row in range(144-a)])
value_matrix_y = np.matrix([[0.0 for col in range(60)] for row in range(144-a)])
value_matrix_z = np.matrix([[0.0 for col in range(60)] for row in range(144-a)])

SN_array = ['a' for i in range(143)]

rowcount = 0
for SN in json_dict:
    colcount = 0
    SN_array[rowcount] = SN
    if SN == 'VM2-01100' or SN == 'VM2-01058' or SN == 'VM2-01094' or SN == 'VM2-01061' \
            or SN == 'VM2-01067' or SN == 'VM2-01093' or SN == 'VM2-01064' or SN == 'VM2-01037':
        continue
    else:
        for freq in freq_range:
            value_matrix_x[rowcount, colcount] = json_dict[SN]['data'][freq]['rms_x']
            value_matrix_y[rowcount, colcount] = json_dict[SN]['data'][freq]['rms_y']
            value_matrix_z[rowcount, colcount] = json_dict[SN]['data'][freq]['rms_z']
            colcount += 1
    rowcount += 1

for i in range(60):
    min_x[i] = np.min(value_matrix_x[:, i])
    min_y[i] = np.min(value_matrix_y[:, i])
    min_z[i] = np.min(value_matrix_z[:, i])
    max_x[i] = np.max(value_matrix_x[:, i])
    max_y[i] = np.max(value_matrix_y[:, i])
    max_z[i] = np.max(value_matrix_z[:, i])
    med_x[i] = np.mean(value_matrix_x[:, i])
    med_y[i] = np.mean(value_matrix_y[:, i])
    med_z[i] = np.mean(value_matrix_z[:, i])
    argmin_x[i] = SN_array[np.argmin(value_matrix_x[:, i])]
    argmin_y[i] = SN_array[np.argmin(value_matrix_y[:, i])]
    argmin_z[i] = SN_array[np.argmin(value_matrix_z[:, i])]
    argmax_x[i] = SN_array[np.argmax(value_matrix_x[:, i])]
    argmax_y[i] = SN_array[np.argmax(value_matrix_y[:, i])]
    argmax_z[i] = SN_array[np.argmax(value_matrix_z[:, i])]



print("argminx")
print(argmin_x)
print("argminy")
print(argmin_y)
print("argminz")
print(argmin_z)
print("argmaxx")
print(argmax_x)
print("argmaxy")
print(argmax_y)
print("argmaxz")
print(argmax_z)


plt.plot(freq_range_num, min_x, 'r')
plt.plot(freq_range_num, max_x, 'b')
plt.plot(freq_range_num, med_x, 'g')
plt.show()

plt.plot(freq_range_num, min_y, 'r')
plt.plot(freq_range_num, max_y, 'b')
plt.plot(freq_range_num, med_y, 'g')
plt.show()

plt.plot(freq_range_num, min_z, 'r')
plt.plot(freq_range_num, max_z, 'b')
plt.plot(freq_range_num, med_z, 'g')
plt.show()

# for SN in json_dict:
#     for freq in json_dict[SN]['data']:
#         rms_x = json_dict[SN]['data'][freq]['rms_x']
#         rms_y = json_dict[SN]['data'][freq]['rms_y']
#         rms_z = json_dict[SN]['data'][freq]['rms_z']
#         if rms_x < 0.3 or rms_y < 0.3 or rms_z < 0.3:
#             print("Found something!")
#             print("    ", SN, "at", freq)
#             print("    ", rms_x, rms_y, rms_z)