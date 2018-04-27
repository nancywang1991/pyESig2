import sklearn.svm
import cPickle as pickle
import glob
import numpy as np
import itertools
import pdb
import sklearn.ensemble
from sklearn.model_selection import cross_val_score

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
    data_len = min([len(value) for value in samples.itervalues()])
    train_len = int(0.8*data_len)
    val_len = int(0.9*data_len)-int(0.8*data_len)
    test_len = data_len-int(0.9*data_len)
    sample_shape = np.ndarray.flatten(samples.values()[0][0]).shape[0]
    categories = len(synsets_to_do)
    trainX = np.zeros(shape=(train_len*categories, sample_shape))
    trainY = np.zeros(train_len*categories)
    testX = np.zeros(shape=(test_len*categories, sample_shape))
    testY = np.zeros(test_len*categories)
    valX = np.zeros(shape=(val_len*categories, sample_shape))
    valY = np.zeros(val_len*categories)
    cur_cat = 0
    for synset, value in samples.iteritems():
        value = np.reshape(value, (len(value), sample_shape))
        ind = np.arange(len(value))
        np.random.shuffle(ind)
        y = synsets_to_do.index(synset)
        trainX[cur_cat*train_len:(cur_cat+1)*train_len] = value[ind[:train_len]]
        trainY[cur_cat*train_len:(cur_cat+1)*train_len] = y
        valX[cur_cat*val_len:(cur_cat+1)*val_len] = value[ind[int(0.8*data_len): int(0.9*data_len)]]
        valY[cur_cat*val_len:(cur_cat+1)*val_len] = y
        testX[cur_cat*test_len:(cur_cat+1)*test_len] = value[ind[int(0.9 * data_len): data_len]]
        testY[cur_cat*test_len:(cur_cat+1)*test_len] = y
        cur_cat += 1
    return trainX, trainY, testX, testY, valX, valY

def gen_classification_data(data, data_synset, synsets_to_do):
    samples = {}
    for synset in synsets_to_do:
        samples[synset] = []
    for i in xrange(len(data)):
        match = matches(data_synset[i], synsets_to_do)
        if len(match) == 1:
            samples[match[0]].append(data[i])
    return samples

def gen_synsets_to_do(synset_dict, cutoff, n_way):
    eligible = [synset for synset, count in synset_dict.iteritems() if (count > cutoff)]
    combos = list(itertools.combinations(eligible, n_way))
    return [synsets for synsets in combos if synsets[0].split(".")[1]==synsets[1].split(".")[1]]


def main():
    sbj_id = "a0f66459"
    data_loc = "/home/nancy/Documents/speech/synset_mapping/"

    data = []
    synsets =[]
    for file in glob.glob("%s/%s/*/power_feature_maps.p" % (data_loc, sbj_id)):
        if file.split("/")[-2] == "cb46fd46_4":
            continue
        input_data = pickle.load(open(file, "rb"))
        data += input_data["power"]
        synsets += input_data["synset"]
    valid_ind = [i for i, datum in enumerate(data) if not (np.isnan(datum).any() or np.isinf(datum).any())]
    data = np.array(data)[valid_ind]
    synsets = np.array(synsets)[valid_ind]
    synset_dict = synset_summary(synsets)
    synsets_to_do_list = gen_synsets_to_do(synset_dict, 300, 2)

    for synsets_to_do in synsets_to_do_list:
        samples = gen_classification_data(data, synsets, synsets_to_do)
        if min([len(value) for value in samples.itervalues()]) < 200:
            continue
        trainX, trainY, testX, testY, valX, valY = train_val_test_split(samples, synsets_to_do)
        model = sklearn.ensemble.RandomForestClassifier()
        print synsets_to_do
        print np.mean(cross_val_score(model, trainX, trainY, cv=10))
        #model.fit(trainX, trainY)
        #score =  model.score(testX, testY)
        #if score > 0.55:
        #    print synsets_to_do
        #    print score
        #    print model.score(valX, valY)
        #    print np.mean(cross_val_score(model, trainX, trainY, cv=10))
        #    print model.score(trainX, trainY)
        #pdb.set_trace()

if __name__=="__main__":
    main()


