__author__ = 'wangnxr'
import numpy as np
from sklearn.decomposition import PCA
import glob
import cPickle as pickle
import matplotlib.pyplot as plt
import pdb
import matplotlib.cm as cm
from pyESig2.preprocess.misc_info import patient_channels

def frequency_integration(data, low, hi, res=1):
    return np.sum(np.abs(data[:,int(low/res):int(hi/res)]), axis=1)

def ratio_measure(data):

    ratio1 = frequency_integration(data, 1, 30*2)/frequency_integration(data, 1, 80*2)
    ratio2 = frequency_integration(data, 1, 2*2)/frequency_integration(data, 1, 5*2)
    return (ratio1, ratio2)


def smooth(x, window_len=20):

     """ Hanning window smoothing """
     # extending the data at beginning and at the end
     # to apply the window at the borders

     s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
     w = np.hanning(window_len)
     y = np.convolve(w/w.sum(),s,mode='valid')
     return y[window_len/2:len(y)-(window_len/2-1)]


def plot_2d_coords(result):
    #samples = np.random.choice(len(result), 0.2*len(result))
    #plt.scatter(result[samples,0], result[samples,1], s=0.01)
    #mymap = plt.get_cmap("rainbow")
    x = np.arange(19)
    ys = [i+x+(i*x)**2 for i in range(20)]
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    f, axes = plt.subplots(19,1, sharex='col')
    for t in range(1,20,1):
        samples = np.random.choice(len(result[t*60*60:(t+1)*60*60,0]), 0.2*len(result[t*60*60:(t+1)*60*60,0]))
        axes[(t-1)].scatter(result[samples,0], result[samples,1], s=0.2, c="black", edgecolors="face")
    plt.show()

def main(data_fldr, sbj_id, day, channels):

    max_sec = 20*60*60
    result_temp_1 = np.zeros(shape=(max_sec, channels))
    result_temp_2 = np.zeros(shape=(max_sec, channels))
    result = np.zeros(shape=(max_sec, 2))

    for t in xrange(max_sec):
        if t%60==0:
            print "Processing minute: %i" % (t/60)
        try:
            data = pickle.load(open("%s\\%i_%i.p" % (data_fldr, day, t)))
            result_temp_1[t,:], result_temp_2[t,:]= ratio_measure(data)
        except IOError:
            print "Cannot open"

    print "pca"
    pca = PCA(n_components=1, whiten=True)
    result[:,0] = np.ndarray.flatten(pca.fit_transform(result_temp_1))
    result[:,1] = np.ndarray.flatten(pca.fit_transform(result_temp_2))

    print "Smoothing"
    result[:,0] = smooth(result[:,0])
    result[:,1] = smooth(result[:,1])
    plot_2d_coords(result)

    pickle.dump(result, open("E:\\ratio_mapping\\ecog_processed\\%s_%i_ratio_30_80.p" % (sbj_id, day), "wb"))
    return result


if __name__ == "__main__":
    sbj_id = "fcb01f7a"
    day = 13
    result = main("E:\\ratio_mapping\\ecog_processed\\%s\\" % sbj_id, sbj_id, day, patient_channels[sbj_id])
    #plot_2d_coords(pickle.load(open("E:\\ratio_mapping\\ecog_processed\\a86a4375_3_ratio_40_100.p")))