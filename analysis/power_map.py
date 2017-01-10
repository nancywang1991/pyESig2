import argparse
import csv
import glob
import os
import cPickle as pickle
import numpy as np
import scipy.io
import pdb
import scipy.stats

def main(mv_loc, ecog_loc, f_min, f_max, vid_start_end):

    track_labels = ["head", "wrist_r", "wrist_l","elbow_r", "elbow_l", "shoulder_r", "shoulder_l"]
    tracks_final = {"head": [], "shoulder_l": [], "shoulder_r": [], "wrist_r": [], "wrist_l": [], "elbow_r": [],
                  "elbow_l": []}
    tracks_all = {"head": [], "shoulder_l": [], "shoulder_r": [], "wrist_r": [], "wrist_l": [], "elbow_r": [],
                  "elbow_l": [], "None": []}
    significance = {}

    sbj_id, day, vid_num, _ = sorted(glob.glob(mv_loc + "\\*.p"))[0].split("\\")[-1].split(".")[0].split("_")
    mean_ecog = []
    for f, file in enumerate(sorted(glob.glob("%s\\%s\\%s_*.p" % (ecog_loc, sbj_id, day)))):
        mean_ecog.append(np.mean(pickle.load(open(file))))

    overall_mean = np.mean(np.array(mean_ecog))
    overall_std = np.std(np.array(mean_ecog))

    for f, file in enumerate(sorted(glob.glob(mv_loc + "\\*.p"))[:20]):
        tracks = {"head": [], "shoulder_l": [], "shoulder_r": [], "wrist_r": [], "wrist_l": [], "elbow_r": [],
                  "elbow_l": [], "None": [], "all": []}
        print "Working on %s" % file
        sbj_id, day, vid_num, _ = file.split("\\")[-1].split(".")[0].split("_")
        mvmt = pickle.load(open(file))

        time = (vid_start_end["start"][int(vid_num)]-vid_start_end["start"][0]).total_seconds()*2
        for t in range(0, len(mvmt), 15):
            ecog = pickle.load(open("%s\\%s\\%s_%i.p" % (ecog_loc, sbj_id, day, int(time+t/15))))[:,f_min*2:f_max*2]
            if np.abs(np.mean(ecog)-overall_mean)/overall_std < 4:
                tracks["all"].append(ecog)
                if np.max(mvmt[t:t+15]) < 2 and np.max(mvmt[t:t+15]) >=0 :
                    tracks["None"].append(ecog)
                    tracks_all["None"].append(ecog)
                else:
                    for j in xrange(len(mvmt[t])):
                        if np.max(mvmt[t:t+15,j])>5 and np.max(mvmt[t:t+15,j])<500:
                            tracks[track_labels[j]].append(ecog)
                            tracks_all[track_labels[j]].append(ecog)

        if tracks["all"] is not None and len(tracks["None"]) > 1:

            control_mean = np.mean(np.sum(np.array(tracks["None"]), axis=2), axis=0)
            control_std = np.std(np.sum(np.array(tracks["None"]), axis=2), axis=0)

            for track, value in tracks.iteritems():
                if not track == "None" and not track == "all" and len(value) > 1:
                    tracks_final[track].append((np.mean(np.sum(np.array(value), axis=2), axis=0)-control_mean)/control_std)

    for track in tracks_final.iterkeys():
        #pdb.set_trace()
        significance[track] = scipy.stats.ttest_ind(np.sum(tracks_all[track], axis=2), np.sum(tracks_all["None"], axis=2), equal_var=False)
        tracks_final[track] = np.mean(np.array(tracks_final[track]), axis=0)

    return tracks_final, significance




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

    tracks_final, significance = main(args.mv_dir, args.power_dir, args.frequency_min, args.frequency_max, vid_start_end)
    scipy.io.savemat(args.save_dir + "arm_mvmt_%i_%i.mat" % (args.frequency_min, args.frequency_max,), tracks_final)
    scipy.io.savemat(args.save_dir + "arm_significance_%i_%i.mat" % (args.frequency_min, args.frequency_max,), significance)
