import sklearn
import cPickle as pickle
import glob
import numpy as np
import itertools
import pdb


def synset_summary(synset_list):
    synset_dict = {}
    for synsets in synset_list:
        for synset in synsets:
            try:
                synset_dict[synset] += 1
            except KeyError:
                synset_dict[synset] = 1
    return synset_dict

def matches(list1, list2):
    match = []
    for item in list1:
        if item in list2:
            match.append(item)
    return match

def train_val_test_split(samples, synsets_to_do):
    data_len = min([value for value in samples.itervalues()])
    trainX = []
    trainY = []
    testX = []
    testY = []
    valX = []
    valY = []
    for synset, value in samples.iteritems():
        ind = np.arange(len(value))
        np.random.shuffle(ind)
        y = synsets_to_do.index(synset)
        trainX += value[ind[:int(0.8*data_len)]]
        trainY += [y]*int(0.8*data_len)
        valX += value[ind[int(0.8*data_len): int(0.9*data_len)]]
        valY += [y]*(int(0.9*data_len)-int(0.8*data_len))
        testX += value[ind[int(0.9 * data_len): data_len]]
        testY += [y] * (data_len - int(0.9 * data_len))

    return trainX, trainY, testX, testY, valX, valY

def gen_classification_data(data, synset, synsets_to_do):
    samples = {}
    for synset in synsets_to_do:
        samples[synset] = []
    for i in xrange(len(data)):
        match = matches(synset[i], synsets_to_do)
        if len(match) == 1:
            samples[match[0]].append(data[i])
    return samples

def gen_synsets_to_do(synset_dict, cutoff, n_way):
    eligible = [synset for synset, count in synset_dict.iteritems() if (count > cutoff)]
    return list(itertools.combinations(eligible, n_way))



sbj_id = "cb46fd46"
data_loc = "/home/nancy/Documents/speech/synset_mapping/"

data = []
synsets =[]
for file in glob.glob("%s/%s/*/power_feature_maps.p" % (data_loc, sbj_id)):
    input_data = pickle.load(open(file, "rb"))
    data += input_data["power"]
    synsets += input_data["synset"]
    synset_dict = synset_summary(synsets)
    synsets_to_do_list = gen_synsets_to_do(synset_dict, 100, 2)

    for synsets_to_do in synsets_to_do_list:
        print synsets_to_do
        samples = gen_classification_data(data, synsets, synsets_to_do)
        trainX, trainY, testX, testY, valX, valY = train_val_test_split(samples, synsets_to_do)
        model = sklearn.svm.SVC()
        model.fit(trainX, trainY)
        print model.score(testX, testY)
        pdb.set_trace()


