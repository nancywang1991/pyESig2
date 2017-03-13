__author__ = 'wangnxr'
import xmltodict
import numpy as np
import glob
import os
import pickle

def label_parse(fname):
    result = {}
    with open(fname) as fd:
        doc = xmltodict.parse(fd.read())
        if doc["annotation"]["keypoints"] is None:
            return -1, -1, -1, -1
        xmin = np.inf
        xmax = -np.inf
        ymin = np.inf
        ymax = -np.inf
        for i in xrange(len(doc["annotation"]["keypoints"]["keypoint"])):
            cur_keypoint = doc["annotation"]["keypoints"]["keypoint"][i]
            name = cur_keypoint["@name"]
            y = float(cur_keypoint["@y"])
            x = float(cur_keypoint["@x"])
            result[name] = (x,y)
    return result



label_dir = "C:\Users\Nancy\Downloads\OneDrive_2017-03-02\info_e5bad52f"

results = {}
for fname in glob.glob(label_dir + "\\info\\*"):
    print fname
    result = label_parse(fname)
    results[os.path.basename(fname)] = result

pickle.dump(results, open("%s\\joint_locations.p" % label_dir, "wb"))