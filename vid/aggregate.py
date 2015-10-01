import cPickle as pickle
import numpy as np
import os
import edflib._edflib as edflib
import pdb
import matplotlib.pyplot as plt
from pyESig2.vid.feature_chunk_class import feature_chunk
from pyESig2.vid.misc_funcs import has_video

sbj_id = "e70923c4"
day = 5
sr=30
input_file_loc = "E:\\mvmt\\e70923c4\\"
output_file_loc = input_file_loc
has_video_array = has_video("C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\disconnect_times\\" \
                            + sbj_id + "_" + str(day) + ".txt", samp_rate = sr)

total_features = np.zeros(has_video_array.shape[0])
feature_obj = feature_chunk(input_file_loc, sbj_id, day)
for f in xrange(has_video_array.shape[0]):
    if has_video_array[f] == 0:
        total_features[f] = -1
    else:
        if feature_obj.has_next():
            total_features[f] = feature_obj.next()

        else:

            total_features[f] = -1

pickle.dump(total_features, open(output_file_loc + sbj_id + "_" + str(day) + ".p" , "wb"))

plt.plot(np.array(range(270*30*60))/(60*30.0), total_features[:270*30*60])
#plt.ylim([10**11,6*10**15])
plt.xlabel("Time (Min)")
plt.ylabel("Speech sound level")
plt.show()