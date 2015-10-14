import numpy as np
import edflib._edflib as edflib
import pdb
from pyESig2.Signal.signal_filter import (butter_bandpass_filter, butter_highpass_filter)
import glob
import pickle
import matplotlib.pyplot as plt
from multiprocessing import Process
import os

#-------------------------------Main Function--------------------------------
def transform_file(f, file, f_lo, f_hi, save_file_loc, n_channels):
    neural_sig = edflib.Edfreader(file)
    samp_rate = int(neural_sig.samplefrequency(0))
    buffer_size = samp_rate*100
    window_size = samp_rate*2


    size = int(neural_sig.samples_in_file(1))
    frequency = np.zeros(shape=(n_channels, (f_hi-f_lo)/3))
    cnt=0
    if size > buffer_size*3:
        for chunk in xrange(0,size-3*buffer_size, buffer_size):
            if not os.path.isfile(save_file_loc + str(f)
                                                + "_" + str((chunk+1)/window_size) + ".p"):

                print ("Processing chunk " + str(chunk/(buffer_size)) + " of "
                + str((size-samp_rate)/(buffer_size)) + " in file " + str(f) + "\n")
                chan_sig = np.zeros(shape=(n_channels, buffer_size))
                for c in xrange(1, 1+n_channels):
                    sig = np.zeros(buffer_size*4)
                    neural_sig.readsignal(c, chunk-buffer_size,
                                          buffer_size*3, sig)
                    clean_sig = butter_bandpass_filter(sig, 0.1, 160, samp_rate, order=2)
                    chan_sig[c-1,:] = clean_sig[buffer_size:buffer_size*2]


                for sub_chunk in xrange(0,buffer_size-window_size,window_size):
##                    if not os.path.isfile(save_file_loc + str(f)
##                                                    + "_" + str(cnt) + ".p"):
                    if 1:
                        for c in xrange(1, 1+n_channels):
                            frequency[c-1,:] = (np.abs(np.fft.fft(
                                chan_sig[c-1,sub_chunk:sub_chunk+window_size]))**2)[f_lo:f_hi:3]
                       #pickle.dump(frequency, open(save_file_loc + str(f)
                       #                             + "_" + str(cnt) + ".p", "wb"))
                        #print (save_file_loc + str(f)
                        #                            + "_" + str(cnt) + ".p" + " saved")

                        y, x = np.mgrid[slice(0, n_channels, 1),
                        slice(0, 100*3, 3)]
                        plt.pcolormesh(x,y,frequency, cmap='RdBu', vmin=-1, vmax=1)
                        plt.axis([x.min(), x.max(), y.min(), y.max()])
                        plt.colorbar()
                        #plt.title(track)
                        plt.xlabel("Frequency")
                        plt.ylabel("Channel")
                    else:
                        print (save_file_loc + str(f)
                                                    + "_" + str(cnt) + ".p" + " skipped")
                    cnt+=1
            else:
                cnt += buffer_size/window_size

#---------------------------------Subject Params-------------------------------

#sbj_id = "fcb01f7a"
#n_channels = 84
#sbj_id = "e70923c4"
#n_channels = 86
#sbj_id = "a86a4375"
#n_channels = 104
#sbj_id = "ffb52f92"
#n_channels = 106
sbj_id = "d6532718"
n_channels = 82
eeg_file_loc = "/media/nancy/Picon/NancyStudyData/ecog/edf/"
save_file_loc = "/media/nancy/Picon/ecog_processed/" + sbj_id + "/"
f_lo = 1
f_hi = 301


#--------------------------------Signal Extraction-----------------------------

files = glob.glob(eeg_file_loc + sbj_id + "/*")


for file in files:
    if not (file[-4:]=="misc"):
        parent, num = file.split('_')
        f, ext = num.split('.')
        #p = Process(target=transform_file,
        #            args=(f, file, f_lo, f_hi, save_file_loc, n_channels))
        #p.start()
        transform_file(f, file, f_lo, f_hi, save_file_loc, n_channels)
#p.join()



