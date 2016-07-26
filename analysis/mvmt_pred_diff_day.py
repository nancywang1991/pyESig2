__author__ = 'wangnxr'
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
import pickle
from random import shuffle
import numpy as np
import pdb
offsets = range(-3,3)
for offset in offsets:

    pos_data_train = pickle.load(open("E:\\mvmt_pred_features\\fcb01f7a_12_13_pos_offset_%i.p" % offset))
    neg_data_train = pickle.load(open("E:\\mvmt_pred_features\\fcb01f7a_12_13_neg_offset_%i.p" % offset))

    shuffle(neg_data_train)
    shuffle(pos_data_train)
    clf = RandomForestClassifier()

    y = np.zeros(len(pos_data_train) + len(pos_data_train))

    y[:len(pos_data_train)] = 1
    recalls = []
    precisions = []
    true_neg = []
    accuracy = []
    for i in xrange(100):
        clf.fit(np.array(pos_data_train + neg_data_train[:len(pos_data_train)]), y)
        pos_results = clf.predict(pickle.load(open("E:\\mvmt_pred_features\\fcb01f7a_15_pos_offset_%i.p" % offset)))
        neg_data = pickle.load(open("E:\\mvmt_pred_features\\fcb01f7a_15_neg_offset_%i.p" % offset))
        #np.random.shuffle(neg_data)
        neg_results = clf.predict(neg_data)
        precisions.append(sum(pos_results)/(float(sum(neg_results) + sum(pos_results))))
        recalls.append(sum(pos_results)/float(len(pos_results)))
        true_neg.append((len(neg_results)-sum(neg_results))/len(neg_results))
        accuracy.append(np.mean([true_neg[-1],recalls[-1]] ))

    print offset
    print "True Positive: %.5f std: %.5f" % (np.mean(recalls), np.std(precisions))
    print "True Negative:%.5f std: %.5f" % (np.mean(true_neg), np.std(true_neg))
    print "Accuracy:%.5f std: %.5f" % (np.mean(accuracy), np.std(accuracy))

