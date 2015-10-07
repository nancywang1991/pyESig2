__author__ = 'wangnxr'

import cPickle as pickle
import numpy as np
import sys
import glob
from pyESig2.util.error import varError
import pdb

def top_cluster_score(cluster_res, labels_ind):
    precision_mat = np.zeros(10)
    recall_mat = np.zeros(10)
    avg_mat = np.zeros(10)
    thresh = 5
    for l in xrange(10):
        total_found = np.where(cluster_res[l,:]>thresh)[0].shape[0]
        if total_found>0:
            correct = np.where(labels_ind[np.where(cluster_res[l,:]>thresh)[0]]==1)[0].shape[0]

            total_labels = np.where(labels_ind==1)[0].shape[0]
            recall_mat[l] = correct/float(total_labels)
            precision_mat[l] = correct/float(total_found)
    avg_mat = np.mean([recall_mat, precision_mat], axis=0)

    return (recall_mat.max(), np.where(recall_mat==recall_mat.max())[0][0],
            precision_mat.max(), np.where(precision_mat==precision_mat.max())[0][0],
            avg_mat.max(), np.where(avg_mat==avg_mat.max())[0][0])

def repeat1(cluster_res):
    n_data=cluster_res.shape[1]
    levels=10
    new_cluster_res=np.zeros(shape=(levels, n_data))
    for l in xrange(levels):
        for c in xrange(n_data):
            new_cluster_res[l,2*c:2*(c+1)]=cluster_res[l,c]
    return new_cluster_res

def extract_filenum(filename):
     name = filename.split('\\')[-1]
     id, day, rest = name.split('_')
     filenum,_ = rest.split('.')
     return int(filenum)
def condense(labels):
     new_labels = []
     for label in labels:
         num_mins=int(np.round(label.shape[1]/60.0))
         new_l = np.zeros(shape=(label.shape[0],num_mins))
         for t, track in enumerate(label):
             for i in xrange(num_mins):
                 if sum(track[i*60:(i+1)*60])>0:
                     new_l[t,i] = 1
         new_labels.append(new_l)
     return new_labels

def main(sbj_id, day, extracted_label_dir, cluster_file, time_correspondence_file, save_loc):
    all_labels = []
    all_cluster_results = []
    filetime = pickle.load(open(time_correspondence_file, "rb"))
    cluster_res = pickle.load(open(cluster_file, "rb"))[:,:10]

    for file in glob.glob(extracted_label_dir + "/" + sbj_id +"_" + day + "*.p" ):
        filenum = extract_filenum(file)
        labels = pickle.load(open(file, "rb"))
        start = int(round((filetime["start"][filenum]-filetime["start"][0]).total_seconds()/60.0))
        dur = int(round(labels['labels_array'].shape[1]/60.0))
        cluster_res_section = cluster_res[start:start+dur,:]
        all_labels.append(labels['labels_array'])
        all_cluster_results.append(cluster_res_section.T)
    final_labels = np.hstack(condense(all_labels))
    final_cluster_results = np.hstack(all_cluster_results)
    save_file = open(save_loc + "/" + sbj_id + "_" + day + "_accuracy_results.txt", "wb")
    for t, track in enumerate(labels['tracks']):
        if final_labels[t,:].max()>0:
            (recall_score, recall_loc, precision_score, precision_loc, avg_score, avg_loc)\
                = top_cluster_score(final_cluster_results, final_labels[t,:])
            save_file.write(' '.join(["track:", track, "recall_score:" , str(recall_score), "recall_loc:" ,
                                str(recall_loc), "precision_score:", str(precision_score),
                                "precision_loc:", str(precision_loc), " avg_score:",str(avg_score),
                                "avg_loc:", str(avg_loc) +"\n"]))
        else:
            save_file.write(' '.join(["track:", track, "No labels\n"]))

    save_file.close()

if __name__ == "__main__":
    if not(len(sys.argv) == 7):
        print len(sys.argv)
        raise varError("Arguments should be <Subject ID> <Day><Extracted Label Directory>\
                         <Cluster result file><File time correspondence file> <Save directory>")
    main(*sys.argv[1:])