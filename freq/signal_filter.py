import numpy as np
from scipy.signal import butter, filtfilt
import pdb

def butter_bandpass(lowcut, highcut, fs,  order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
   

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
 
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def butter_lowpass(lowcut, fs,  order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    b, a = butter(order, low, btype='low')
    return b, a
   

def butter_lowpass_filter(data, lowcut, fs, order=5):
 
    b, a = butter_lowpass(lowcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def butter_highpass(lowcut, fs,  order=5):
    nyq = 0.5 * fs
    high = lowcut / nyq
    b, a = butter(order, high, btype='high')
    return b, a
   

def butter_highpass_filter(data, highcut, fs, order=5):
 
    b, a = butter_lowpass(highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def butter_bandstop(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='stop')
    return b, a
   

def butter_bandstop_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandstop(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y
