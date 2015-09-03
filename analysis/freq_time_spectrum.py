import numpy as np
#from obspy.signal.filter import bandpass
import pdb
import matplotlib.pyplot as plt
import edflib._edflib as edflib
import cPickle as pickle
from matplotlib.gridspec import GridSpec
from pyESig.analysis.mu_drop_funcs \
    import mvmt_thresh, signal_filter, butter_bandpass_filter, butter_bandstop_filter

sbj_id = "a86a4375"
day = 2
mvmt_file_loc = "C:\\Users\\wangnxr\\Documents\\rao_lab" \
                + "\\video_decode\\mvmt_result_agg\\"
neural_file_loc = "D:\\NancyStudyData\\ecog\\edf\\" + sbj_id + "\\"
output_file_loc = "C:\\Users\\wangnxr\\Documents\\rao_lab" \
                + "\\video_analysis\\figures\\" + sbj_id + "\\"
total_mvmt = pickle.load(open(mvmt_file_loc + sbj_id + \
                              "_" + str(day) + ".p","rb"))
delay = (5*60*60)*30
mvmt_level = mvmt_thresh(total_mvmt[delay:delay+200000])
neural_sig = edflib.Edfreader(neural_file_loc  + sbj_id + "_" + str(day) + ".edf")
buffer_size = 200000
samp_rate = 1000
f_lo = 1
f_hi = 160
time_lim = 34
for c in range(1,65):
    name = neural_sig.signal_label(c)
    fft_arr = np.zeros(shape = (min(time_lim,max(mvmt_level)) + 4,f_hi-f_lo))
    total_samp = np.zeros(min(time_lim,max(mvmt_level)) + 4)
    for chunk in xrange((mvmt_level.shape[0]*samp_rate/30)/buffer_size):
        print "chunk: " + str(chunk) + " of " + str((mvmt_level.shape[0]*1000/30)/buffer_size)\
              + " in channel " + str(c)
        chan_sig = np.zeros(buffer_size)
        neural_sig.readsignal(c, chunk*buffer_size+delay/30*samp_rate, buffer_size, chan_sig)
        clean_sig = butter_bandpass_filter(chan_sig, 1, 100, samp_rate)
        clean_sig = butter_bandstop_filter(clean_sig, 59, 61, samp_rate)
        clean_sig = clean_sig-np.mean(clean_sig)
##        if c == 12:
##            plt.plot(chan_sig)
##            plt.plot(clean_sig)
##            
##            plt.show()
##            pdb.set_trace()
        for level in xrange(min(time_lim,max(mvmt_level)) + 1):
            fft_sig = signal_filter(clean_sig[3000:-1000], mvmt_level,\
                                level, f_lo, f_hi, samp_rate, False, \
                                    chunk*buffer_size + 3000, neural_sig.physical_min(c))
            if len(fft_sig)>0:
                fft_arr[level,:] = (total_samp[level]/(total_samp[level] + len(fft_sig)))*fft_arr[level,:]\
                                   + (len(fft_sig)/(total_samp[level] + len(fft_sig))*(np.mean(fft_sig, axis=0)))                
                total_samp[level] += len(fft_sig)

        # Signal right after movement
        for neg_level in [-2,-3,-4]:
            fft_sig = signal_filter(clean_sig[3000:-1000], mvmt_level,\
                                    neg_level, f_lo, f_hi, samp_rate, False, \
                                        chunk*buffer_size + 3000, neural_sig.physical_min(c))
            level = fft_arr.shape[0]-neg_level-5
            if len(fft_sig)>0:
                fft_arr[level,:] = (total_samp[level]/(total_samp[level] + len(fft_sig)))*fft_arr[level,:]\
                                       + (len(fft_sig)/(total_samp[level] + len(fft_sig))*(np.mean(fft_sig, axis=0)))                
                total_samp[level] += len(fft_sig)
                
                

    fft_arr_norm = (fft_arr-np.mean(fft_arr, axis=0))/np.std(fft_arr, axis=0)
    ## Plot the spectrogram
    fig1=plt.figure(figsize=[8,6])
    gs = GridSpec(100,100,bottom=0.18,left=0.18,right=0.88)
    ax1 = fig1.add_subplot(gs[:,0:7])
    ax2 = fig1.add_subplot(gs[:,11:87])
    ax3 = fig1.add_subplot(gs[:,91:])
    #np.array(range(max(mvmt_level)))/30.0, np.array(range(f_lo, f_hi)),
    X1 = np.tile(np.array(range(3,-1,-1)), (f_hi-f_lo,1))
    Y1 = np.tile(np.array(range(f_lo, f_hi)), (4,1)).T
    X2 = np.tile(np.array(range(0,time_lim-3))/30.0, (f_hi-f_lo,1))
    Y2 = np.tile(np.array(range(f_lo, f_hi)), (time_lim-3,1)).T
    X3 = np.tile(np.array(range(0,4)), (f_hi-f_lo,1))
    Y3 = np.tile(np.array(range(f_lo, f_hi)), (4,1)).T
    #pdb.set_trace()
    p1 = ax1.pcolormesh(X1,Y1,fft_arr_norm[:4,:].T)
    p2 = ax2.pcolormesh(X2,Y2,fft_arr_norm[3:-4,:].T)
    p3 = ax3.pcolormesh(X3,Y3,fft_arr_norm[-4:,:].T)
    cb = fig1.colorbar(p3, ax=ax3)
    ax2.set_xlabel("Seconds after movement onset")
    ax3.set_xlabel("Seconds after\n movement end")
    ax1.set_xlabel("Seconds before\n movement onset")
    ax1.set_ylabel("Frequency (Hz)")
    ax2.set_yticklabels('',visible=False)
    ax1.set_xticks([3,2,1,0])
    ax1.set_xticklabels(['3','2','1','0'])
    ax3.set_yticklabels('',visible=False)
    ax3.set_xticks([0,1,2,3])
    ax3.set_xticklabels(['0','1','2','3'])
    ax2.set_title("Power spectrogram for\n subject " + sbj_id + " on channel " + name)
   
    plt.savefig(output_file_loc + "movement_spectrogram_" + name + "_4.png")
    
        
        


