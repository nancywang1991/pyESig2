import argparse
import csv
import glob
import os
import cPickle as pickle
import numpy as np
import scipy.io
import pdb
import scipy.stats

def main(ecog_loc, f_min, f_max):

    tracks = {"arm_r_1": [], "mv_0": []}
    tracks_final = {}
    for track in tracks.iterkeys():
        print "Working on %s" % track
        for f, file in enumerate(sorted(glob.glob(ecog_loc + "/%s/*.npy" % track))[:20]):
            ecog = np.load(file)
            frequency = np.zeros(len(64, f_max-f_min))
            for c in xrange(len(ecog)):
                frequency[c, :] = np.abs(np.fft.fft(ecog[c,100:-100]) ** 2)[f_min:f_max]
            tracks[track].append(frequency)
    frequency_mean = np.mean(np.hstack([track for track in tracks.itervalues()]), axis=1)
    frequency_std = np.std(np.hstack([track for track in tracks.itervalues()]), axis=1)

    for track in tracks.itervalues():
        track = [(freq-frequency_mean)/frequency_std for freq in track]

    for track in tracks_final.iterkeys():
        #pdb.set_trace()
        significance[track] = scipy.stats.ttest_ind(np.sum(tracks["arm_mv_1"], axis=2), np.sum(tracks["mv_0"], axis=2), equal_var=False)
        tracks_final[track] = np.mean(np.array(tracks[track]), axis=0)

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
