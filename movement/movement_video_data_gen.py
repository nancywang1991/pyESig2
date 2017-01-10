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

def main(mv_file, vid_file, save_dir, offset):
    mv_file = pickle.load(open(mv_file))
    if np.sum(mv_file[np.where(mv_file>0)])<0.5*3000:
        #Very little going on in this file
        print vid_file
        return
    vid_name = os.path.split(vid_file)[-1].split('.')[0]
    vid_file = my_video_capture(vid_file, 30)
    left_arm_mvmt = np.sum(mv_file[:,(2,4,6)], axis=1)
    right_arm_mvmt = np.sum(mv_file[:,(1,3,5)], axis=1)
    head_mvmt = mv_file[:,0]
    train_dir = os.path.join(save_dir, "train")
    test_dir = os.path.join(save_dir, "test")

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    if not os.path.exists(os.path.join(train_dir, "l_arm_1")):
        os.makedirs(os.path.join(train_dir,"head_0"))
        os.makedirs(os.path.join(train_dir,"head_1"))
        os.makedirs(os.path.join(train_dir,"r_arm_0"))
        os.makedirs(os.path.join(train_dir,"r_arm_1"))
        os.makedirs(os.path.join(train_dir,"l_arm_0"))
        os.makedirs(os.path.join(train_dir,"l_arm_1"))
        os.makedirs(os.path.join(train_dir,"mv_1"))
        os.makedirs(os.path.join(train_dir,"mv_0"))

    if not os.path.exists(os.path.join(test_dir,"l_arm_1")):
        os.makedirs(os.path.join(test_dir,"head_0"))
        os.makedirs(os.path.join(test_dir,"head_1"))
        os.makedirs(os.path.join(test_dir,"r_arm_0"))
        os.makedirs(os.path.join(test_dir,"r_arm_1"))
        os.makedirs(os.path.join(test_dir,"l_arm_0"))
        os.makedirs(os.path.join(test_dir,"l_arm_1"))
        os.makedirs(os.path.join(test_dir,"mv_1"))
        os.makedirs(os.path.join(test_dir,"mv_0"))
    if np.random.randint(100) < 75:
        cur_dir = train_dir
    else:
        cur_dir = test_dir

    for f in range(offset+1,len(mv_file), 10):
        vid_file.forward_to(f - offset)
        img = vid_file.read()

        if np.mean(left_arm_mvmt[f:f+5]>5):
            #cv2.imwrite(os.path.join(cur_dir, "l_arm_1", "%s_%i.png" %(vid_name,f - offset)), img)
            cv2.imwrite(os.path.join(cur_dir, "mv_1", "%s_%i.png" % (vid_name, f - offset)), img)
        elif np.mean(right_arm_mvmt[f:f+5]>5):
            #cv2.imwrite(os.path.join(cur_dir, "r_arm_1", "%s_%i.png" % (vid_name, f - offset)), img)
            cv2.imwrite(os.path.join(cur_dir, "mv_1", "%s_%i.png" % (vid_name, f - offset)), img)
        elif np.mean(head_mvmt[f:f+5]>3):
            #cv2.imwrite(os.path.join(cur_dir, "head_1", "%s_%i.png" % (vid_name, f - offset)), img)
            cv2.imwrite(os.path.join(cur_dir, "mv_1", "%s_%i.png" % (vid_name, f - offset)), img)
    vid_file.rewind()
    for f in range(offset+1, len(mv_file), 60):
        vid_file.forward_to(f-offset)
        img = vid_file.read()
        flag = 0

        if np.all(left_arm_mvmt[f:f+5] >= 0) and np.mean(left_arm_mvmt[f:f + 5]) < 1:
            #cv2.imwrite(os.path.join(cur_dir, "l_arm_0", "%s_%i.png" % (vid_name, f - offset)), img)
            flag+=1
        if np.all(right_arm_mvmt[f:f + 5] >= 0) and np.mean(right_arm_mvmt[f:f + 5]) < 1:
            #cv2.imwrite(os.path.join(cur_dir, "r_arm_0", "%s_%i.png" % (vid_name, f - offset)), img)
            flag+=1
        if np.all(head_mvmt[f:f + 5] >= 0) and np.mean(head_mvmt[f:f + 5]) < 1:
            #cv2.imwrite(os.path.join(cur_dir, "head_0", "%s_%i.png" % (vid_name, f - offset)), img)
            flag+=1
        if flag==3:
            cv2.imwrite(os.path.join(cur_dir, "mv_0", "%s_%i.png" % (vid_name, f - offset)), img)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-v', '--vid_dir', required=True, help="video directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    parser.add_argument('-o', '--offset', default=15, type=int, help="how many frames into the future")
    args = parser.parse_args()

    for file in sorted(glob.glob(args.mv_dir + "/*.p")[64:]):
        #pdb.set_trace()
        sbj_id, day, vid_num, _ = os.path.split(file)[-1].split(".")[0].split("_")
        vid_name = os.path.join(args.vid_dir, "%s_%s_%s.avi" %( sbj_id, day, vid_num))
        main(file, vid_name, args.save_dir, args.offset)

