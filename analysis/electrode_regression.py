import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pyedflib
import sklearn
import sklearn.linear_model
import numpy as np
import scipy
import scipy.io
import pdb

sbj_id = "a0f66459"
edf_file = pyedflib.EdfReader("/data1/decrypted_edf/%s/%s_8.edf" % (sbj_id, sbj_id))
test_period_awake = [60*60*4, 60*60*4+60*10]
test_period_asleep = [60*60*21, 60*60*21+60*10]
train_period_asleep = [60*60*20, 60*60*20+60*10]
train_period_awake = [60*60*3, 60*60*3 +60*10]

train_period = train_period_awake

save_fname = "/home/nancy/results/reconstruct_lin_reg_%s_awake.mat" % sbj_id

channels = edf_file.getSignalLabels()[1:80]
model = sklearn.linear_model.LinearRegression()
result_mat = {"train": [], "test_asleep": [], "test_awake": []} 

#Data gathering

train_X_all = np.zeros(shape=(len(channels), (train_period[1]-train_period[0])*1000))
test_X_asleep_all = np.zeros(shape=(len(channels), (test_period_asleep[1] - test_period_asleep[0]) * 1000))
test_X_awake_all = np.zeros(shape=(len(channels), (test_period_awake[1] - test_period_awake[0]) * 1000))

for c, chan in enumerate(channels):
    train_X_all[c] = edf_file.readSignal(c+1, start=train_period[0]*1000, n=(train_period[1]-train_period[0])*1000)
    test_X_asleep_all[c] = edf_file.readSignal(c+1, start=test_period_asleep[0]*1000, n=(test_period_asleep[1]-test_period_asleep[0])*1000)
    test_X_awake_all[c] = edf_file.readSignal(c+1, start=test_period_awake[0]*1000, n=(test_period_awake[1]-test_period_awake[0])*1000)

#regression
for c, chan in enumerate(channels):
    train_X = np.vstack([train_X_all[:c], train_X_all[c+1:]])
    test_X_asleep = np.vstack([test_X_asleep_all[:c], test_X_asleep_all[c+1:]])
    test_X_awake = np.vstack([test_X_awake_all[:c], test_X_awake_all[c+1:]])

    train_Y = train_X_all[c]
    test_Y_asleep = test_X_asleep_all[c]
    test_Y_awake = test_X_awake_all[c]

    model.fit(train_X.T, train_Y)
    train_acc =  np.sqrt(np.mean(np.divide((model.predict(train_X.T) - train_Y),train_Y)**2))
    test_acc_asleep =  np.sqrt(np.mean(np.divide((model.predict(test_X_asleep.T) - test_Y_asleep),test_Y_asleep)**2))
    test_acc_awake = np.sqrt(np.mean(np.divide((model.predict(test_X_awake.T) - test_Y_awake),test_Y_awake)**2))
    #train reconstruction
    plt.plot(model.predict(train_X.T)[:2000], label="Reconstructed Voltage")
    plt.plot(train_Y[:2000], label="True Voltage")
    plt.xlabel("Time step")
    plt.ylabel("voltage")
    plt.title("%s_train_ch_%i" % (save_fname.split(".")[0], c))
    plt.legend()
    plt.savefig("%s_train_ch_%i.png" % (save_fname.split(".")[0], c))
    plt.close()


    plt.plot(model.predict(test_X_awake.T)[:2000], label="Reconstructed Voltage")
    plt.plot(test_Y_awake[:2000], label="True Voltage")
    plt.xlabel("Time step")
    plt.ylabel("voltage")
    plt.title("%s_test_awake_ch_%i" % (save_fname.split(".")[0], c))
    plt.legend()
    plt.savefig("%s_test_awake_ch_%i.png" % (save_fname.split(".")[0], c))
    plt.close()
    
    plt.plot(model.predict(test_X_asleep.T)[:2000], label="Reconstructed Voltage")
    plt.plot(test_Y_asleep[:2000], label="True Voltage")
    plt.xlabel("Time step")
    plt.ylabel("voltage")
    plt.title("%s_test_asleep_ch_%i" % (save_fname.split(".")[0], c))
    plt.legend()
    plt.savefig("%s_test_asleep_ch_%i.png" % (save_fname.split(".")[0], c))
    plt.close()
    
    print "training accuracy:%f" % train_acc
    print "sleep testing accuracy:%f" % test_acc_asleep
    print "awake testing accuracy:%f" % test_acc_awake
    result_mat["train"].append(train_acc)
    result_mat["test_asleep"].append(test_acc_asleep)
    result_mat["test_awake"].append(test_acc_awake)

scipy.io.savemat(save_fname, result_mat)


