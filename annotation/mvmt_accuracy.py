import pandas
import pdb
import numpy as np
import datetime
import glob
import cPickle as pickle

annotation_file1 = "C:\\Users\\Nancy\\OneDrive\\Documents\\Documents\\brunton_lab\\AAAI2018\\mvmt_label_maya.xlsx"
annotation_file2 = "C:\\Users\\Nancy\\OneDrive\\Documents\\Documents\\brunton_lab\\AAAI2018\\mvmt_label_nancy.xlsx"
mvmt_dir = "C:\\Users\\Nancy\\Downloads\\mvmt"

def detect_mvmt(mv_file, arm):
    mv_file = pickle.load(open(mv_file))
    left_arm_mvmt = mv_file[:,2]
    right_arm_mvmt = mv_file[:,1]
    head_mvmt = mv_file[:,0]
    final_mvmt = []
    final_rest = []
    for f in range(0,min(len(mv_file), 30*119), 2):
        if arm == "left" and np.mean(left_arm_mvmt[f:f+5])>1 and np.all(left_arm_mvmt[f-10:f] >= 0) and np.mean(left_arm_mvmt[f-10:f]) < 0.5:
                final_mvmt.append(int(round(f/3.0)))
        if arm == "right" and np.mean(right_arm_mvmt[f:f+5])>1 and np.all(right_arm_mvmt[f-10:f] >= 0) and np.mean(right_arm_mvmt[f-10:f]) < 0.5:
                final_mvmt.append(int(round(f/3.0)))

        if (f) % 10 == 0:
            flag = 0
            if np.all(left_arm_mvmt[f - 30:f + 30] >= 0) and np.mean(left_arm_mvmt[f - 30:f + 30]) < 0.5:
                flag += 1
            if np.all(right_arm_mvmt[f - 30:f + 30] >= 0) and np.mean(right_arm_mvmt[f - 30:f + 30]) < 0.5:
                flag += 1
            if np.all(head_mvmt[f - 30:f + 30] >= 0) and np.mean(head_mvmt[f - 30:f + 30]) < 0.5:
                flag += 1
            if flag==3:
                final_rest.append(int(round(f/3.0)))
    return final_mvmt, final_rest


def time_conversion(time):
    if not isinstance(time, datetime.time):
        if isinstance(time, float):
            return int(round(time*10))
        else:
            return time*10
    else:
        return int(round(time.minute*600 + time.second*10+time.microsecond/100000))

## Interrater agreement
arm = ["right", "left", "right", "right"]
for sheet in xrange(4):
    rest_accuracy = []
    rest_count = []
    mvmt_accuracy = []
    mvmt_count = []
    annot1 = pandas.read_excel(annotation_file1, sheetname=sheet, header=None)
    annot2 = pandas.read_excel(annotation_file2, sheetname=sheet, header=None)
    annot1_time = np.zeros(shape=(27, 1200))
    annot2_time = np.zeros(shape=(27, 1200))
    for r in range(1,len(annot1),3):
        c=1

        while not (c >= annot1.shape[1] or pandas.isnull(annot1.iloc[r].iloc[c])):
            start = annot1.iloc[r].iloc[c]
            end = annot1.iloc[r+1].iloc[c]
            annot1_time[(r-1)/3,time_conversion(start): time_conversion(end)]=1
            c+=1


    for r in range(1,len(annot2),3):
        c=1
        try:
            mvmt_file = glob.glob("%s/%s_movement.p" % (mvmt_dir, annot1.iloc[r-1].iloc[0].split(".")[0]))[0]
            mvmt, rest = detect_mvmt(mvmt_file, arm[sheet])
        except:
            mvmt = []
            rest = []
        while not (c >= annot2.shape[1] or pandas.isnull(annot2.iloc[r].iloc[c])):
            start = annot2.iloc[r].iloc[c]
            end = annot2.iloc[r+1].iloc[c]
            annot2_time[(r-1)/3,time_conversion(start): time_conversion(end)]=1
            c+=1
        if len(rest)>0:
            rest_accuracy.append(len(rest)-sum(annot1_time[(r-1)/3, rest]))
            rest_count.append(len(rest))
        if len(mvmt) > 0:
            #if sheet==2:
            #    pdb.set_trace()
            mvmt_accuracy.append(sum(annot1_time[(r-1)/3, mvmt]))
            mvmt_count.append(len(mvmt))
    agreement = []
    agreement_1_v1 = []
    count_1_v1 = []
    agreement_1_v2 = []
    count_1_v2 = []
    for l in xrange(len(annot1_time)):
        if sum(annot1_time[l]) > 0:
            agreement.append(len(np.where(annot1_time[l] == annot2_time[l])[0])/1200.0)
        if sum(annot1_time[l])>0:
            agreement_1_v1.append(sum(annot1_time[l]*annot2_time[l]))
            count_1_v1.append(sum(annot1_time[l]))
        if sum(annot2_time[l])>0:
            agreement_1_v2.append(sum(annot1_time[l]*annot2_time[l]))
            count_1_v2.append(sum(annot2_time[l]))
    #pdb.set_trace()
    print np.mean(agreement)
    #print np.mean([np.sum(agreement_1_v1)/float(np.sum(count_1_v1)), np.sum(agreement_1_v2) / float(np.sum(count_1_v2))])

    print np.mean([np.sum(rest_accuracy)/float(np.sum(rest_count)), np.sum(mvmt_accuracy)/float(np.sum(mvmt_count))])
    #print np.sum(mvmt_accuracy)/float(np.sum(mvmt_count))


