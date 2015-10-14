import numpy as np
from glob import glob
import sys
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pdb
import cPickle as pickle
from sklearn.decomposition import PCA

def load_and_track(f, file, total):
    if f%100==0:
        print "loading file " + str(f) + " of " + str(total) + " for file " + file
    data = pickle.load(open(file,"rb"))[:,:]
    return data

sbj_id = "d6532718"
days = [2,3,4,5,6,7,8]

#sbj_id = "ffb52f92"
#days = [3,4,5,6,7]

for day in days:
    datapath = "/media/nancy/Picon/ecog_processed/" + sbj_id + "/" + str(day) + "_"
    files_eeg = glob(datapath + '*.p')
    assert len(files_eeg) > 0, "Unable to read files!"
    new_files_eeg = []
    for f in files_eeg:
        name = f.split('/')[-1]
        vid, rest = name.split('_')
        num, _ = rest.split('.')
        if int(vid)==day:
            new_files_eeg.append(f)

    files_eeg = np.array(new_files_eeg)
    total_files = len(files_eeg)

    pickle.dump(files_eeg, open("/media/nancy/Picon/ecog_processed/d_reduced/index_pca_" + sbj_id + "_" + str(day) + ".p", "wb"))

    X_eeg = np.array([load_and_track(f, file, total_files)
                      for (f, file) in enumerate(files_eeg)], dtype= 'float64')


    X_eeg -= np.nanmean(X_eeg, axis=0)

    X_eeg /= np.nanstd(X_eeg, axis=0)

    X_eeg = np.nan_to_num(X_eeg)
    X_eeg = np.array([np.ndarray.flatten(f) for f in X_eeg])

    pca = PCA(n_components=50, whiten=True)
    result = pca.fit_transform(X_eeg)
    pickle.dump(result, open("/media/nancy/Picon/ecog_processed/d_reduced/transformed_pca_" + sbj_id + "_" + str(day) + ".p", "wb"))
    pickle.dump(pca, open("/media/nancy/Picon/ecog_processed/d_reduced/transformed_pca_model_" + sbj_id + "_" + str(day) + ".p", "wb"))
    print(pca.explained_variance_ratio_)

