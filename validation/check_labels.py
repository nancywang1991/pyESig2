__author__ = 'wangnxr'

import cPickle as pickle
import numpy as np
import sys
import glob
from pyESig2.util.error import varError
import pdb
import matplotlib.pyplot as plt
import random
import copy
from pyESig2.analysis import correlate_sections


def top_cluster_score(cluster_res, labels_ind):
    precision_mat = np.zeros(cluster_res.shape[0])
    recall_mat = np.zeros(cluster_res.shape[0])
    thresh = 1
    for l in xrange(cluster_res.shape[0]):
        total_found = np.where(cluster_res[l,:]>thresh)[0].shape[0]
        total_labels = np.where(labels_ind==1)[0].shape[0]
        if total_found>0 and total_labels>0:
            correct = np.where(labels_ind[np.where(cluster_res[l,:]>thresh)[0]]==1)[0].shape[0]
            recall_mat[l] = correct/float(total_labels)
            precision_mat[l] = correct/float(total_found)

    if (precision_mat+recall_mat).sum() > 0 :
        f1_mat = 2*np.divide(np.multiply(recall_mat,precision_mat),(precision_mat+recall_mat))
        f1_mat_loc = np.where(f1_mat==np.nanmax(f1_mat))[0][0]
    else:
        f1_mat=precision_mat
        f1_mat_loc = 0


    return (np.nanmax(recall_mat), np.where(recall_mat==np.nanmax(recall_mat))[0][0],
            np.nanmax(precision_mat), np.where(precision_mat==np.nanmax(precision_mat))[0][0],
            recall_mat[f1_mat_loc], precision_mat[f1_mat_loc],np.nanmax(f1_mat), f1_mat_loc)

def select_cluster_score(cluster_res, best_cluster, labels_ind,):
    thresh = 1
    total_found = np.where(cluster_res[best_cluster,:]>thresh)[0].shape[0]
    precision=0
    recall=0
    if total_found>0:
        correct = np.where(labels_ind[np.where(cluster_res[best_cluster,:]>thresh)[0]]==1)[0].shape[0]
        total_labels = np.where(labels_ind==1)[0].shape[0]
        recall = correct/float(total_labels)
        precision = correct/float(total_found)
    if (precision+recall)> 0:
        f1 = 2*recall*precision/(precision+recall)
    else:
        f1=precision


    return (recall, precision, f1)

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
def condense(labels, rate):
     new_labels = []
     for label in labels:
         num_mins=int(round(label.shape[1]/float(rate)))
         new_l = np.zeros(shape=(label.shape[0],num_mins))
         for t, track in enumerate(label):
             for i in xrange(num_mins):
                 if sum(track[i*int(rate):(i+1)*int(rate)])> (1*rate/4.0):
                     new_l[t,i] = 1
         new_labels.append(new_l)
     return new_labels

def label_accuracy(sbj_id, day, extracted_label_dir, extracted_random_label_dir,
                   condensed_cluster_file, time_correspondence_file, save_loc):
    all_labels = []
    all_cluster_results = []
    filetime = pickle.load(open(time_correspondence_file, "rb"))

    cluster_res = pickle.load(open(condensed_cluster_file, "rb"))

    for file in glob.glob(extracted_label_dir + "/" + sbj_id +"_" + str(day) + "*.p" ):
        filenum = extract_filenum(file)
        labels = pickle.load(open(file, "rb"))
        start = int(round((filetime["start"][filenum]-filetime["start"][0]).total_seconds()/15.0))
        dur = int(round(labels['labels_array'].shape[1]/15.0))
        cluster_res_section = cluster_res[start:start+dur,:]
        all_labels.append(labels['labels_array'])
        all_cluster_results.append(cluster_res_section.T)
    all_labels_random = copy.deepcopy(all_labels)
    final_labels = np.hstack(condense(all_labels, 15))
    final_labels_random = np.hstack(condense(all_labels_random, 15))
    random.shuffle(final_labels_random.T)

    final_cluster_results = np.hstack(all_cluster_results)
    save_file = open(save_loc + "\\" + sbj_id + "_" + str(day) + "_accuracy_results.txt", "wb")
    for t, track in enumerate(labels['tracks']):
        if final_labels[t,:].max()>0:
            (recall_score, recall_loc, precision_score, precision_loc, f1_recall, f1_precision, f1_max, f1_loc)\
                = top_cluster_score(final_cluster_results, final_labels[t,:])
            save_file.write(' '.join(["track:", track, "recall_score:" , str(recall_score), "recall_loc:" ,
                                str(recall_loc), "precision_score:", str(precision_score),
                                "precision_loc:", str(precision_loc), " f1_recall_score:",str(f1_recall),
                                " f1_precision_score:",str(f1_precision),
                                "f1_score:", str(f1_max),"f1_loc:", str(f1_loc) +"\n"]))
        else:
            save_file.write(' '.join(["track:", track, "No labels\n"]))

    save_file.write("---------------------------RANDOM------------------------------------------\n")
    for t, track in enumerate(labels['tracks']):
        if final_labels_random[t,:].max()>0:
            (recall_score, recall_loc, precision_score, precision_loc, f1_recall, f1_precision, f1_max, f1_loc)\
                = top_cluster_score(final_cluster_results, final_labels_random[t,:])
            save_file.write(' '.join(["track:", track, "recall_score:" , str(recall_score), "recall_loc:" ,
                                str(recall_loc), "precision_score:", str(precision_score),
                                "precision_loc:", str(precision_loc), " f1_recall_score:",str(f1_recall),
                                " f1_precision_score:",str(f1_precision),
                                "f1_score:", str(f1_max),"f1_loc:", str(f1_loc) +"\n"]))
        else:
            save_file.write(' '.join(["track:", track, "No labels\n"]))

    save_file.close()

