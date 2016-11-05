import argparse
import glob
import cPickle as pickle
import csv
import numpy as np
import os
import pdb
import matplotlib.pyplot as plt

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

def main(mv_file, label_file, day, sbj_id, vid_num, writer):
    mv_file = pickle.load(open(mv_file))
    label_file = pickle.load(open(label_file))

    left_arm_mvmt = np.sum(mv_file[:,(2,4,6)], axis=1) > 1
    right_arm_mvmt = np.sum(mv_file[:,(1,3,5)], axis=1) > 1
    head_mvmt = mv_file[:,0] > 0.5
    truth_len = len(label_file["labels_array"][0])
    pred_len = len(head_mvmt)
    writer.writerow([sbj_id, day, vid_num, "Head"] + scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Head_mv")][:pred_len], head_mvmt[:truth_len]))
    writer.writerow([sbj_id, day, vid_num, "Left arm"] + scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Arm_mv_left")][:pred_len], left_arm_mvmt[:truth_len]))
    writer.writerow([sbj_id, day, vid_num, "Right arm"] + scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Arm_mv_right")][:pred_len], right_arm_mvmt[:truth_len]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-l', '--label_dir', required=True, help="Manual labels directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()
    write_file = open("%s\\accuracy_2.csv" % (args.save_dir), "wb")
    writer = csv.writer(write_file)
    writer.writerow(["sbj_id", "day", "vid_num", "Body part", "Precision", "Recall", "Movement_secs"])
    for file in glob.glob(args.mv_dir + "/*.p"):
        sbj_id, day, vid_num, _ = file.split("\\")[-1].split(".")[0].split("_")
        label_file = "%s\\%s_%s_%s.p" % (args.label_dir, sbj_id, day, vid_num)

        if os.path.exists(label_file):
            main(file, label_file, day, sbj_id, vid_num, writer)

    write_file.close()
