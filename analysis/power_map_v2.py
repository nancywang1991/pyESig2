import argparse
import csv
import glob
import os
import cPickle as pickle
import numpy as np
import scipy.io
import pdb
import scipy.stats
import matplotlib.pyplot as plt
from scipy import signal

def main(ecog_loc, f_min, f_max):

    tracks = {"r_arm_1": [], "mv_0": []}
    tracks_final = {}
    significance = {}


    for track in tracks.iterkeys():
        displaymat = np.zeros(shape=(64, 129,85))
        print "Working on %s" % track
        for f, file in enumerate(sorted(glob.glob(ecog_loc + "/%s/*.npy" % track))):
            ecog = np.load(file)
            for c in range(64):
                f, t, Sxx = signal.spectrogram(ecog[c], 1000, noverlap=200)
                displaymat[c]+=Sxx


            frequency = np.zeros(shape=(64, (f_max-f_min)/2))
            for c in xrange(64):
                frequency[c, :] = np.abs(np.fft.fft(ecog[c,-500:]) ** 2)[f_min/2:f_max/2] -np.abs(np.fft.fft(ecog[c,-1500:-1000]) ** 2)[f_min/2:f_max/2]
            #if track=="r_arm_1" and np.mean(frequency[47])>3:
            #    print file
                #plt.plot(np.transpose(ecog[44:50,-3000:]))
                #plt.show()
            if np.median(np.sum(frequency, axis=1)) >100 or np.median(np.sum(frequency,axis=1)) <-100 or np.max(abs(np.sum(frequency,axis=1)))>1000:
                print file
                #print np.sum(frequency, axis=1)
                #plt.plot(np.transpose(ecog))
                #plt.show()
            else:
                tracks[track].append(frequency)
        displaymat /= float(len(glob.glob(ecog_loc + "/%s/*.npy" % track)))

        for c in range(64):
            for freq in xrange(displaymat.shape[1]):
                mean = np.mean(displaymat[c,freq])
                std = np.std(displaymat[c,freq])
                displaymat[c, freq,:] -= mean
                displaymat[c, freq, :] /=std
        plt.pcolormesh(t, f, displaymat[7])
        plt.show()
        pdb.set_trace()
        plt.pcolormesh(t, np.arange(64), displaymat[:,30])
        plt.show()
        plt.pcolormesh(t, np.arange(64), displaymat[:,80])
        plt.show()
        #plt.imshow(np.sum(np.array(tracks[track])[:500], axis=2), clim=(-10,10))
        #plt.show()
    #frequency_mean = np.mean(tracks["mv_0"], axis=0)
    #frequency_std = np.std(tracks["mv_0"], axis=0)
    #for t,track in tracks.iteritems():
    #    tracks[t] = [(freq-frequency_mean)/frequency_std for freq in track]
	
    for track in tracks.iterkeys():
        #significance[track] = scipy.stats.ttest_ind(np.sum(tracks[track], axis=2), np.sum(tracks["mv_0"], axis=2), equal_var=False)
        tracks_final[track] = np.mean(np.array(tracks[track]), axis=0)

    print significance
    return tracks_final, significance




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--power_dir", required=True, help="Power frequency directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    parser.add_argument('-f_min', '--frequency_min', required=True, help="minimum frequency", type=int)
    parser.add_argument('-f_max', '--frequency_max', required=True, help="maximum frequency", type=int)
    args = parser.parse_args()

    tracks_final, significance = main(args.power_dir, args.frequency_min, args.frequency_max)
    scipy.io.savemat(args.save_dir + "arm_mvmt_%i_%i.mat" % (args.frequency_min, args.frequency_max,), tracks_final)
    scipy.io.savemat(args.save_dir + "arm_significance_%i_%i.mat" % (args.frequency_min, args.frequency_max,), significance)
