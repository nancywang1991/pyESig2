import numpy as np
import pdb
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, hilbert, savgol_filter
from datetime import timedelta, datetime, date
import csv
from numpy import int32

#-------------------------------------Helper-----------------------------------

def my_hilb_transform(signal, f_lo, f_hi, win_size, samp_rate):
        hilb_signals = np.zeros(shape = (signal.shape[0], f_hi-f_lo))
        for f, cnt in enumerate(range(f_lo,f_hi)):
            transform = np.abs(hilbert(bandpass(signal, f, f+1, samp_rate))**2
            hilb_signals[:,cnt] = savgol_filter(transform), win_size, 2)            
        return hilb_signals


#---------------------------------------Main-----------------------------------

def hilb_filter(signal, level, criteria, samp_rate, t_start, signal_min):
    filt_signal = []
    vid_samp_rate = 30
    for t in range(0,signal.shape[0]-samp_rate,samp_rate/vid_samp_rate):
        if (np.where(signal[t:t+samp_rate]<=signal_min)[0].shape[0] == 0)
            and (level[int((t+t_start)/float(samp_rate)*vid_samp_rate)]
                    == criteria):                    
                filt_signal.append(np.sum(signal[t:t+samp_rate,:], axis=0))
                
    return np.array(filt_signal)


def fft_filter(signal, level, criteria, f_lo, f_hi, samp_rate,
               t_start, signal_min):

    filt_signal = []
                
    for t in range(0,signal.shape[0]-samp_rate,samp_rate/vid_samp_rate):
        if (np.where(signal[t:t+samp_rate]<=signal_min)[0].shape[0] == 0)
            and (level[int((t+t_start)/float(samp_rate)*vid_samp_rate)]
                    == criteria):
                    fft_transform =
                            (np.abs(np.fft.fft(signal[t:t+samp_rate]))**2)
                    filt_signal.append(fft_transform[f_lo:f_hi])
                    
    return np.array(filt_signal)
  
