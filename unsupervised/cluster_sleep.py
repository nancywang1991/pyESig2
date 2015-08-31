from sklearn.cluster import KMeans, AffinityPropagation
import matplotlib.pyplot as plt
import cPickle as pickle
import numpy as np
import pdb

features_loc = ("C:\\Users\\wangnxr\\Documents\\" +
                "rao_lab\\video_analysis\\features\\")
sbj_id = "e1556efa"
day = 2

data = pickle.load(open(features_loc + sbj_id + "_" + str(day) + ".p", "rb"))
mean = np.mean(data, axis=0)
stdev = np.std(data, axis=0)
num_clusters = 5
width = 1.0
start_min = 1000
##-----------------------------Script----------------------------

# K-means
##for d in xrange(data.shape[0]):
##    for e in xrange(data.shape[1]):
##        if (data[d,e] > mean[e] + stdev[e]/20
##            or data[d,e] < mean[e] - 1*stdev[e]/20):
##            data[d,e] = mean[e]
##estimator = KMeans(n_clusters=num_clusters)
##
##estimator.fit(data[:,:])
##labels = estimator.labels_
##num_labels = np.zeros(shape=(data.shape[0]/(60*60/3), num_clusters))
##for h in xrange(data.shape[0]/(60*60/3)):
##    for n in xrange(num_clusters):
##        num_labels[h,n] = np.where(estimator.labels_[h*60*60/3:(h+1)*60*60/3] == n)[0].shape[0]
##for n in xrange(num_clusters):
##    plt.plot(num_labels[:,n])
####plt.bar(range(num_labels.shape[0]-start_min),num_labels[start_min:,0], width,
####        color='r', edgecolor="none")
####plt.bar(range(num_labels.shape[0]-start_min),num_labels[start_min:,1], width,
####        bottom=num_labels[start_min:,0], color='y', edgecolor="none")
####plt.bar(range(num_labels.shape[0]-start_min),num_labels[start_min:,2], width,
####        bottom=num_labels[start_min:,1], color='b', edgecolor="none")
####plt.bar(range(num_labels.shape[0]-start_min),num_labels[start_min:,3], width,
####        bottom=num_labels[start_min:,2], color='g', edgecolor="none")
####plt.bar(range(num_labels.shape[0]-start_min),num_labels[start_min:,4], width,
####        bottom=num_labels[start_min:,3], color='r', edgecolor="none")
##plt.xlabel("minute")
##plt.ylabel("Count")
##plt.show()


# Affinity Propagation

for d in xrange(data.shape[0]):
    for e in xrange(data.shape[1]):
        if (data[d,e] > mean[e] + stdev[e]/20
            or data[d,e] < mean[e] - 1*stdev[e]/20):
            data[d,e] = mean[e]
estimator = AffinityPropagation(preference = -5e+19)

estimator.fit(data[::10,:])
labels = estimator.labels_
pdb.set_trace()
num_labels = np.zeros(shape=(data.shape[0]/(60*60/3), num_clusters))

for h in xrange(data.shape[0]/(60*60/3)):
    for n in xrange(num_clusters):
        num_labels[h,n] = np.where(estimator.labels_[h*60*60/3:(h+1)*60*60/3] == n)[0].shape[0]
for n in xrange(num_clusters):
    plt.plot(num_labels[:,n])
plt.xlabel("hour")
plt.ylabel("Count")
plt.show()
