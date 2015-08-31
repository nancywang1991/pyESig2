import numpy as np
import edflib._edflib as edflib
import pdb
import datetime
from pyESig.vid.vid_time import get_disconnected_times
from pyESig.analysis.mu_drop_funcs import *
from datetime import time, datetime, timedelta
from scipy.signal import hilbert
import cPickle as pickle
import matplotlib.pyplot as plt


sbj_id = "a86a4375"
day = 2
neural_file_loc = "D:\\NancyStudyData\\ecog\\edf\\" + sbj_id + "\\"
output_file_loc = "D:\\face_ecog\\" + sbj_id + "_" + str(day) + "\\"
time_file = "C:\\Users\\wangnxr\\Documents\\rao_lab\\" + \
                    "video_analysis\\vid_real_time\\" + sbj_id + \
                    "_" + str(day) + ".p"
disconnect_file = "C:\\Users\\wangnxr\\Documents" + \
                    "\\rao_lab\\video_analysis\\disconnect_times\\" \
                    + sbj_id + "_" + str(day) + ".txt"
annotation_loc = "C:\\Users\\wangnxr\\Documents\\rao_lab" + \
                     "\\video_analysis\\manual_annotations\\sleep.csv"

start_time, end_time, start, end = get_disconnected_times(disconnect_file)

cur_time = start_time

# Average Signal amplitude
neural_sig = edflib.Edfreader(neural_file_loc  + sbj_id + "_"
                              + str(day) + ".edf")
buffer_size = 1000
samp_rate = 1000
f_lo = 5
f_hi = 15
total_secs = (end_time-start_time).seconds
##final_sig_cutoff = np.zeros(total_secs/10-9)
##for chunk in xrange(100, total_secs-1000, 10):
##    chan_sig = np.zeros(buffer_size*10)
##    neural_sig.readsignal(3, chunk*buffer_size, buffer_size*10, chan_sig)
##    clean_sig = butter_bandpass_filter(chan_sig, f_lo, f_hi, samp_rate)
##    final_sig_cutoff[(chunk-100)/10] = np.mean(np.abs(hilbert(clean_sig)**2))        
##    print str(chunk) + " of " + str(total_secs)
##pdb.set_trace()
signal_cutoff = 3100

# Signal Extraction

f_lo = 1
f_hi = 50

time_conversion = pickle.load(open(time_file, "rb"))
annotation = np.genfromtxt(annotation_loc, delimiter=',', dtype='string')

#pdb.set_trace()

def extract_label(annotation, sbj_id, day, vid_num):
    same= np.where(annotation[:,2] == str(vid_num))[0]
    if len(same) > 1:
        same = np.where(annotation[same,0] == sbj_id)[0]
    if len(same) > 1:
        same = np.where(annotation[same,1] == str(day))[0]
    if len(same) > 1:
        print "duplicate"
    if len(same) == 0:
        return 2
    return int(annotation[same[0],-1])

cur_time += timedelta(seconds=6010)
for chunk in range(6011,(end_time-start_time).seconds):
    final_sig = np.zeros(shape=(64, f_hi-f_lo))
    print "chunk: " + str(chunk) + " of " + \
        str((end_time-start_time).seconds)
    # Calculate amplitude
    chan_sig = np.zeros(buffer_size*10)
    neural_sig.readsignal(3, chunk*buffer_size, buffer_size*10, chan_sig)
    clean_sig = butter_bandpass_filter(chan_sig, 5, 15, samp_rate)
    final_amplitude = np.mean(np.abs(hilbert(clean_sig)**2))
    label = 2
    for i, video in enumerate(time_conversion):
        if cur_time < video[1] and cur_time>time_conversion[i-1][1]:
            video_num = i
            label = extract_label(annotation, sbj_id, day, video_num-1)
            break
    
    if label == 1 or (label==0 and final_amplitude > signal_cutoff):        
        for c in range(0,64):        
            chan_sig = np.zeros(buffer_size)
            neural_sig.readsignal(c, chunk*buffer_size, buffer_size, chan_sig)
            clean_sig = butter_bandpass_filter(chan_sig, f_lo, f_hi, samp_rate)
            final_sig[c,:] = np.abs(np.fft.fft(clean_sig)**2)[f_lo:f_hi]
            pickle.dump(final_sig, open(output_file_loc + str(time_conversion[video_num-1][0]) + "_"
                            + str((cur_time-time_conversion[video_num-1][1]).seconds) + ".p", "wb"))
                
    cur_time += timedelta(seconds=1)
    
    

