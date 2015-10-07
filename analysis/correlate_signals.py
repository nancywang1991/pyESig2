import cPickle as pickle
import numpy as np
import sys
from scipy.stats import pearsonr
from freq.signal_filter import butter_lowpass_filter
from util.error import varError
import matplotlib.pyplot as plt
import pdb
import copy

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
    end = input_file_cluster.shape[0]
    sound_thresh = np.median(input_file_sound)
    mvmt_thresh = np.median(input_file_mvmt)
    #Number of frames in unit
    nf=sr*15.0

    sound_reduced = np.zeros(input_file_cluster.shape[0])
    mvmt_reduced = np.zeros(input_file_cluster.shape[0])
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

        sound_corr[c]=pearsonr(sound_reduced, values[start:end])[0]
        mvmt_corr[c]=pearsonr(mvmt_reduced, values[start:end])[0]

    mvmt_channel = np.where(mvmt_corr==np.nanmax(mvmt_corr))[0][0]
    sound_channel = np.where(sound_corr==np.nanmax(sound_corr))[0][0]

    if (mvmt_channel==sound_channel):
        if np.nanmax(mvmt_corr)>np.nanmax(sound_corr):
            sound_corr_temp = copy.deepcopy(sound_corr)
            sound_corr_temp[mvmt_channel]=0
            sound_channel = np.where(sound_corr_temp==np.nanmax(sound_corr_temp))[0][0]
        else:
            mvmt_corr_temp = copy.deepcopy(mvmt_corr)
            mvmt_corr_temp[sound_channel]=0
            mvmt_channel = np.where(mvmt_corr_temp==np.nanmax(mvmt_corr_temp))[0][0]
    average = np.mean(np.vstack([mvmt_corr, sound_corr]), axis=0)

    rest_channel = np.where(average==np.nanmin(average))[0][0]
    print mvmt_corr[mvmt_channel]
    print sound_corr[sound_channel]
    print average[rest_channel]
    return {'Mvmt':mvmt_channel,'Sound':
           sound_channel,'Rest':rest_channel}

def correlate_section(sound, mvmt, cluster, sections):
    """ Calculates correlation between cluster results and sound and movement
    levels """
    #Load files
    input_file_orig = pickle.load(open(sound, "rb"))
    input_file_sound = butter_lowpass_filter(input_file_orig, 0.1, 30)

    input_file_mvmt = pickle.load(open(mvmt, "rb"))
    input_file_cluster = pickle.load(open(cluster, "rb"))
    #Sampling Rate
    sr = 30

    sound_thresh = np.median(input_file_sound)
    mvmt_thresh = np.median(input_file_mvmt)
    #Number of frames in unit
    nf=sr*15.0

    sound_reduced = np.zeros(input_file_cluster.shape[0])
    mvmt_reduced = np.zeros(input_file_cluster.shape[0])
    for i in xrange(start,end):
        # Reduce Sound and movement resolution by percentage
        # of values above threshold
        sound_reduced[i] = np.where(input_file_sound[i*nf:(i+1)*nf]
                                    > sound_thresh)[0].shape[0]/nf
        mvmt_reduced[i] = np.where(input_file_mvmt[i*nf:(i+1)*nf]
                                    > mvmt_thresh)[0].shape[0]/nf
    sound_sections=[]
    mvmt_sections=[]
    cluster_sections=[]
    for section in sections:
        sound_sections.append(sound_reduced[:section[0]:section[0]+section[1]])
        mvmt_sections.append(mvmt_reduced[:section[0]:section[0]+section[1]])
        cluster_sections.append(input_file_cluster[:section[0]:section[0]+section[1],:])
    sound_sections=np.hstack(sound_sections)
    mvmt_sections=np.hstack(mvmt_sections)
    cluster_sections=np.hstack(cluster_sections)
    sound_corr = np.zeros(input_file_cluster.shape[1])
    mvmt_corr = np.zeros(input_file_cluster.shape[1])
    for c, values in enumerate(cluster_sections.T):

        sound_corr[c]=pearsonr(sound_sections, values)[0]
        mvmt_corr[c]=pearsonr(mvmt_sections, values)[0]

    mvmt_channel = np.where(mvmt_corr==np.nanmax(mvmt_corr))[0][0]
    sound_channel = np.where(sound_corr==np.nanmax(sound_corr))[0][0]

    if (mvmt_channel==sound_channel):
        if np.nanmax(mvmt_corr)>np.nanmax(sound_corr):
            sound_corr_temp = copy.deepcopy(sound_corr)
            sound_corr_temp[mvmt_channel]=0
            sound_channel = np.where(sound_corr_temp==np.nanmax(sound_corr_temp))[0][0]
        else:
            mvmt_corr_temp = copy.deepcopy(mvmt_corr)
            mvmt_corr_temp[sound_channel]=0
            mvmt_channel = np.where(mvmt_corr_temp==np.nanmax(mvmt_corr_temp))[0][0]
    average = np.mean(np.vstack([mvmt_corr, sound_corr]), axis=0)

    rest_channel = np.where(average==np.nanmin(average))[0][0]
    print mvmt_corr[mvmt_channel]
    print sound_corr[sound_channel]
    print average[rest_channel]
    return {'Mvmt':mvmt_channel,'Sound':
           sound_channel,'Rest':rest_channel}

if __name__ == "__main__":
    if not(len(sys.argv) == 4):
        raise varError("Arguments should be <Sound File> <Movement File>\
                         <Cluster Result File>")
    correlate(*sys.argv[1:])
