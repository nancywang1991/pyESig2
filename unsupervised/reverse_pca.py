import cPickle as pickle
import pdb
import matplotlib.pyplot as plt
import numpy as np
import scipy.io

def back_project(pca_model, cluster_center_file, best_corr_cluster, save_loc):
    model = pickle.load(open(pca_model, "rb"))
    cluster_centers = pickle.load(open(cluster_center_file, "rb"))
    results = {}
    for track, best_cluster in best_corr_cluster.iteritems():
        if best_cluster < len(cluster_centers):
            orig_activation = model.inverse_transform(cluster_centers[best_cluster])
            shape = [orig_activation.shape[0]/35, 35]
            results[track] = np.reshape(orig_activation,shape)
                ## Plot the spectrogram

            y, x = np.mgrid[slice(0, shape[0], 1),
                    slice(0, shape[1]*3, 3)]
            plt.pcolormesh(x,y,results[track], cmap='RdBu', vmin=-1, vmax=1)
            plt.axis([x.min(), x.max(), y.min(), y.max()])
            plt.colorbar()
            plt.title(track)
            plt.xlabel("Frequency")
            plt.ylabel("Channel")
            #plt.show()
            plt.savefig(save_loc + track + "_" + "orig_cluster_center.png")
            plt.close()

        pickle.dump(results, open(save_loc + "orig_cluster_center.p", "wb"))
        scipy.io.savemat(save_loc + "orig_cluster_center.mat", results)
