import glob
import argparse
import os
import pickle
import numpy as np
import subprocess
from pyESig2.movement.joint_movement_norm import *
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

def main(file, vid_name, joints_file, crop_file, save_dir):
    mv_file = pickle.load(open(file))
    right_arm_mvmt = mv_file[:, 1]
    start = -1

    # Pose calculation
    crop_coords = np.array([np.array([int(coord) for coord in crop_coord.split(',')]) for crop_coord in
                            open(crop_file).readlines()])
    poses = np.array([numerate_coords(row) for row in (open(joints_file)).readlines()])
    poses_normalized = np.array(
        [normalize_to_camera(row, crop_coord) for row, crop_coord in zip(poses, crop_coords)])
    poses_normalized_filtered = filter_confidence(poses_normalized, poses[:, :, 2])
    poses_normalized = my_savgol_filter(poses_normalized_filtered, 21, 3, axis=0)

    mvmt_profiles_x = []
    mvmt_profiles_y = []
    for f in range(0, len(mv_file), 2):
        if np.mean(right_arm_mvmt[f:f+5])>1.5 and np.all(right_arm_mvmt[f-10:f] >= 0) and np.mean(right_arm_mvmt[f-10:f]) < 0.5:
            start = f
        if start > 0 and np.all(right_arm_mvmt[f:f+5]<1) and (f-start)>30:# and np.all(right_arm_mvmt[f:f+2] >= 0):
            end = f
            savename = "%s/%s_%i_%i.avi" % (save_dir, vid_name.split("/")[-1].split(".")[0], start, end)
            subprocess.call("ffmpeg -i %s -ss %f -c copy -t %f %s" % (vid_name, start / 30.0, (end - start) / 30.0, savename), shell=True)
            mvmt_profiles_x = poses_normalized[end,1,0] - poses_normalized[start, 1, 0]
            mvmt_profiles_y = poses_normalized[end, 1, 1] - poses_normalized[start, 1, 1]
            start = -1
    plt.scatter(mvmt_profiles_x, mvmt_profiles_y)
    plt.savefig(save_dir + "summary.png")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--joint_dir', required=True, help="Joint directory")
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-v', '--vid_dir', required=True, help="video directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()

    for file in sorted(glob.glob(args.mv_dir + "/*.p")[64:]):
        #pdb.set_trace()
        sbj_id, day, vid_num, _ = os.path.split(file)[-1].split(".")[0].split("_")
        vid_name = os.path.join(args.vid_dir, "%s_%s_%s.avi" %( sbj_id, day, vid_num))
        joint_file = "%s/%s_%s/%s_%s_%s.txt" % (args.joint_dir, sbj_id, day, sbj_id, day, vid_num)
        crop_file = "%s/crop_coords/%s_%s_%s.txt" % (args.joint_dir, sbj_id, day, vid_num)
        main(file, vid_name, joint_file, crop_file, args.save_dir)
