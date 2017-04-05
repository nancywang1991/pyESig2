import numpy as np
#import edflib.edfreader as edfreader

from pyESig2.freq.signal_filter import (butter_bandpass_filter, butter_bandstop_filter)
import glob
import pickle
import os
import argparse
from pyESig2.preprocess.misc_info import patient_channels
import pdb


def clean_signal(sig, samp_rate):

    band_pass_sig = butter_bandpass_filter(sig, 0.1, 210, samp_rate, order=2)
    band_stop_sig = butter_bandstop_filter(band_pass_sig, 59, 61, samp_rate, order=2)
    clean_sig = butter_bandstop_filter(band_stop_sig, 119, 121, samp_rate, order=2)

    return clean_sig
#-------------------------------Main Function--------------------------------
def transform_file(f, file, f_lo, f_hi, win_size, step_size, save_file_loc, n_channels):

    neural_sig = edfreader.EdfReader(file)
    samp_rate = 1000
    if neural_sig.getSampleFrequency(0) < 999:
        pdb.set_trace()
    window_size = int(samp_rate*win_size)
    step_size = int(samp_rate*step_size)
    buffer_size = step_size*100
    f_lo = int(f_lo*win_size) + 1
    f_hi = int(f_hi*win_size) + 1

    size = int(neural_sig.samples_in_file(1))
    frequency = np.zeros(shape=(n_channels, (f_hi-f_lo)))
    cnt=0
    if size > buffer_size*3:
        for chunk in xrange(0,size-3*buffer_size, buffer_size):
            if not os.path.isfile("%s%s_%i.p" % (save_file_loc, f, (chunk+buffer_size)/(step_size)-1)):
                print ("Processing chunk %i of %i in file %s" %(chunk/(buffer_size),(size-samp_rate)/(buffer_size),f))
                chan_sig = np.zeros(shape=(n_channels, buffer_size))
                for c in xrange(1, n_channels + 1):
                    sig = np.zeros(buffer_size*4)
                    neural_sig.readsignal(c, chunk-buffer_size, buffer_size*3, sig)
                    clean_sig = clean_signal(sig, samp_rate)
                    chan_sig[c-1,:] = clean_sig[buffer_size:buffer_size*2]

                for sub_chunk in xrange(0,buffer_size,step_size):
                   if not os.path.isfile("%s%s_%i.p" % (save_file_loc, f, cnt)):
                        for c in xrange(1, n_channels+1):
                            frequency[c-1,:] = (np.abs(np.fft.fft( chan_sig[c-1,sub_chunk:sub_chunk+window_size]))**2)[f_lo:f_hi]

                        if sum(np.ndarray.flatten(frequency)) > 0:
                            pickle.dump(frequency, open("%s%s_%i.p" % (save_file_loc, f, cnt), "wb"))
                   else:
                        print ("%s%s_%i.p is skipped" %(save_file_loc , f, cnt))
                   cnt += 1
            else:
                cnt += buffer_size/(step_size)


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--subject_id', type=str, help = "Subject ID for fft extraction", required=True)
parser.add_argument('-d', '--day', type=int, help="Day of subject stay to extract", required=True)
parser.add_argument('-eeg', '--eeg_fldr', type=str, help = "Folder location of eeg edf files", default="D:\\NancyStudyData\\ecog\\edf\\")
parser.add_argument('-save', '--save_fldr', type=str, help = "Save folder location", default="E:\\ratio_mapping\\ecog_processed\\")
parser.add_argument('-f_lo', '--f_lo', type=int, help = "Low end  of frequency cutoff", default = 1)
parser.add_argument('-f_hi', '--f_hi', type=int, help = "High end  of frequency cutoff", default = 150)
parser.add_argument('-w_size', '--win_size', type=float, help="Number of seconds in window", default = 2 )
parser.add_argument('-s_size', '--step_size', type=float, help="Number of seconds between windows", default = 1)

args = parser.parse_args()

files = glob.glob("%s%s\\*_%i.edf" % (args.eeg_fldr, args.subject_id, args.day))
#pdb.set_trace()
for file in files:
    if not (file[-4:]=="misc" or file[-4:]=="Misc" or file[-5:]=="other"):
        parent, num = file.split('_')
        f, ext = num.split('.')
        if not os.path.exists(args.save_fldr+args.subject_id + "\\"):
            os.makedirs(args.save_fldr+args.subject_id + "\\")
        transform_file(f, file, args.f_lo, args.f_hi, args.win_size, args.step_size,
                   args.save_fldr+args.subject_id+"\\", patient_channels[args.subject_id])
