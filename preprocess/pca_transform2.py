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
    data = pickle.load(open(file,"rb"))[:,:35]

    data[np.where(data>10**11)] = np.nan

    return data

sbj_id = "d6532718"
days = [4,5,6,7,8]
components = 50

#sbj_id = "ffb52f92"
#days = [3,4,5,6,7]

for day in days:
    #datapath = "/media/nancy/Picon/ecog_processed/" + sbj_id + "/" + str(day) + "_"
    datapath = "D:\\ecog_processed\\" + sbj_id + "\\" + str(day) + "_"
    files_eeg = glob(datapath + '*.p')
    assert len(files_eeg) > 0, "Unable to read files!"
    new_files_eeg = []
    for f in files_eeg:
        name = f.split('\\')[-1]
        vid, rest = name.split('_')
        num, _ = rest.split('.')
        if int(vid)==day and int(num) < 15000:
            new_files_eeg.append(f)

    files_eeg = np.array(new_files_eeg)
    total_files = len(files_eeg)

    #pickle.dump(files_eeg, open("/media/nancy/Picon/ecog_processed/d_reduced/index_pca_" + sbj_id + "_" + str(day) + ".p", "wb"))
    pickle.dump(files_eeg, open("D:\\ecog_processed\\d_reduced\\index_pca_" + sbj_id + "_" + str(day) + ".p", "wb"))

    X_eeg = np.array([load_and_track(f, file, total_files)
                      for (f, file) in enumerate(files_eeg)], dtype= 'float64')


    X_eeg -= np.nanmean(X_eeg, axis=0)

    X_eeg /= np.nanstd(X_eeg, axis=0)

    #X_eeg = np.nan_to_num(X_eeg)

    X_eeg_no_nan_l=[]
    valid_pos = []
    for i,x in enumerate(X_eeg):
        if not np.isnan(x).any():
            X_eeg_no_nan_l.append(np.ndarray.flatten(x))
            valid_pos.append(i)
    print len(valid_pos)/float(len(X_eeg))
    X_eeg_no_nan = np.array(X_eeg_no_nan_l)
    result = np.empty(shape=(X_eeg.shape[0], components))
    result[:,:] = np.nan
    pca = PCA(n_components=components, whiten=True)
    result_temp = pca.fit_transform(X_eeg_no_nan)
    result[valid_pos,:] = result_temp

    #pickle.dump(result, open("/media/nancy/Picon/ecog_processed/d_reduced/transformed_pca_" + sbj_id + "_" + str(day) + ".p", "wb"))
    #pickle.dump(pca, open("/media/nancy/Picon/ecog_processed/d_reduced/transformed_pca_model_" + sbj_id + "_" + str(day) + ".p", "wb"))
    #pickle.dump(valid_pos, open("/media/nancy/Picon/ecog_processed/d_reduced/valid_pos_" + sbj_id + "_" + str(day) + ".p", "wb"))
    pickle.dump(result, open("D:\\ecog_processed\\d_reduced\\transformed_pca_" + sbj_id + "_" + str(day) + ".p", "wb"))
    pickle.dump(pca, open("D:\\ecog_processed\\d_reduced\\transformed_pca_model_" + sbj_id + "_" + str(day) + ".p", "wb"))
    pickle.dump(valid_pos, open("D:\\ecog_processed\\d_reduced\\valid_pos_" + sbj_id + "_" + str(day) + ".p", "wb"))
    print(pca.explained_variance_ratio_)

