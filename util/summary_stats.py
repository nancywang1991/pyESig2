import numpy as np

def print_averages(dictionary):
    for key, value in dictionary.iteritems():
        print key
        value_temp = np.array(value)
        print np.nanmean(value_temp[np.where(value_temp>0)[0]])