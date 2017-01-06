import argparse
import glob
import cPickle as pickle
import csv
import numpy as np
import os
import pdb
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def detect_breaks(legit):
    breaks = [-1]
    for i, ind in enumerate(legit[1:]):
        if ind-legit[i]>1:
            breaks.append(i)
    breaks.append(len(legit))
    return breaks

def scoring(truth, predicted_in, legit):
    breaks = detect_breaks(legit)
    for i, ind in enumerate(breaks[:-1]):
        if len(predicted_in[breaks[i]+1:breaks[i+1]])> 50:
            predicted_in[breaks[i]+1:breaks[i+1]] = savgol_filter(predicted_in[breaks[i]+1:breaks[i+1]], 31, 2)
        elif len(predicted_in[breaks[i]+1:breaks[i+1]])> 10:
            predicted_in[breaks[i]+1:breaks[i+1]] = savgol_filter(predicted_in[breaks[i]+1:breaks[i+1]], 5, 2)
    # plt.plot(legit/30.0, truth*15, label="truth")
    # plt.plot(legit/30.0, predicted_in, label="predicted")
    # plt.plot(legit/30.0, np.zeros(len(legit))+0.75)
    # plt.ylim([0,20])
    # plt.legend()
    # plt.show()

    pred_locs = np.where(predicted_in>0.75)[0]
    predicted = np.zeros(len(predicted_in))
    predicted[pred_locs] = 1
    for loc in pred_locs:
        predicted[loc-15:loc+15] = 1
    true_correct = sum(np.logical_and(predicted,truth==1))
    true = sum(truth)
    detected = sum(predicted)
    if detected==0:
        precision = np.NAN
    else:
        precision = true_correct/float(detected)
    if true == 0:
        recall = np.NAN
    else:
        recall = true_correct/true

    return np.array([precision, recall, true/30.0])

def main(mv_file, label_file, day, sbj_id, vid_num, writer):
    mv_file = pickle.load(open(mv_file))
    label_file = pickle.load(open(label_file))
    truth_len = len(label_file["labels_array"][0])
    legit = [np.where((mv_file[:truth_len,0]<40) & (mv_file[:truth_len,0]>=0))[0],
             np.where((mv_file[:truth_len,1]<40) & (mv_file[:truth_len,1]>=0))[0],
             np.where((mv_file[:truth_len,2]<40) & (mv_file[:truth_len,2]>=0))[0]]
    left_arm_mvmt = np.sum(mv_file[:,(2,4,6)], axis=1) > 1
    right_arm_mvmt = np.sum(mv_file[:,(1,3,5)], axis=1) > 1
    head_mvmt = mv_file[:,0] > 0.5


    pred_len = len(head_mvmt)
    print sbj_id
    print vid_num
    #pdb.set_trace()
    head_score = scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Head")][:pred_len][legit[0]],
            mv_file[:truth_len, 0][legit[0]], legit[0])
    wrist_l_score = scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Left.wrist")][:pred_len][legit[2]], mv_file[:truth_len, 2][legit[2]], legit[2])
    wrist_r_score = scoring(label_file["labels_array"][label_file["pretty_tracks"].index("Right.wrist")][:pred_len][legit[1]], mv_file[:truth_len, 1][legit[1]], legit[1])
    writer.writerow([sbj_id, day, vid_num, "Head", len(legit[0])/float(len(mv_file))] + list(head_score))
    writer.writerow([sbj_id, day, vid_num, "Left wrist", len(legit[2])/float(len(mv_file))] + list(wrist_l_score))
    writer.writerow([sbj_id, day, vid_num, "Right wrist",len(legit[1])/float(len(mv_file))] + list(wrist_r_score))

    return np.vstack([head_score, wrist_l_score, wrist_r_score])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mv_dir', required=True, help="Joint movement directory")
    parser.add_argument('-l', '--label_dir', required=True, help="Manual labels directory")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    args = parser.parse_args()
    write_file = open("%s\\accuracy_5.csv" % (args.save_dir), "wb")
    writer = csv.writer(write_file)
    writer.writerow(["sbj_id", "day", "vid_num", "Body part", "Eligible","Precision", "Recall", "Movement_secs"])
    scores = []
    #pdb.set_trace()
    for file in glob.glob(args.mv_dir + "\\*.p"):
        sbj_id, day, vid_num, _ = file.split("\\")[-1].split(".")[0].split("_")
        label_file = "%s\\%s_%s_%s.p" % (args.label_dir, sbj_id, day, vid_num)

        if os.path.exists(label_file):
            score = main(file, label_file, day, sbj_id, vid_num, writer)
            scores.append(score)

    scores = np.array(scores)

    writer.writerow(["weighted_head_recall", np.nansum(scores[:,0,1]*scores[:,0,2])/(np.sum(scores[:,0,2])-np.sum(scores[np.where(np.isnan(scores[:,0,1]))[0],0,2])),
                     "weighted_head_precision", np.nansum(scores[:,0,0]*scores[:,0,2])/(np.sum(scores[:,0,2])-np.sum(scores[np.where(np.isnan(scores[:,0,0]))[0],0,2]))])
    writer.writerow(["weighted_left_wrist_recall", np.nansum(scores[:, 2, 1] * scores[:, 2, 2]) / (np.sum(scores[:, 2, 2]-np.sum(scores[np.where(np.isnan(scores[:,2,1]))[0],2,2]))),
                     "weighted_left_wrist_precision", np.nansum(scores[:, 2, 0] * scores[:, 2, 2]) / (np.sum(scores[:, 2, 2])-np.sum(scores[np.where(np.isnan(scores[:,2,0]))[0],2,2]))])
    writer.writerow(["weighted_right_wrist_recall", np.nansum(scores[:, 1, 1] * scores[:, 1, 2]) / (np.sum(scores[:, 1, 2])-np.sum(scores[np.where(np.isnan(scores[:,1,1]))[0],1,2])),
                     "weighted_right_wrist_precision", np.nansum(scores[:, 1, 0] * scores[:, 1, 2]) / (np.sum(scores[:, 1, 2])-np.sum(scores[np.where(np.isnan(scores[:,1,0]))[0],1,2]))])
    write_file.close()
