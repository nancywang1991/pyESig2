__author__ = 'wangnxr'

import cPickle as pickle
import numpy as np
import sys
import glob
from pyESig2.util.error import varError

def top_cluster_score(cluster_res, labels_ind):
    precision_mat = np.zeros(10, 2**10)
    recall_mat = np.zeros(10, 2**10)
    for l in xrange(10):
        for c in xrange(2**l):
            correct = (labels_ind[np.where(cluster_res[l,:]==c)[0]]==1).shape[0]
            total_labels = np.where(labels_ind==1)[0].shape[0]
            total_found = np.where(cluster_res[l,:]==c)[0].shape[0]
            recall_mat[l,c] = correct/total_labels
            precision_mat[l,c] = correct/total_found
    return (recall_mat.max(), np.where(recall_mat==recall_mat.max())[0][0],
            precision_mat.max(), np.where(precision_mat==precision_mat.max())[0][0])

def repeat1(cluster_res):
    n_data=cluster_res.shape[1]
    levels=10
    new_cluster_res=np.zeros(shape=(levels, n_data))
    for l in xrange(levels):
        for c in xrange(n_data):
            new_cluster_res[l,2*c:2*(c+1)]=cluster_res[l,c]
    return new_cluster_res

def extract_filenum(filename):
     name = filename.split('/')[-1]
     id, rest = name.split('_')
     day,rest = rest.split('_')
     filenum,_ = rest.split('.')
     return int(filenum)

def main(sbj_id, day, extracted_label_dir, cluster_file, time_correspondence_file, save_loc):
    all_labels = []
    all_cluster_results = []
    filetime = pickle.load(open(time_correspondence_file, "rb"))
    cluster_res = repeat1(pickle.load(open(cluster_file, "rb")))
    for file in glob.glob(extracted_label_dir + "/" + sbj_id +"_" + day + "*.p" ):
        filenum = extract_filenum(file)
        labels = pickle.load(open(file, "rb"))
        cluster_res_section = cluster_res[:,filetime["start"][filenum]:filetime["end"][filenum]]
        all_labels.append(labels['labels_array'])
        all_cluster_results.append(cluster_res_section)
    final_labels = np.hstack(all_labels)
    final_cluster_results = np.hstack(all_cluster_results)
    save_file = open(save_loc + "/" + sbj_id + "_" + day + "_accuracy_results.txt", "wb")
    for t, track in enumerate(labels['tracks']):
        (recall_score, recall_loc, precision_score, precision_loc)\
            = top_cluster_score(final_cluster_results, final_labels[t,:])
        save_file.writerow(["track: ", track, "recall_score: " , recall_score, "recall_loc: " ,
                            recall_loc, "precision_score: ", precision_score,
                            "precision_loc: ", precision_loc])
    save_file.close()

if __name__ == "__main__":
    if not(len(sys.argv) == 6):
        raise varError("Arguments should be <Subject ID> <Day><Extracted Label Directory>\
                         <Cluster result file><File time correspondence file> <Save directory>")
    main(*sys.argv[1:])