def cluster_label_accuracy(sbj_id, day, best_corr_clusters, extracted_label_dir, extracted_random_label_dir,
                           condensed_cluster_file, time_correspondence_file, audio_file, mvmt_file, save_loc):
    all_labels = []
    all_cluster_results = []
    filetime = pickle.load(open(time_correspondence_file, "rb"))
    cluster_res = pickle.load(open(condensed_cluster_file, "rb"))
    audio_res=pickle.load(open(audio_file, "rb"))
    mvmt_res=pickle.load(open(mvmt_file, "rb"))
    sections=[]

    for file in glob.glob(extracted_label_dir + "/" + sbj_id +"_" + str(day) + "*.p" ):
        filenum = extract_filenum(file)
        labels = pickle.load(open(file, "rb"))
        start = int(round((filetime["start"][filenum]-filetime["start"][0]).total_seconds()/15.0))
        dur = int(round(labels['labels_array'].shape[1]/15.0))
        cluster_res_section = cluster_res[start:start+dur,:]
        sections.append((start,dur))
        all_labels.append(labels['labels_array'])
        all_cluster_results.append(cluster_res_section.T)
    best_corr_clusters=correlate_sections(audio_res,mvmt_res,cluster_res,sections)
    all_labels_random = copy.deepcopy(all_labels)

    final_labels = np.hstack(condense(all_labels, 15))
    final_labels_random = np.hstack(condense(all_labels_random, 15))
    random.shuffle(final_labels_random.T)
    final_cluster_results = np.hstack(all_cluster_results)

    save_file = open(save_loc + "/" + sbj_id + "_" + str(day) + "_accuracy_results_cluster.txt", "wb")
    for t, track in enumerate(labels['tracks']):
        if track in best_corr_clusters and final_labels[t,:].max()>0:
            (recall, precision, f1)\
                = select_cluster_score(final_cluster_results, best_corr_clusters[track], final_labels[t,:])
            save_file.write(' '.join(["track:", track, "recall_score:" ,
                                      str(recall), "precision_score:", str(precision),
                                " f1_score:",str(f1),"loc:", str(best_corr_clusters[track]) +"\n"]))
        else:
            save_file.write(' '.join(["track:", track, "No labels\n"]))
    save_file.write("---------------------------RANDOM------------------------------------------\n")
    for t, track in enumerate(labels['tracks']):
        if track in best_corr_clusters and final_labels_random[t,:].max()>0:
            (recall, precision, f1)\
                = select_cluster_score(final_cluster_results, best_corr_clusters[track], final_labels_random[t,:])
            save_file.write(' '.join(["track:", track, "recall_score:" ,
                                      str(recall), "precision_score:", str(precision),
                                " f1_score:",str(f1),"loc:", str(best_corr_clusters[track]) +"\n"]))
        else:
            save_file.write(' '.join(["track:", track, "No labels\n"]))

    save_file.close()

def delete_co_occurence(labels_raw):
    labels_final = np.zeros(shape=labels_raw.shape)
    for t in xrange(labels_raw.shape[0]):
        labels_final[t,:] = labels_raw[t,:]
        for t2 in np.delete(np.arange(labels_raw.shape[0]), [t, 9]):
            labels_final[t,:] *=(1-labels_raw[t2,:])
    return labels_final
