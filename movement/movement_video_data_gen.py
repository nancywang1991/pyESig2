import argparse
import glob
import cPickle as pickle
import csv
import numpy as np
import os
import pdb
import matplotlib.pyplot as plt
from pyESig2.vid.my_video_capture import my_video_capture
import cv2

def scoring(truth, predicted):
    plt.plot(np.array(range(len(truth)))/30.0, truth*5, label="truth")
    plt.plot(np.array(range(len(truth)))/30.0, predicted*2, label="predicted")
    plt.ylim([0,6])
    plt.legend()
    plt.show()
    pred_locs = np.where(predicted==1)[0]
    for loc in pred_locs:
        predicted[loc-15:loc+15] = 1
    true_correct = sum(np.logical_and(predicted,truth==1))
    true = sum(truth)
    detected = sum(predicted)

    precision = true_correct/float(detected)
    recall = true_correct/true

    return [precision, recall, true/30.0]

def main(mv_file, vid_file, day, sbj_id, vid_num, writer):
    mv_file = pickle.load(open(mv_file))
    vid_file = my_video_capture(vid_file, 30)
    vid_name = vid_file.split("/")[-1].split('.')[0]
    left_arm_mvmt = np.sum(mv_file[:,(2,4,6)], axis=1)
    right_arm_mvmt = np.sum(mv_file[:,(1,3,5)], axis=1)
    head_mvmt = mv_file[:,0]

    if not os.path.exists(args.save_dir + "/l_arm_1"):
        os.makedirs(args.save_dir + "/head_0")
        os.makedirs(args.save_dir + "/head_1")
        os.makedirs(args.save_dir + "/r_arm_0")
        os.makedirs(args.save_dir + "/r_arm_1")
        os.makedirs(args.save_dir + "/l_arm_0")
        os.makedirs(args.save_dir + "/l_arm_1")

    for f in range(15,len(mv_file)):
        img = vid_file.read()
        if left_arm_mvmt[f]>2:
            cv2.imwrite("%s/l_arm_1/%s_%i.png" %(args.save_dir, vid_name, f), img)
        elif left_arm_mvmt[f]>0 and left_arm_mvmt<1:
            cv2.imwrite("%s/l_arm_0/%s_%i.png" % (args.save_dir, vid_name, f), img)
        if right_arm_mvmt[f]>2:
            cv2.imwrite("%s/r_arm_1/%s_%i.png" %(args.save_dir, vid_name, f), img)
        elif right_arm_mvmt[f]>0 and right_arm_mvmt<1:
            cv2.imwrite("%s/r_arm_0/%s_%i.png" % (args.save_dir, vid_name, f), img)
        if head_mvmt[f]>2:
            cv2.imwrite("%s/head_1/%s_%i.png" %(args.save_dir, vid_name, f), img)
        elif head_mvmt[f]>0 and head_mvmt<1:
            cv2.imwrite("%s/head_0/%s_%i.png" % (args.save_dir, vid_name, f), img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-l', '--vid_dir', required=True, help="video directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()
    for file in glob.glob(args.mv_dir + "/*.p"):
        sbj_id, day, vid_num, _ = file.split("/")[-1].split(".")[0].split("_")
        vid_name = "%s/%s_%s_%s.avi" %(args.vid_dir, sbj_id, day, vid_num)
        main(file, args.vid_dir, day, sbj_id, vid_num, args.save_dir)

