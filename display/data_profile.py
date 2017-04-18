import pickle
import matplotlib.pyplot as plt
import numpy as np
import pdb

day = 10
sbj_id = "e5bad52f"
file = pickle.load(open("C:\\Users\\Nancy\\Documents\\data\\%s_means_stds\\%s_stds_%i.p" % (sbj_id,sbj_id,day)))
file_mean = pickle.load(open("C:\\Users\\Nancy\\Documents\\data\\%s_means_stds\\%s_means_%i.p" % (sbj_id,sbj_id,day)))
file_fft = pickle.load(open("C:\\Users\\Nancy\\Documents\\data\\%s_means_stds\\%s_ffts_%i.p" % (sbj_id,sbj_id,day)))
norm_file = pickle.load(open("C:\\Users\\Nancy\\Documents\\data\\%s_means_stds\\%s_norm_factors_%i.p" % (sbj_id,sbj_id,day)))

for c in xrange(93):
    f, axarr = plt.subplots(8, figsize=(8,18))

    axarr[0].hist(file[c,:-1000], bins=np.arange(0, 0.001 + 0.000001, 0.000001))
    axarr[0].set_title("Histogram of standard deviation of day %i channel %i" % (day, c+1))
    axarr[1].plot(file[c,:-1000:100])
    axarr[1].set_ylim([0,0.0005])
    axarr[1].set_title("Standard deviation of day %i channel %i" % (day,c + 1))
    axarr[1].set_xlabel("Second")
    axarr[0].text(0.05, 0.95, "Overall std: %f" % norm_file[c,1], transform=axarr[0].transAxes, fontsize=14,
            verticalalignment='top')

    axarr[2].hist(file_mean[c,:-1000], bins=np.arange(0, 0.01 + 0.000001, 0.000001))
    axarr[2].set_title("Histogram of mean of day %i channel %i" % (day, c+1))
    axarr[3].plot(file_mean[c,:-1000:100])
    axarr[3].set_ylim([np.mean(file_mean[c,:-1000])-3*np.std(file_mean[c,:-1000]), np.mean(file_mean[c,:-1000])+3*np.std(file_mean[c,:-1000])])
    axarr[3].set_title("Mean of day %i channel %i" % (day, c + 1))
    axarr[3].set_xlabel("Second")
    axarr[2].text(0.05, 0.55, "Overall mean: %f" % norm_file[c,0], transform=axarr[0].transAxes, fontsize=14,
            verticalalignment='center')

    axarr[4].hist(file_fft[c, :-1000, 0], bins=np.arange(0, 0.001 + 0.000001, 0.000001))
    axarr[4].set_title("Histogram of power (2-5Hz) of day %i channel %i" % (day, c + 1))
    axarr[5].plot(file_fft[c, :-1000:100, 0])
    #pdb.set_trace()
    axarr[5].set_ylim([-0.0001, 0.0003])
    axarr[5].set_title("Power (2-5Hz) of day %i channel %i" % (day, c + 1))
    axarr[5].set_xlabel("Second")

    axarr[6].hist(file_fft[c, :-1000, 1], bins=np.arange(0, 0.0005 + 0.000001, 0.000001))
    axarr[6].set_title("Histogram of power (30-40Hz) of day %i channel %i" % (day, c + 1))
    axarr[7].plot(file_fft[c, :-1000:100, 1])
    # pdb.set_trace()
    axarr[7].set_ylim([-0.00001, 0.00003])
    axarr[7].set_title("Power (30-40Hz) of day %i channel %i" % (day, c + 1))
    axarr[7].set_xlabel("Second")

    plt.tight_layout()
    plt.savefig("C:\\Users\\Nancy\\Documents\\data\\%s_means_stds\\day%i\\chan_%i.png" % (sbj_id,day,c))
    plt.close()
