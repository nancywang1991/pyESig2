__author__ = 'wangnxr'

from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from sklearn.neighbors import kneighbors_graph
import matplotlib.pyplot as plt
import cPickle as pickle
import numpy as np
import time
import sys
from pyESig2.util.error import varError
import pdb

def find_data_ind(date, index):
    for d in xrange(index.shape[0]):
        name = index[d].split('/')[-1]
        vid, rest = name.split('_')
        num, _ = rest.split('.')
        if int(vid==date):
            return d

def split_cluster(cluster_data):
    estimator = KMeans(n_clusters=2)
    estimator.fit(cluster_data)
    return estimator.labels_

def temporal_consistency(ind):
    return np.std(ind)

def hier_cluster(data, ind, prev_stdev, result, level):
    consistency = temporal_consistency(ind)
    if not (data.shape[0] < 100 or consistency < prev_stdev or level > 9):
        labels=split_cluster(data)
        cluster0 = np.where(labels==0)[0]
        cluster0_ind = ind[np.where(labels==0)[0]]
        cluster1 = np.where(labels==1)[0]
        cluster1_ind = ind[np.where(labels==1)[0]]
        result[level, cluster0_ind] = 0
        result[level, cluster1_ind] = 1
        hier_cluster(cluster0, cluster0_ind, consistency, result, level + 1)
        hier_cluster(cluster1, cluster1_ind, consistency, result, level + 1)
def add_hier(cluster_result, level):
    for l in xrange(level):
        # Change cluster code using binary conversion at each level
        cluster_result[level] += (2**level)*cluster_result[l,:]

def condense_time(cluster_result, level):
    n_clusters = 2**level
    n_mins = cluster_result.shape[0]
    n_labels = np.zeros(shape=(n_mins,n_clusters))
    for h in xrange(n_mins):
        for n in xrange(n_clusters):
            n_labels[h,n] = np.where(cluster_result[h*60/2:(h+1)*60/2]==n)[0].shape[0]
    return n_labels

def main(sbj_id, dates, features_loc, save_loc):
    index = pickle.load(open(features_loc + "index_pca_"+ sbj_id + ".p", "rb"))
    raw_data = pickle.load(open(features_loc + "transformed_pca_" + sbj_id + ".p", "rb"))
    mean = np.mean(raw_data, axis=0)
    stdev = np.std(raw_data, axis=0)
    width = 1.0

    for d in dates:
        data = raw_data[find_data_ind(d, index)]
        cluster_result_temp = np.zeros(shape=(10, data.shape[0]))-1
        hier_cluster(data, range(data), float("inf"), cluster_result_temp, 0)
        cluster_result = np.zeros(shape=(10, data.shape[0]))
        for level in cluster_result_temp:
            cluster_result[level,:] = add_hier(cluster_result_temp, level)
        cluster_result[np.where(cluster_result_temp==-1)[0]]=-1
        # Plot Cluster Figures
        plt.figure(figsize=(20,10))
        plt.legend()
        plt.label("Time(Minute)")
        plt.ylabel("Count")
        for l in xrange(10):
            condensed = condense_time(cluster_result[level,:])
            for c in xrange(2**l):
                plt.plot(condensed[c])
        plt.show()
        pickle.dump(cluster_result, open(save_loc+ "/" + sbj_id + "_" + str(d) + ".p", "wb"))


if __name__ == "__main__":
    if not(len(sys.argv) == 4):
        raise varError("Arguments should be <Subject ID> <Dates> <Features directory>\
                          <Save directory>")
    main(*sys.argv[1:])

