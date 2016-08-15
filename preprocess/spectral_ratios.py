__author__ = 'wangnxr'
import numpy as np
from sklearn.decomposition import PCA
import glob
import cPickle as pickle
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pdb
import matplotlib.cm as cm
import argparse
import logging
from pyESig2.preprocess.misc_info import patient_channels
import os


def frequency_integration(data, low, hi, res=1):

    return np.sum(np.abs(data[:,int(low/res):int(hi/res)]), axis=1)

def ratio_measure(data, ratio1, ratio2):

    ratio_res1 = frequency_integration(data, 1, ratio1[0]*2)/frequency_integration(data, 1, ratio1[1]*2)
    #ratio_res1 = frequency_integration(data,1,ratio1[0]*2)
    ratio_res2 = frequency_integration(data, 1, ratio2[0]*2)/frequency_integration(data, 1, ratio2[1]*2)
    return (ratio_res1, ratio_res2)


def smooth(x, window_len=20):

     """ Hanning window smoothing """
     # extending the data at beginning and at the end
     # to apply the window at the borders

     s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
     w = np.hanning(window_len)
     y = np.convolve(w/w.sum(),s,mode='valid')
     return y[window_len/2:len(y)-(window_len/2-1)]


def plot_2d_coords(result, ratio1, ratio2):
    #samples = np.random.choice(len(result), 0.2*len(result))
    #plt.scatter(result[samples,0], result[samples,1], s=0.01)
    #mymap = plt.get_cmap("rainbow")

    x = np.arange(6)
    ys = [i+x+(i*x)**2 for i in range(6)]
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    f, axes = plt.subplots(6,1, sharex='col', figsize=(5,15))

    for h in range(0,22,4):
        t = h/4
        samples = np.random.choice(len(result[h*60*60:(h+1)*60*60,0]), 0.5*len(result[h*60*60:(h+1)*60*60,0]))
        axes[t].scatter(result[samples + h*60*60,0], result[samples+h*60*60,1], s=0.2, c="black", edgecolors="face")
        axes[t].set_title("%i o'clock" % ((h+8)%24))
        axes[t].set_ylim([-1,1])

    axes[-1].set_xlabel("Ratio %i:%i Hz" %(ratio1[0], ratio1[1] ))
    axes[3].set_ylabel("Ratio %i:%i Hz" %(ratio2[0], ratio2[1] ))
    plt.tight_layout()

    return f

def plot_time(result, c):
    f = plt.figure()
    plt.plot(result[:,c])
    return f

def main(data_fldr, sbj_id, days, ratio1, ratio2, save_fldr):

    days_str = "_".join([str(day) for day in days])
    max_sec = 23*60*60
    if not os.path.exists( "%s/%s_%i_ratio_multi_day_%i_%i_%i_%i.p" % (save_fldr, sbj_id, days[0], ratio1[0],
                                                                ratio1[1], ratio2[0], ratio2[1])):

        result_temp_1 = np.zeros(shape=(max_sec * len(days), patient_channels[sbj_id]))
        result_temp_2 = np.zeros(shape=(max_sec * len(days), patient_channels[sbj_id]))
        result = np.zeros(shape=(max_sec * len(days), 2))

        for d in xrange(len(days)):
            for t in xrange(max_sec):
                if t%(60*60)==0:
                    print "Processing day: %i hour: %i" % (d, t/(60*60))
                try:
                    data = pickle.load(open("%s/%i_%i.p" % (data_fldr, days[d], t)))
                    result_temp_1[d*max_sec + t,:], result_temp_2[d*max_sec + t,:]= ratio_measure(data, ratio1, ratio2)
                except IOError:
                    print "Cannot open"

        print "remove extremes"
        result_temp_1_norm = (result_temp_1 - np.mean(result_temp_1))/np.std(result_temp_1)
        result_temp_2_norm = (result_temp_2 - np.mean(result_temp_2))/np.std(result_temp_2)

        invalid = (set(np.where(result_temp_1_norm>5)[0]) | set(np.where(result_temp_1_norm<-5)[0]) |
                   set(np.where(result_temp_2_norm>5)[0]) | set(np.where(result_temp_2_norm<-5)[0]))
        mask = np.ones(result.shape[0], dtype=bool)
        mask[list(invalid)]=False
        print "pca"
        pca = PCA(n_components=1, whiten=True)

        result[mask,0] = np.ndarray.flatten(pca.fit_transform(result_temp_1[mask,:]))
        result[mask,1] = np.ndarray.flatten(pca.fit_transform(result_temp_2[mask,:]))

        print "Smoothing"
        result[:,0] = smooth(result[:,0])
        result[:,1] = smooth(result[:,1])

        for d, day in enumerate(days):
            pickle.dump(result[d*max_sec:(d+1)*max_sec], open("%s/%s_%i_ratio_multi_day_%i_%i_%i_%i.p" % (save_fldr, sbj_id, day, ratio1[0],
                                                                    ratio1[1], ratio2[0], ratio2[1]), "wb"))

    else:
        result = []
        for d, day in enumerate(days):
            result.append(pickle.load(open("%s/%s_%i_ratio_multi_day_%i_%i_%i_%i.p" % (save_fldr, sbj_id, day, ratio1[0],
                                                                    ratio1[1], ratio2[0], ratio2[1]), "rb")))
        result = np.vstack(result)
    for d, day in enumerate(days):
        pdb.set_trace()
        figure = plot_2d_coords(result[d*max_sec:(d+1)*max_sec], ratio1, ratio2)
        figure.savefig("%s/%s_%i_ratio_multi_day_%i_%i_%i_%i.jpg" % (save_fldr, sbj_id, day, ratio1[0],
                                                                            ratio1[1], ratio2[0], ratio2[1]))
    plt.close()
    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sbj_id', required=True, help="Subject id")
    parser.add_argument('-d', '--day', required=True, help="Day of study", type=int, )
    parser.add_argument('-e', '--ecog_processed',
                        help='FFT extracted ecog file location', default="E:\\ratio_mapping\\ecog_processed\\")
    parser.add_argument('-r1', '--ratio1', help='First ratio pair', nargs=2, type=int)
    parser.add_argument('-r2', '--ratio2', help='Second ratio pair', nargs=2, type=int)
    parser.add_argument('-save', '--save', help='save directory', default="E:\\mvmt_pred_features\\")
    args = parser.parse_args()
    final_result = main(args.ecog_processed, args.sbj_id, args.day, args.ratio1, args.ratio2, args.save)