import matplotlib as mpl
mpl.use('Agg')
import sys
sys.path.append('/home/wangnxr/Documents/deeppose/tests')
import numpy as np
import csv
import argparse
import matplotlib.pyplot as plt
import pickle
import pdb
import cv2
import glob
#from test_flic_dataset import draw_joints
import os
import subprocess
from sklearn.cluster import KMeans
from pyESig2.vid.vid_start_end import get_len
from datetime import time, datetime, timedelta
import shutil
import scipy

joint_map = ['head', 'right wrist', 'left wrist', 'right elbow', 'left elbow',  'right shoulder', 'left shoulder']

def best_cluster(mini_window, model):
    distances = model.transform(np.vstack([mini_window[i:i+30] for i in xrange(30)]))

    best = scipy.stats.mode(np.where(distances==np.min(distances))[1])

    return best.mode[0]


def cluster_mvmt_hier(mvmt_vectors, vid_dir, sbj_id, day, save_fldr):
    primary_model = KMeans(n_clusters=100)
    primary_labels = primary_model.fit_predict(mvmt_vectors)
    temporal_windows_small = np.vstack([primary_labels[i:i+30] for i in range(0,len(primary_labels)-30,10)])
    temporal_windows_large = np.vstack([primary_labels[i:i+60] for i in range(0,len(primary_labels)-60,30)])

    secondary_model = KMeans(n_clusters=8)

    secondary_model.fit(temporal_windows_small)

    motion_type = [best_cluster(mini_window, secondary_model) for mini_window in temporal_windows_large]
    gen_motion_clips(motion_type, vid_dir, sbj_id, day, save_fldr)
    return np.array(motion_type)

def gen_motion_clips(labels, vid_dir, sbj_id, day, save_fldr):
    vid_files = sorted(glob.glob(vid_dir + "/%s_%s_*.avi" % (sbj_id, day)))
    vid_lengths = [timedelta(seconds=get_len(file)) for file in vid_files]
    vid_starts = [np.sum(vid_lengths[0:i]).seconds for i in xrange(1, len(vid_lengths))]
    vid_starts.insert(0, 0)
    for cluster in xrange(max(labels)+1):
        clip_locs = np.where(np.array(labels)==cluster)[0]
        if os.path.exists("tmp_vids"):
            shutil.rmtree("tmp_vids")
        os.makedirs("tmp_vids")

        for i, c in enumerate(clip_locs):

            vid = max(np.where(c>=vid_starts)[0])
            offset = c-vid_starts[vid]

            subprocess.call("ffmpeg -ss 00:0%i:%02i -i %s -t 00:00:01 -vcodec copy tmp_vids\\temp_%i.avi" % (offset/60, offset%60, vid_files[vid], i), shell=True)
        tmp_file = open("tmp_vids\\tmp.txt", "wb")
        tmp_file.writelines(["file \'tmp_vids\\temp_%i.avi\'\n" % i for i in xrange(len(clip_locs))])
        tmp_file.close()
        subprocess.call("ffmpeg -f concat -i tmp_vids\\tmp.txt -c copy %s\\cluster_%i.avi" % (save_fldr, cluster))


        # stitch together clips using ffmpeg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', required=True, help="Movement directory")
    parser.add_argument('-v', '--vid_dir', required=True, help="Video directory")
    parser.add_argument('-sbj', '--sbj_id', required=True, help="subject ID")
    parser.add_argument('-day', '--day', required=True, help="day")
    parser.add_argument('-s', '--save', required=True, help="Save directory" )
    args = parser.parse_args()
    mvmt_agg = []
    for file in sorted(glob.glob("%s/%s_%s_*_movement.p" % (args.dir, args.sbj_id, args.day))):
        mvmt_agg.append(pickle.load(open(file)))
    #pdb.set_trace()
    mvmt_agg = np.vstack(mvmt_agg)

    cluster_labels = cluster_mvmt_hier(mvmt_agg, args.vid_dir, args.sbj_id, args.day, args.save)
