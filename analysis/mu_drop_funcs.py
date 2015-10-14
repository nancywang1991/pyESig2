import numpy as np
from obspy.signal.filter import bandpass
import pdb
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, hilbert, savgol_filter
from datetime import timedelta, datetime, date
import csv
from numpy import int32

def mvmt_thresh(mvmt):
    '''0 indicates 3 second before motion, 1 indicates 2 seconds before motion, 2 indicates 1 second before motion
        -2 indicates 1 second after motion, -3 = 2 s after motion... and so on
       -1 indicates no motion, all otherpositive numbers represent number of frames
       after motion started - 2'''

    mvmt_level = np.zeros(mvmt.shape[0], dtype=int)-1
    cur_mvmt_level = 3
    for m in range(mvmt.shape[0]):        
        num_mvmt = np.where(mvmt[m: m + 30] > 1.1)[0].shape[0]
        if (num_mvmt > 15):
            mvmt_level[m] = cur_mvmt_level
            cur_mvmt_level += 1
        elif (num_mvmt < 5):
            mvmt_level[m] = 0
            cur_mvmt_level = 3
    
    for m in range(mvmt.shape[0]):
 
        if mvmt_level[m]==0 and np.where(mvmt_level[m:m+30]==3)[0].shape[0]>0:
            mvmt_level[m] = 2
        elif mvmt_level[m]==0 and np.where(mvmt_level[m+30:m+60]==3)[0].shape[0]>0:
            mvmt_level[m] = 1
        elif mvmt_level[m]==0 and np.where(mvmt_level[m+60:m+90]==3)[0].shape[0]==0:
            if np.where(mvmt_level[m-30:m]>0)[0].shape[0]>0:
                mvmt_level[m] = -2
            elif np.where(mvmt_level[m-60:m-30]>0)[0].shape[0]>0:
                mvmt_level[m] = -3
            elif np.where(mvmt_level[m-90:m-60]>0)[0].shape[0]>0:
                mvmt_level[m] = -4
            else: mvmt_level[m] = -1
    
    return mvmt_level

def sound_thresh(sound):
    '''0 indicates 3 second before motion, 1 indicates 2 seconds before motion, 2 indicates 1 second before motion
        -2 indicates 1 second after motion, -3 = 2 s after motion... and so on
       -1 indicates no motion, all otherpositive numbers represent number of frames
       after motion started - 2'''

    sound_level = np.zeros(sound.shape[0], dtype=int)-1
    cur_sound_level = 3
    
    for m in range(sound.shape[0]):

        num_sound = np.where(sound[m: m + 30] > 1.5)[0].shape[0]
        if (num_sound > 15):
            sound_level[m] = cur_sound_level
            cur_sound_level += 1
        elif (num_sound < 5):
            sound_level[m] = 0
            if cur_sound_level>3 and np.where(sound_level[m-90:m]>0)[0].shape[0]==0:
                sound_level[m] = -10
                cur_sound_level = 3

    
    for m in range(sound.shape[0]): 
        if sound_level[m]==0 or sound_level[m]==-1:
            if np.where(sound_level[m:m+30]==3)[0].shape[0]>0:
                sound_level[m] = 2
            elif np.where(sound_level[m+30:m+60]==3)[0].shape[0]>0:
                sound_level[m] = 1
            elif np.where(sound_level[m+60:m+90]==3)[0].shape[0]>0:
                sound_level[m] = 0
            elif np.where(sound_level[m-90:m]==-10)[0].shape[0]>0:
                if np.where(sound_level[m-30:m]==-10)[0].shape[0]>0:
                    sound_level[m] = -2
                elif np.where(sound_level[m-60:m-30]==-10)[0].shape[0]>0:
                    sound_level[m] = -3
                else: 
                    sound_level[m] = -4
            elif np.where(sound_level[m-180:m+180]>0)[0].shape[0]==0:
                sound_level[m] = -20
            else: sound_level[m] = -1
    
    return sound_level


def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
   

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandstop(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='stop')
    return b, a
   

def butter_bandstop_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandstop(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass( highcut, fs, order=3):
    nyq = 0.5 * fs
    high = highcut / nyq
    b, a = butter(order, high, btype='high')
    return b, a


def butter_highpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_highpass(highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def signal_filter(signal_raw, mvmt_level, criteria, f_lo, f_hi, samp_rate, filt, t_start, signal_min, filt_type='fft', hilb_sig=None):

    #signal = signal-np.mean(signal)
    filt_signal = []
    if filt_type == 'fft':
        
        if filt == True:
            signal = bandpass(signal_raw, 0.05, 100, samp_rate)
        else: signal = signal_raw
        
        for t in range(0,signal.shape[0]-samp_rate,samp_rate/30):
            if not(np.where(signal[t:t+samp_rate]<=signal_min)[0].shape[0] > 0):
                if mvmt_level[ int((t + t_start)/float(samp_rate)*30)] == criteria:
                    
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
                if mvmt_level[ int((t + t_start)/float(samp_rate)*30)] == criteria:
                    
                    filt_signal.append(np.sum(hilb_sig[t:t+samp_rate,:],axis=0))
                    
    return filt_signal

def my_hilb_transform(signal, f_lo, f_hi, win_size, samp_rate):
        hilb_signals = np.zeros(shape = (signal.shape[0], f_hi-f_lo))
        cnt = 0
        for f in range(f_lo,f_hi):            
            hilb_signals[:,cnt] = \
                            savgol_filter(np.abs(hilbert(bandpass(signal, f, f+1, samp_rate))**2), win_size, 2)
            cnt += 1
        return hilb_signals
    
def weighted_signal_average(signal_chunks):
    average = 0
    cnt = 0
    for chunk in signal_chunks:
        average += chunk[0]*chunk[1]
        cnt += chunk[1]

    return average/cnt

def check_mvmt_level(mvmt_level, delay, start_time, file_name):
    starts = np.unique(np.where(mvmt_level==3)[0]/30)
    ends = np.unique(np.where(mvmt_level==-10)[0]/30)

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


        
        
        
