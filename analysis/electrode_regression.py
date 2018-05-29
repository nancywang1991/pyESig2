import pyedflib
import sklearn
import numpy as np

edf_file = pyedflib.EdfReader("/data1/decrypted_edf/d6532718/d6532718_4.edf")
train_period = [60*60*3, 60*60*3+60]
test_period = [60*60*4, 60*60*4+60]
channels = edf_file.getSignalLabels()
model = sklearn.linear_model.LinearRegression()

for c, chan in enumerate(channels):
    train_X = np.zeros(shape=(len(channels)-1, (train_period[1]-train_period[0])*1000))
    test_X = np.zeros(shape=(len(channels) - 1, (test_period[1] - test_period[0]) * 1000))

    for c2, chan2 in enumerate(np.hstack([np.arange(0,c), np.arange(c+1, len(channels))])):
        train_X[c2] = edf_file.readSignal(chan2)[train_period[0]*1000:train_period[1]*1000]
        test_X[c2] = edf_file.readSignal(chan2)[test_period[0]*1000:test_period[1]*1000]
    train_Y = edf_file.readSignal(c)[train_period[0]*1000:train_period[1]*1000]
    test_Y = edf_file.readSignal(c)[test_period[0] * 1000:test_period[1] * 1000]
    model.fit(train_X.T, train_Y)
    print "channel:%i" % c
    print "training accuracy:%f" % model.score(train_X.T, train_Y)
    print "testing accuracy:%f" % model.score(test_X.T, test_Y)




