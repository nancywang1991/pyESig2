import cPickle as pickle
import numpy as np
import sys
from scipy.stats import pearsonr
from freq.signal_filter import butter_lowpass_filter
from util.error import varError
import matplotlib.pyplot as plt
import pdb

def correlate(sound, mvmt, cluster):
    """ Calculates correlation between cluster results and sound and movement
    levels """
    #Load files
    input_file_orig = pickle.load(open(sound, "rb"))
    input_file_sound = butter_lowpass_filter(input_file_orig, 0.1, 30)

    input_file_mvmt = pickle.load(open(mvmt, "rb"))
    input_file_cluster = pickle.load(open(cluster, "rb"))
    #Sampling Rate
    sr = 30
    
    start = 0
    end = 270
    sound_thresh = np.median(input_file_sound)
    mvmt_thresh = np.median(input_file_mvmt)
    #Number of frames in minute
    nf=sr*60.0
    
    sound_reduced = np.zeros(270)
    mvmt_reduced = np.zeros(270)
    for i in xrange(start,end):
        # Reduce Sound and movement resolution by percentage
        # of values above threshold
        sound_reduced[i] = np.where(input_file_sound[i*nf:(i+1)*nf] 
                                    > sound_thresh)[0].shape[0]/nf
        mvmt_reduced[i] = np.where(input_file_mvmt[i*nf:(i+1)*nf]
                                    > mvmt_thresh)[0].shape[0]/nf
    sound_corr = np.zeros(input_file_cluster.shape[1])
    mvmt_corr = np.zeros(input_file_cluster.shape[1])
    for c, values in enumerate(input_file_cluster.T):
        sound_corr[c]=pearsonr(sound_reduced, values[start:end])
        mvmt_corr[c]=pearsonr(sound_reduced, values[start:end])

    mvmt_channel = mvmt_corr.index(mvmt.max())
    sound_channel = sound_corr.index(sound.max())
    average = np.mean([mvmt_corr, sound_corr])
    rest_channel = average.index(average.min())

    return {'mvmt':input_file_cluster[:,mvmt_channel],'sound':
           input_file_cluster[:,sound_channel],'rest':input_file_cluster[:,rest_channel]}

if __name__ == "__main__":
    if not(len(sys.argv) == 4):
        raise varError("Arguments should be <Sound File> <Movement File>\
                         <Cluster Result File>")
    correlate(*sys.argv[1:])
