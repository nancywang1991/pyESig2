from pyESig.unsupervised.feature_extract_funcs import *
from pyESig.analysis.mu_drop_funcs import *
import numpy as np
import edflib._edflib as edflib
import cPickle as pickle

sbj_id = "e1556efa"
day = 2
neural_file_loc = "D:\\NancyStudyData\\eeg\\edf\\" + sbj_id + "\\"
neural_sig = edflib.Edfreader(neural_file_loc  + sbj_id + "_"
                              + str(day) + ".edf")
out_file_loc = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\features\\"

samp_rate = neural_sig.samplefrequency(0)
buffer_size = int(samp_rate*3)
delta_lo = 1
delta_hi = 4
gamma_lo = 30
gamma_hi = 55
total_secs = neural_sig.datarecords_in_file
win_size = 3

delta_power = np.zeros(shape=(total_secs/3, 20))
gamma_ratio = np.zeros(shape=(total_secs/3, 20))
stdev = np.zeros(shape=(total_secs/3, 20))
for chunk in range(0,total_secs-3, win_size):
    print str(chunk) + " of " + str(total_secs)
    for c in range(1,21):
        chan_sig = np.zeros(buffer_size)
        neural_sig.readsignal(c, chunk*samp_rate, buffer_size, chan_sig)      
        signal = butter_bandpass_filter(chan_sig, 0.01, 100, samp_rate)
        delta_power[chunk/3, c-1] = extract_power(signal, delta_lo, delta_hi, samp_rate)
        gamma_ratio[chunk/3, c-1] = extract_power(signal, gamma_lo, gamma_hi, samp_rate)/delta_power[chunk/3,c-1]
        stdev[chunk/3, c-1] = np.std(signal)

delta_power = delta_power-np.mean(delta_power, axis=0)
gamma_ratio = gamma_ratio-np.mean(gamma_ratio, axis=0)
delta_gradient = np.gradient(delta_power)[0]
gamma_ratio_gradient = np.gradient(gamma_ratio)[0]

final_features = np.hstack((delta_power, gamma_ratio, delta_gradient, gamma_ratio_gradient, stdev))
pickle.dump(final_features, open(out_file_loc + sbj_id + "_" + str(day) + ".p", "wb"))
