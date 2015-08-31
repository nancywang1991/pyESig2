import numpy as np
import pdb
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, hilbert, savgol_filter
from datetime import timedelta, datetime, date
import csv
from numpy import int32

#----------------------------------Helper---------------------------------------

def assign_level(cur_level, signal, thresh, direction):
    '''Determines what level the snippet of movement magnitudes is based on the
cur_level and direction'''
    num_signal = np.where(signal>thresh)[0].shape[0]
    if direction == 1:
        if num_signal > 15:
            return cur_level + 1
        elif num_signal < 5:
            return 0
        else:
            return None                    
    if direction == -1 and num_signal < 5:
        return cur_level - 1
    else:
        return None

#-----------------------------------Main----------------------------------------

def signal_thresh(signal, thresh, frame_rate=30):
    '''signal is an array of signal magnitudes for each frame, levels indicates
       what frame it is before or after a threshold is acheived in the result
       (neg levels indicating before, zero as other, positive as
       after). Positive overwrites negative'''

    signal_level = np.zeros(signal.shape[0], dtype=int)
    cur_signal_level = 0
    for m in range(signal.shape[0]):
        level = assign_level(cur_signal_level, signal[m:m+frame_rate], thresh, 1)
        if level is not None:
            signal_level[m] = level
            cur_signal_level = level
    for n in range(signal.shape[0]-1):
        if signal_level[n+1]==1:            
            while signal_level[n] == 0 and n >= 0:
                level = assign_level(signal_level[n+1], signal[n-frame_rate:n], thresh, -1)
                if level is not None:
                    signal_level[n] = level
                else:
                    break    
    return signal_level




def signal_filter(signal_raw, signal_level, criteria, f_lo, f_hi, samp_rate, filt, t_start, signal_min, filt_type='fft', hilb_sig=None):

    #signal = signal-np.mean(signal)
    filt_signal = []
    if filt_type == 'fft':
        
        if filt == True:
            signal = bandpass(signal_raw, 0.05, 100, samp_rate)
        else: signal = signal_raw
        
        for t in range(0,signal.shape[0]-samp_rate,samp_rate/30):
            if not(np.where(signal[t:t+samp_rate]<=signal_min)[0].shape[0] > 0):
                if signal_level[ int((t + t_start)/float(samp_rate)*30)] == criteria:
                    
    ##                plt.plot(signal[t:t+512])
    ##                plt.show()
    ##                plt.plot((np.abs(np.fft.fft(signal[t:t+512]))**2)[f_lo:f_hi])
    ##                plt.show()
    ##                pdb.set_trace()
                    
                    filt_signal.append((np.abs(np.fft.fft(signal[t:t+samp_rate]))**2)[f_lo:f_hi])
                    #pdb.set_trace()
    elif filt_type == 'hilbert':
        
        for t in range(0,hilb_sig.shape[0]-samp_rate,samp_rate/30):
            if not(np.where(signal_raw[t:t+samp_rate]<=signal_min)[0].shape[0] > 0):
                if signal_level[ int((t + t_start)/float(samp_rate)*30)] == criteria:
                    
                    filt_signal.append(np.sum(hilb_sig[t:t+samp_rate,:],axis=0))
                    
    return filt_signal

  
def weighted_signal_average(signal_chunks):
    average = 0
    cnt = 0
    for chunk in signal_chunks:
        average += chunk[0]*chunk[1]
        cnt += chunk[1]

    return average/cnt

def check_signal_level(signal_level, delay, start_time, file_name):
    starts = np.unique(np.where(signal_level==3)[0]/30)
    ends = np.unique(np.where(signal_level==-10)[0]/30)

    with open(file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['hours', 'minutes', 'seconds',  'type'])
        for i in xrange(ends.shape[0]):
            t=(datetime.combine(date(1,1,1),start_time) + \
               timedelta(seconds=int(delay/30 + starts[i]))).time()
            
            writer.writerow([t.hour, t.minute,  t.second, 'start'])
            t=(datetime.combine(date(1,1,1),start_time) + \
               timedelta(seconds=int(delay/30 + ends[i]))).time()
            writer.writerow([t.hour, t.minute,t.second,'end'])


        
        
        
