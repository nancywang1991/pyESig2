__author__ = 'wangnxr'

import pdb
from scipy.io import loadmat, savemat
import glob
import numpy as np
import xmltodict
from PIL import Image

def label_crop(fname):
    with open(fname) as fd:
        doc = xmltodict.parse(fd.read())
        if doc["annotation"]["keypoints"] is None:
            return None
        xmin = np.inf
        xmax = -np.inf
        ymin = np.inf
        ymax = -np.inf
        for i in xrange(len(doc["annotation"]["keypoints"]["keypoint"])):
            cur_keypoint = doc["annotation"]["keypoints"]["keypoint"][i]
            xmin = min(xmin, float(cur_keypoint["@x"])-20)
            ymin = min(ymin, float(cur_keypoint["@y"])-20)
            xmax = max(xmax, float(cur_keypoint["@x"])+20)
            ymax = max(ymax, float(cur_keypoint["@y"])+20)
            if cur_keypoint["@name"] == "Nose":
                ymin = min(ymin, float(cur_keypoint["@y"])-70)
                ymax = min(ymin, float(cur_keypoint["@y"])+270)
    return [[xmin, ymin, xmax, ymax]]

def label_joints(fname):
    part_map = {"L_Shoulder":1, "L_Elbow":2, "L_Wrist":3, "R_Shoulder":4, "R_Elbow":5, "R_Wrist":6, "L_Eye":13, "R_Eye":14, "L_Ear":15, "R_Ear":16, "Nose":17}
    coords = np.empty((2,29))
    coords[:]=np.NAN

    with open(fname) as fd:
        doc = xmltodict.parse(fd.read())
        if doc["annotation"]["keypoints"] is None:
            return -1, -1, -1, -1
        for i in xrange(len(doc["annotation"]["keypoints"]["keypoint"])):
            cur_keypoint = doc["annotation"]["keypoints"]["keypoint"][i]
            x =float(cur_keypoint["@x"])
            y = float(cur_keypoint["@y"])
            if part_map.has_key(cur_keypoint["@name"]):
                coords[0,part_map[cur_keypoint["@name"]]-1]=x
                coords[1,part_map[cur_keypoint["@name"]]-1]=y
            if cur_keypoint["@name"] == "Nose":
                nose = [x,y]
            elif cur_keypoint["@name"] == "L_Ear":
                l_ear = [x,y]
            elif cur_keypoint["@name"] == "R_Ear":
                r_ear = [x,y]
        l_eye = np.mean([nose, l_ear], axis=0)
        r_eye = np.mean([nose, r_ear], axis=0)
        coords[0, part_map["L_Eye"]-1] = l_eye[0]
        coords[1, part_map["L_Eye"]-1] = l_eye[1]
        coords[0, part_map["R_Eye"]-1] = r_eye[0]
        coords[1, part_map["R_Eye"]-1] = r_eye[1]

    return [list(coords[0,:]),list(coords[1,:])]

image_path_main= "/home/wangnxr/Documents/darknet/yolo/train_data/VOCdevkit/"
subjects=["a0f66459", "a86a4375", "ab2431d9", "c95c1e82", "cb46fd46", "d6532718", "d7d5f068", "e70923c4"]
examples = loadmat(open("/home/wangnxr/Documents/deeppose/data/FLIC-full/examples.mat", "rb"))
tr_indices = loadmat(open("/home/wangnxr/Documents/deeppose/data/FLIC-full/tr_plus_indices.mat", "rb"))

for sbj in subjects:
    for f in glob.glob(image_path_main + sbj + "/info/" + "*.xml"):
        new_example = np.array(np.empty(1), dtype=np.dtype(examples['examples'][0][0]))
        crop = label_crop(f)
        if crop is not None:
            #poselet_hit_idx
            new_example[0][0]=[np.NAN]
            #moviename
            new_example[0][1]=[sbj]
            #coords
            new_example[0][2]=label_joints(f)
            img_name = f.split("/")[-1][:-6] + ".jpg"
            img_path = image_path_main + sbj + "/JPEGImages/" + img_name
            #filepath
            new_example[0][3]=img_path
            img_dim = Image.open(img_path).size
            #imgdims
            new_example[0][4]=[img_dim[0], img_dim[1], 3]
            frame = int(img_name.split("_")[-1][:-4])
            #currframe
            new_example[0][5]=[[frame]]
            #torsobox
            new_example[0][6]=crop
            if np.random.randint(0,100)>75:
                #istrain
                new_example[0][7]=[[0]]
                #istest
                new_example[0][8]=[[1]]
            else:
                np.append(tr_indices["tr_plus_indices"],np.array([[len(examples['examples'][0])+1]]), axis=0)
                new_example[0][7]=[[1]]
                new_example[0][8]=[[0]]
            #isbad
            new_example[0][9]=[[0]]
            #isunchecked
            new_example[0][10]=[[0]]
            np.append(examples['examples'][0], new_example, axis=0)
            pdb.set_trace()

savemat("/home/wangnxr/Documents/deeppose/data/FLIC-full/examples_patients.mat", examples)
savemat("/home/wangnxr/Documents/deeppose/data/FLIC-full/tr_plus_indices_patients.mat", tr_indices)
