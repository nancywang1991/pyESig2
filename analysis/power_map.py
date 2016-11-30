import argparse
import csv
import glob
import os
import cPickle as pickle
import numpy as np
import scipy.io
import pdb

def main(mv_loc, ecog_loc, f_min, f_max, vid_start_end):

    track_labels = ["head", "wrist_r", "wrist_l","elbow_r", "elbow_l", "shoulder_r", "shoulder_l"]
    tracks_final = {"head": [], "shoulder_l": [], "shoulder_r": [], "wrist_r": [], "wrist_l": [], "elbow_r": [],
                  "elbow_l": []}

    for f, file in enumerate(sorted(glob.glob(mv_loc + "\\*.p"))):
        tracks = {"head": [], "shoulder_l": [], "shoulder_r": [], "wrist_r": [], "wrist_l": [], "elbow_r": [],
                  "elbow_l": [], "none": [], "all": []}
        print "Working on %s" % file
        sbj_id, day, vid_num, _ = file.split("\\")[-1].split(".")[0].split("_")
        mvmt = pickle.load(open(file))

        time = (vid_start_end["start"][int(vid_num)]-vid_start_end["start"][0]).total_seconds()*2
        for t in range(0, len(mvmt), 15):

            ecog = pickle.load(open("%s\\%s\\%s_%i.p" % (ecog_loc, sbj_id, day, int(time+t/15))))[:,f_min*2:f_max*2]
            tracks["all"].append(ecog)
            if np.max(mvmt[t:t+15]) < 5 and np.max(mvmt[t:t+15]) >=0 :
                tracks["none"].append(ecog)
            else:
                for j in xrange(len(mvmt[t])):
                    if np.max(mvmt[t:t+15,j])>20 and np.max(mvmt[t:t+15,j])<500:
                        tracks[track_labels[j]].append(ecog)
        if tracks["all"] is not None:
            control_mean = np.mean(np.sum(np.array(tracks["none"]), axis=2), axis=0)
            control_std = np.std(np.sum(np.array(tracks["none"]), axis=2), axis=0)

        for track, value in tracks.iteritems():
            if not track == "none" and not track == "all" and len(value) > 1:
                tracks_final[track].append((np.mean(np.sum(np.array(value), axis=2), axis=0)-control_mean)/control_std)


    for track in tracks_final.iterkeys():

        tracks_final[track] = np.mean(np.array(tracks_final[track]), axis=0)

    return tracks_final




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument("-p", "--power_dir", required=True, help="Power frequency directory")
    parser.add_argument("-v", "--vid_start_end", required=True, help="vid_start_end file")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    parser.add_argument('-f_min', '--frequency_min', required=True, help="minimum frequency", type=int)
    parser.add_argument('-f_max', '--frequency_max', required=True, help="maximum frequency", type=int)
    args = parser.parse_args()
    vid_start_end = pickle.load(open(args.vid_start_end))

    tracks_final = main(args.mv_dir, args.power_dir, args.frequency_min, args.frequency_max, vid_start_end)
    scipy.io.savemat(args.save_dir + "arm_mvmt_%i_%i.mat" % (args.frequency_min, args.frequency_max,), tracks_final)
