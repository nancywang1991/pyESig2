__author__ = 'wangnxr'

import pdb
from scipy.io import loadmat, savemat
import glob
import numpy as np
import xmltodict
from PIL import Image
import cv2
import os


def relabel_joints(coords, top, left):
    part_map = {"L_Shoulder":1, "L_Elbow":2, "L_Wrist":3, "R_Shoulder":4, "R_Elbow":5, "R_Wrist":6, "L_Eye":13, "R_Eye":14, "L_Ear":15, "R_Ear":16, "Nose":17}
    new_part_map = ["Nose", "R_Wrist", "L_Wrist", "R_Elbow", "L_Elbow", "R_Shoulder", "L_Shoulder"]
    new_coords = np.zeros(7*2)

    for i in xrange(7):
        if coords[0][part_map[new_part_map[i]]-1] >= 640 or coords[1][part_map[new_part_map[i]]-1]>= 480:
            return []
        new_coords[2*i] = coords[0][part_map[new_part_map[i]]-1]-left
        new_coords[2*i+1] = coords[1][part_map[new_part_map[i]]-1]-top
    return new_coords

def make_crop_img(path, image_path_flic_main, crop_coords, new_image_fldr, is_test):
    if os.path.exists(path):
        img = cv2.imread(path)
        img_name = path.split("/")[-1]
        top = max(int(crop_coords[1]-50), 0)
        left = max(int(crop_coords[0] - 50), 0)
        cropped_img = img[top:int(crop_coords[3]+50), left:int(crop_coords[2]+50)]
    else:
        img = cv2.imread(image_path_flic_main + path)
        img_name = path
        top = max(int(crop_coords[1]-180), 0)
        left = max(int(crop_coords[0] - 150), 0)
        cropped_img = img[top:int(crop_coords[3]+120), left:int(crop_coords[2]+170)]
    if cropped_img.shape[0] < 270 or cropped_img.shape[1] < 270:
        return None, None, None
    if is_test:
        cv2.imwrite(new_image_fldr+ "/test/" + img_name, cropped_img)
        return "test/" + img_name, top, left
    else:
        cv2.imwrite(new_image_fldr+ "/train/" + img_name, cropped_img)
        return "train/" + img_name, top, left

image_path_patient_main= "/home/wangnxr/Documents/patient_pose_data/"
image_path_flic_main = "/home/wangnxr/Documents/deeppose/data/FLIC-full/images/"
new_image_fldr = "/home/wangnxr/Documents/patient_pose_data/caffe_heatmap/"
mat_sample = loadmat("/home/wangnxr/Documents/deeppose/data/FLIC-full/examples_patients.mat")
train_list = open("%s/train_patients.txt" % (new_image_fldr), "wb")
test_list = open("%s/test_patients.txt" % (new_image_fldr), "wb")

for example in mat_sample["examples"][0]:
    img_path, top, left= make_crop_img(example[3][0], image_path_flic_main, example[6][0], new_image_fldr, example[8][0])

    if img_path is not None:
        coords = relabel_joints(example[2], top, left)
        if len(coords)>0 and not np.any(coords<0) and not np.any(np.isnan(coords)):
            if example[8][0] == 0:
                try:
                    train_list.write("%s %s 0,0,0,0,0 0\n" %(img_path, ','.join([str(int(c)) for c in coords])))
                except:
                    pdb.set_trace()
            else:
                test_list.write("%s %s 0,0,0,0,0 0\n" %(img_path, ','.join([str(int(c)) for c in coords])))

train_list.close()
test_list.close()
