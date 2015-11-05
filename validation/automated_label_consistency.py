from pyESig2.annotation.extract_labels import extract_labeller_reduced_labels
import cPickle as pickle
import glob
import os
import numpy as np
import pdb

sbj_id_all = ["d6532718", "cb46fd46","e70923c4", "fcb01f7a", "a86a4375", "c95c1e82" ]
dates_all = [[4,5,6,7],[7,8,9,10],[4,5,6,7],[8,9,10,11,12,16], [4,5,6,7], [4,5,6,7]]
#sbj_id_all = [ "cb46fd46"]
#dates_all = [[10]]
#threshold = 3.3*10**11
threshold = 1.2
type = 'Mvmt'
sr = 30
consistency_all = []

for s, sbj_id in enumerate(sbj_id_all):
    consistency_date=[]
    dates=dates_all[s]
    video_loc="D:\\NancyStudyData\\ecog\\raw\\" + sbj_id + "\\"
    label_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\manual_annotations\\tracks\\"
    #Save_locations
    extracted_label_loc="C:\\Users\\wangnxr\Documents\\rao_lab\\video_analysis\\manual_annotations\\extracted_labels_reduced\\"
    label_accuracy_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\validation\\" + sbj_id + "\\"

    label_consistency_loc="C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\validation\\"

    for date in dates:
        #automated_label_loc="E:\\sound\\" + sbj_id + "\\" + str(date) + "\\"
        automated_label_loc="E:\\mvmt\\" + sbj_id + "\\"
        consistency_file=[]
        extract_labeller_reduced_labels(sbj_id, date, label_loc, video_loc, extracted_label_loc, 'rs')
        for file in glob.glob(extracted_label_loc + "\\" + sbj_id + "_" + str(date) + "_*_" + 'rs' + ".p"):
            filename = file.split("\\")[-1]
            name, ext = file.split(".")
            filenum = file.split("_")[-2]
            if os.path.isfile(automated_label_loc + sbj_id + "_" + str(date) + "_" + filenum + ".p"):
                auto_label_temp = pickle.load(open(automated_label_loc + sbj_id + "_" + str(date) + "_" + filenum + ".p", "rb"))
                labels1 = pickle.load(open(file, "rb"))
                l = labels1["tracks"].index(type)
                o = labels1["tracks"].index("Other")
                auto_label = np.zeros(len(labels1["labels_array"][l]))
                for i in xrange(len(auto_label)):
                    if np.where(auto_label_temp[i*sr:(i+1)*sr] > threshold)[0].shape[0] > 5:
                        auto_label[i]=1

                include = np.where(labels1["labels_array"][o]>=0)[0]
                correct = np.where(labels1["labels_array"][l][include]==auto_label[include])[0].shape[0]
                #pdb.set_trace()
                if len(labels1["labels_array"][l][include]) > 0 :
                    accuracy = correct/float(len(labels1["labels_array"][l][include]))
                    consistency_file.append({"filenum":filenum, "accuracy": accuracy})
        consistency_date.append({"date":date, "file_accu": consistency_file})
    consistency_all.append({"sbj_id":sbj_id, "date_accu": consistency_date})

# Summary stats
all_accu = []

for sbj in consistency_all:
    print "Subject: " + sbj["sbj_id"]
    sbj_accu = []
    for date in sbj["date_accu"]:
        print "date: " + str(date["date"])
        date_accu = []
        for file in date["file_accu"]:
            print "file: " + str(file["filenum"])
            file_accu = []
            all_accu.append(file["accuracy"])
            sbj_accu.append(file["accuracy"])
            file_accu.append(file["accuracy"])
            date_accu.append(file["accuracy"])
            #print np.mean(file_accu)
        #print np.mean(date_accu)
    print np.mean(sbj_accu)

print "Overall consistency" + str(np.mean(all_accu))

pickle.dump(consistency_all, open(label_consistency_loc + "auto_label_consistency_" + type +  ".p", "wb"))

