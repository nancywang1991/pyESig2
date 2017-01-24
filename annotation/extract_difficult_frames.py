import argparse
import glob
import numpy as np
import os
import pdb
from pyESig2.vid.my_video_capture import my_video_capture
from pyESig2.movement.joint_movement_norm import numerate_coords
import cv2

def main(joints_file, vid_file, save_dir):
    poses = np.array([numerate_coords(row) for row in (open(joints_file)).readlines()])
    downsample_fact = 6
    difficult_frames = []
    for p, pose in enumerate(poses):
        if p%downsample_fact==0 and ((p-difficult_frames[-1])>30 or len(difficult_frames)==0) and np.any(pose[:,2]<0.1):
            difficult_frames.append(p)

    vid_name = os.path.split(vid_file)[-1].split('.')[0]
    vid_file = my_video_capture(vid_file, 30/downsample_fact)

    for f in difficult_frames:
        if f%downsample_fact==0:
            vid_file.forward_to(f/downsample_fact)
            img = vid_file.read()
            cv2.imwrite(os.path.join(save_dir, "%s_%i.png" %(vid_name,f)), img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', required=True, help="Joint coordinate directory")
    parser.add_argument('-v', '--vid_dir', required=True, help="video directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()

    for file in sorted(glob.glob(args.dir + "/*.txt")):
        #pdb.set_trace()
        sbj_id, day, vid_num = os.path.split(file)[-1].split(".")[0].split("_")
        vid_name = os.path.join(args.vid_dir, "%s_%s_%s.avi" %( sbj_id, day, vid_num))
        main(file, vid_name, args.save_dir)