def label_histogram(sbj_id, day, extracted_label_dir, cluster_file, time_correspondence_file, save_loc):
    all_labels = []
    all_cluster_results = []
    filetime = pickle.load(open(time_correspondence_file, "rb"))
    cluster_res = pickle.load(open(cluster_file, "rb"))[4,:]

    for file in glob.glob(extracted_label_dir + "\\" + sbj_id +"_" + str(day) + "*.p" ):
        filenum = extract_filenum(file)
        labels = pickle.load(open(file, "rb"))
        start = int(round((filetime["start"][filenum]-filetime["start"][0]).total_seconds()/2.0))
        dur = int(round(labels['labels_array'].shape[1]/2.0))
        cluster_res_section = cluster_res[start:start+dur]
        all_labels.append(labels['labels_array'])
        all_cluster_results.append(cluster_res_section)

    final_labels_raw = np.hstack(condense(all_labels, 2))
    final_labels = delete_co_occurence(final_labels_raw)
    #final_labels = final_labels_raw

    final_cluster_results = np.hstack(all_cluster_results)
    histograms = []
    for c in xrange(int(cluster_res.max())):
        histogram_vals = np.zeros(len(labels['tracks']))
        bar_width = 0.35
        index = np.arange(len(labels['tracks']))
        for t, track in enumerate(labels['tracks']):
            num_found_labels = np.where(final_labels[t,np.where(final_cluster_results==c)[0]]==1)[0].shape[0]
            total_labels = float(np.where(final_labels[t,:]==1)[0].shape[0])
            if total_labels>0:
                histogram_vals[t] = num_found_labels/total_labels
        histograms.append(histogram_vals)
    ind = (np.max(np.array(histograms), axis=1)-np.mean(np.array(histograms), axis=1)).argsort()
    f, axarr = plt.subplots(5, sharex=True, sharey=True)

    for i in xrange(5):
        axarr[i].bar(index,histograms[ind[-(i+1)]])
        axarr[i].set_title("Distribution of labels for cluster " + str(ind[-(i+1)]))
        axarr[i].set_ylim([0,1])
        #axarr[i].set_ylabel("% of total labels")
    axarr[i].set_xticks(index + bar_width)
    axarr[i].set_xticklabels(labels['pretty_tracks'], rotation=30)
    plt.tight_layout()
    plt.savefig(save_loc + "\\" + sbj_id + "_" + str(day) + "_hist.png")

def label_histogram_condensed(sbj_id, day, extracted_label_dir, cluster_file, condensed_cluster_file, time_correspondence_file, save_loc):
    all_labels = []
    all_cluster_results = []
    filetime = pickle.load(open(time_correspondence_file, "rb"))
    cluster_res = pickle.load(open(condensed_cluster_file, "rb"))

    for file in glob.glob(extracted_label_dir + "/" + sbj_id +"_" + str(day) + "*.p" ):
        filenum = extract_filenum(file)
        labels = pickle.load(open(file, "rb"))
        start = int(round((filetime["start"][filenum]-filetime["start"][0]).total_seconds()/15.0))
        dur = int(round(labels['labels_array'].shape[1]/15.0))
        cluster_res_section = cluster_res[start:start+dur,:]
        all_labels.append(labels['labels_array'])
        all_cluster_results.append(cluster_res_section.T)
    final_labels = np.hstack(condense(all_labels, 15))
    raw_cluster_results = np.hstack(all_cluster_results)
    final_cluster_results = np.zeros(shape=raw_cluster_results.shape)
    for t in xrange(raw_cluster_results.shape[1]):
        final_cluster_results[np.where(raw_cluster_results[:,t]==raw_cluster_results[:,t].max())[0], t]=1

    histograms = []
    for c in xrange(cluster_res.shape[1]):
        histogram_vals = np.zeros(len(labels['tracks']))
        bar_width = 0.35
        index = np.arange(len(labels['tracks']))
        for t, track in enumerate(labels['tracks']):
            num_found_labels = np.where(final_labels[t,np.where(final_cluster_results[c,:]==1)[0]]==1)[0].shape[0]
            total_labels = float(np.where(final_labels[t,:]==1)[0].shape[0])
            if total_labels>0:
                histogram_vals[t] = num_found_labels/total_labels
        histograms.append(histogram_vals)
    ind = (np.max(np.array(histograms), axis=1)-np.mean(np.array(histograms), axis=1)).argsort()
    f, axarr = plt.subplots(5, sharex=True, sharey=True)

    for i in xrange(5):
        axarr[i].bar(index,histograms[ind[-(i+1)]])
        axarr[i].set_title("Distribution of labels for cluster " + str(ind[-(i+1)]))
        axarr[i].set_ylim([0,1])
        #axarr[i].set_ylabel("% of total labels")
    axarr[i].set_xticks(index + bar_width)
    axarr[i].set_xticklabels(labels['pretty_tracks'], rotation=30)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if not(len(sys.argv) == 8):
        print len(sys.argv)
        raise varError("Arguments should be <Subject ID> <Day><Extracted Label Directory>\
                         <Cluster result file><Condensed Cluster result file><File time correspondence file> <Save directory>")
    label_accuracy(*sys.argv[1:])
    label_histogram(*sys.argv[1:])
    label_histogram_condensed(*sys.argv[1:])