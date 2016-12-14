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
        predicted[loc-10:loc+10] = 1
    true_correct = sum(np.logical_and(predicted,truth==1))
    true = sum(truth)
    detected = sum(predicted)

    precision = true_correct/float(detected)
    recall = true_correct/true

    return [precision, recall, true/30.0]

def main(mv_file, label_file, day, sbj_id, vid_num, writer):
    mv_file = pickle.load(open(mv_file))
    label_file = pickle.load(open(label_file))
    legit = np.where((mv_file<40) & (mv_file>0))[0]
    left_arm_mvmt = np.sum(mv_file[:,(2,4,6)], axis=1) > 1
    right_arm_mvmt = np.sum(mv_file[:,(1,3,5)], axis=1) > 1
    head_mvmt = mv_file[:,0] > 0.5
    truth_len = len(label_file["labels_array"][0])

    pred_len = len(head_mvmt)
    print sbj_id
    print vid_num
    pdb.set_trace()
    writer.writerow([sbj_id, day, vid_num, "Head"] + scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Head")][:pred_len][legit], mv_file[:truth_len, 0][legit]> 3))
    writer.writerow([sbj_id, day, vid_num, "Left wrist"] + scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Left.wrist")][:pred_len][legit], mv_file[:truth_len, 2][legit]> 3))
    writer.writerow([sbj_id, day, vid_num, "Right wrist"] + scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Right.wrist")][:pred_len][legit], mv_file[:truth_len, 1][legit]> 3))
    writer.writerow([sbj_id, day, vid_num, "Eligible", len(legit)/float(len(mv_file))])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-l', '--label_dir', required=True, help="Manual labels directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()
    write_file = open("%s\\accuracy_3.csv" % (args.save_dir), "wb")
    writer = csv.writer(write_file)
    writer.writerow(["sbj_id", "day", "vid_num", "Body part", "Precision", "Recall", "Movement_secs"])
    #pdb.set_trace()
    for file in glob.glob(args.mv_dir + "\\*.p"):
        sbj_id, day, vid_num, _ = file.split("\\")[-1].split(".")[0].split("_")
        label_file = "%s\\%s_%s_%s.p" % (args.label_dir, sbj_id, day, vid_num)

        if os.path.exists(label_file):
            main(file, label_file, day, sbj_id, vid_num, writer)

    write_file.close()
