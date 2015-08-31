import cPickle as pickle
import numpy as np
import pdb
from pyESig2.freq.signal_filter \
    import butter_bandpass_filter, butter_lowpass_filter
from scipy.stats import pearsonr

def main(sound, mvmt, cluster):
    """ Calculates correlation between cluster results and sound and movement
    levels """
    #Load files
    input_file_sound = pickle.load(open(sound, "rb"))
    input_file_mvmt = pickle.load(open(mvmt, "rb"))
    input_file_cluster = pickle.load(open(cluster, "rb"))
    #Sampling Rate
    sr = 30
    
    start = 0
    end = 270
    sound_thresh = 10**15
    mvmt_thresh = 1
    #Number of frames in minute
    nf=sr*60
    
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

    print ("Sound correlation with mvmt "
           + str(pearsonr(sound_reduced, mvmt_reduced)))

if __name__ == "__main__":
    if not(len(sys.argv) == 4):
        raise varError("Arguments should be <Sound File> <Movement File>\
                         <Cluster Result File>")
    main(sys.argv[1:])
