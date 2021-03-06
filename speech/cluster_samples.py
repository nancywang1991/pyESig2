import sklearn.cluster
import cPickle as pickle
import numpy as np
import glob
from classify_synsets import *
import pdb

sbj_id = "d6532718"
data_loc = "/home/nancy/Documents/speech/synset_mapping/"

def extract_sample_ind(data, synsets, synset_to_do):
    sample_ind = []
    for i in xrange(len(data)):
        if synset_to_do in synsets[i]:
            sample_ind.append(i)
    return sample_ind

def main():
    data = []
    synsets =[]
    transcript = []
    for file in glob.glob("%s/%s/*/power_feature_maps.p" % (data_loc, sbj_id)):
        if file.split("/")[-2] == "cb46fd46_4":
            continue
        input_data = pickle.load(open(file, "rb"))
        data += input_data["power"]
        synsets += input_data["synset"]
        transcript += input_data["transcript"]
    valid_ind = [i for i, datum in enumerate(data) if not (np.isnan(datum).any() or np.isinf(datum).any())]
    data = np.array(data)[valid_ind]
    synsets = np.array(synsets)[valid_ind]
    transcript = np.array(transcript)[valid_ind]

    model = sklearn.cluster.KMeans(n_clusters=10)
    synset_dict = synset_summary(synsets)

    for synset_to_do in [synset for synset, count in synset_dict.iteritems() if count > 200]:
        sample_ind = extract_sample_ind(data, synsets, synset_to_do)
        clusters = model.fit_predict(data[sample_ind, 2])
        for i in xrange(10):
            print i
            print transcript[sample_ind][np.where(clusters==i)[0]]
            pdb.set_trace()
if __name__=="__main__":
    main()
