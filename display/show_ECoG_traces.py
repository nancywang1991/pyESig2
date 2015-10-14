import numpy as np
import edflib._edflib as edflib
import pdb
from pyESig2.analysis.mu_drop_funcs import butter_bandpass_filter
import matplotlib.pyplot as plt

#-------------------------------Main Function--------------------------------
def display_signals(f, file, start_min, stop_min, channels):
    neural_sig = edflib.Edfreader(file)
    samp_rate = int(neural_sig.samplefrequency(0))
    buffer_size = (stop_min-start_min)*samp_rate*60

    start = start_min*samp_rate*60
    print ("Processing starting at " + str(start_min) + " in file " + str(f) + "\n")
    chan_sig = np.zeros(shape=(len(channels), buffer_size))
    for c, channel in enumerate(channels):
        print "Processing channel: " + str(channel)
        sig = np.zeros(buffer_size*4)
        neural_sig.readsignal(channel, start-buffer_size,
                                          buffer_size*3, sig)
        clean_sig = butter_bandpass_filter(sig, 0.1, 160, samp_rate, order=2)+ 300*c
        chan_sig[c,:] = clean_sig[buffer_size:buffer_size*2]

    plt.plot(chan_sig[:,::1000].T, color='black')
    plt.xticks([])
    plt.yticks([])
    plt.show()



#---------------------------------Subject Params-------------------------------

#sbj_id = "fcb01f7a"
#n_channels = 84
sbj_id = "e70923c4"
#n_channels = 86
#sbj_id = "a86a4375"
#n_channels = 104
#sbj_id = "ffb52f92"
#n_channels = 106
#sbj_id = "d6532718"
channels = np.arange(10,20)
date = '5'
eeg_file_loc = "D:\\NancyStudyData\\ecog\\edf\\"
start_min = 0
stop_min = 40


#--------------------------------Signal Extraction-----------------------------

file = eeg_file_loc + sbj_id + "\\" + sbj_id + "_" + date + ".edf"
parent, num = file.split('_')
f, ext = num.split('.')
display_signals(f, file, start_min, stop_min, channels)



