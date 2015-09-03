import cPickle as pickle
import numpy as np
import sys
from scipy.stats import pearsonr
from freq.signal_filter import butter_lowpass_filter
from util.error import varError
import matplotlib.pyplot as plt
import pdb

def main(sound, mvmt, cluster):
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

    for c, values in enumerate(input_file_cluster.T):
        print("Sound correlation with channel " + str(c)
               + str(pearsonr(sound_reduced, values[start:end])))
        print("Mvmt correlation with channel " + str(c)
              + str(pearsonr(mvmt_reduced, values[start:end])))
    plt.plot(sound_reduced)
    plt.show()
    print ("Sound correlation with mvmt "
           + str(pearsonr(sound_reduced, mvmt_reduced)))

if __name__ == "__main__":
    if not(len(sys.argv) == 4):
        raise varError("Arguments should be <Sound File> <Movement File>\
                         <Cluster Result File>")
    main(*sys.argv[1:])
