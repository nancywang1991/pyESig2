import glob
import argparse
import os
import pickle
import numpy as np
import subprocess

def main(file, vid_name, save_dir):
    mv_file = pickle.load(open(file))
    right_arm_mvmt = mv_file[:, 1]
    start = -1
    for f in range(0, len(mv_file), 2):
        if np.mean(right_arm_mvmt[f:f+5])>1 and np.all(right_arm_mvmt[f-10:f] >= 0) and np.mean(right_arm_mvmt[f-10:f]) < 0.5:
            start = f
        if start > 0 and np.mean(right_arm_mvmt[f:f+5])<0.5 and np.all(right_arm_mvmt[f:f+5] >= 0):
            end = f
            savename = "%s/%s_%i_%i.avi" % (save_dir, vid_name.split("/")[-1].split(".")[0], start, end)
            subprocess.call(
                "ffmpeg -i %s -ss %i -c copy -t %i %s" % (vid_name, start / 30, int(round(end - start) / 30.0), savename),
                shell=True)
            start = -1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-v', '--vid_dir', required=True, help="video directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()

    for file in sorted(glob.glob(args.mv_dir + "/*.p")[64:]):
        #pdb.set_trace()
        sbj_id, day, vid_num, _ = os.path.split(file)[-1].split(".")[0].split("_")
        vid_name = os.path.join(args.vid_dir, "%s_%s_%s.avi" %( sbj_id, day, vid_num))
        main(file, vid_name, args.save_dir)
