__author__ = 'wangnxr'

import pdb
from scipy.io import loadmat, savemat
import glob
import numpy as np
import xmltodict
from PIL import Image
import cv2
import os


def relabel_joints(coords, crop_coords):
    part_map = {"L_Shoulder":1, "L_Elbow":2, "L_Wrist":3, "R_Shoulder":4, "R_Elbow":5, "R_Wrist":6, "L_Eye":13, "R_Eye":14, "L_Ear":15, "R_Ear":16, "Nose":17}
    new_part_map = ["Nose", "L_Wrist", "R_Wrist", "L_Elbow", "R_Elbow", "L_Shoulder", "R_Shoulder"]
    new_coords = np.zeros(8*2)
    for i in xrange(8):
        new_coords[2*i] = coords[0][new_part_map[i-1]]-crop_coords[1]
        new_coords[2*i+1] = coords[1][new_part_map[i-1]]-crop_coords[0]
    return new_coords

def make_crop_img(path, image_path_flic_main, crop_coords, new_image_fldr, is_test):
    if os.path.exists(path):
        img = cv2.imread(path)
        img_name = path.split("/")[-1]
    else:
        img = cv2.imread(image_path_flic_main + path)
        img_name = path
    cropped_img = img[crop_coords[0]:crop_coords[2], crop_coords[1]:crop_coords[3]]
    if is_test:
        cv2.imwrite(new_image_fldr+ "/test/" + img_name, cropped_img)
        return new_image_fldr+ "/test/" + img_name
    else:
        cv2.imwrite(new_image_fldr+ "/train/" + img_name, cropped_img)
        return new_image_fldr+ "/train/" + img_name

image_path_patient_main= "/home/wangnxr/Documents/patient_pose_data/"
image_path_flic_main = "/home/wangnxr/Documents/data/FLIC_full/images/"
new_image_fldr = "/home/Documents/patient_pose_data/caffe_heatmap/"
subjects=["a0f66459", "a86a4375", "ab2431d9", "c95c1e82", "cb46fd46", "d6532718", "d7d5f068", "e70923c4"]
examples = loadmat(open("/home/wangnxr/Documents/deeppose/data/FLIC-full/examples.mat", "rb"))
tr_indices = loadmat(open("/home/wangnxr/Documents/deeppose/data/FLIC-full/tr_plus_indices.mat", "rb"))
mat_sample = loadmat("/home/wangnxr/Documents/deeppose/data/FLIC-full/examples_patients_all.mat")
train_list = open("%s/train_patients.txt" % (new_image_fldr), "wb")
test_list = open("%s/test_patients.txt" % (new_image_fldr), "wb")
for sbj in subjects:
    for example in mat_sample["examples"][0]:
        img_path= make_crop_img(example[3][0], image_path_flic_main, example[0][6][0], new_image_fldr, example[0][8][0])
        coords = relabel_joints(example[2][0], example[0][6][0])
        if example[0][8][0] == 1:
            train_list.write("%s %s 0,0,0,0,0 0\n" %(img_path, ','.join(coords)))
        else:
            test_list.write("%s %s 0,0,0,0,0 0\n" %(img_path, ','.join(coords)))
        pdb.set_trace()
train_list.close()
test_list.close()
