from pyESig2.annotation.extract_labels import extract_labeller_reduced_labels
import cPickle as pickle
import glob
import os
import numpy as np
import pdb


labellers = ["rs", "sk"]

sbj_id_all = ["d6532718", "cb46fd46","e70923c4", "fcb01f7a", "a86a4375", "c95c1e82" ]
dates_all = [[4,5,6,7],[7,8,9,10],[4,5,6,7],[8,9,10,11,12,16], [4,5,6,7], [4,5,6,7]]

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
        consistency_file=[]
        extract_labeller_reduced_labels(sbj_id, date, label_loc, video_loc, extracted_label_loc, labellers[0])
        extract_labeller_reduced_labels(sbj_id, date, label_loc, video_loc, extracted_label_loc, labellers[1])
        for file in glob.glob(extracted_label_loc + "\\" + sbj_id + "_" + str(date) + "_*_" + labellers[0] + ".p"):
            filename = file.split("\\")[-1]
            name, ext = file.split(".")
            filenum = file.split("_")[-2]
            file_alt = (extracted_label_loc + "\\" + sbj_id + "_"
                                      + str(date) + "_" + filenum + "_" + labellers[1] + ".p")
            if os.path.exists(file_alt):
                labels1 = pickle.load(open(file, "rb"))
                labels2 = pickle.load(open(file_alt, "rb"))
                accuracy_mat = np.zeros(len(labels1["labels_array"]))
                for l in xrange(len(labels1["labels_array"])):
                    correct = np.where(labels1["labels_array"][l]==labels2["labels_array"][l])[0].shape[0]

                    accuracy_mat[l] = correct/float(len(labels1["labels_array"][l]))
                consistency_file.append({"filenum":filenum, "accuracy": accuracy_mat})
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
            for accu in file["accuracy"]:
                all_accu.append(np.mean(accu))
                sbj_accu.append(np.mean(accu))
                file_accu.append(np.mean(accu))
                date_accu.append(np.mean(accu))
            print np.mean(file_accu)
        print np.mean(date_accu)
    print np.mean(sbj_accu)

print "Overall consistency" + str(np.mean(all_accu))

pickle.dump(consistency_all, open(label_consistency_loc + "labeller_consistency.p", "wb"))


