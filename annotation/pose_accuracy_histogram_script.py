__author__ = 'wangnxr'
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
from pyESig2.movement.joint_movement_norm import normalize_to_camera, numerate_coords
import pdb

annotation_file = "C:\Users\Nancy\Downloads\OneDrive_2017-03-02\info_e5bad52f\joint_locations.p"
annotations = pickle.load(open(annotation_file))
pose_dir = "C:\\Users\\Nancy\\Documents\\results\\e5bad52f_2\\"
crop_dir = "C:\\Users\\Nancy\\Documents\\results\\crop_coords\\"
save_dir = "C:\\Users\\Nancy\\Documents\\results\\"

accuracy = {}
joints_key ={"Nose":0, "R_Wrist":1, "L_Wrist":2, "R_Elbow":3, "L_Elbow":4, "R_Shoulder":5, "L_Shoulder":6}
for filename, annotation in annotations.iteritems():
    print filename
    sbj_id, day, vid_number = filename.split("_")[:3]
    pose_file = open("%s/%s_%s_%s.txt" %(pose_dir, sbj_id, day, vid_number))
    try:
        crop_coords = open(os.path.normpath("%s/%s_%s_%s.txt" % (crop_dir, sbj_id, day, vid_number))).readlines()[1500]
    except IOError:
        print "Crop coords for %s not found" % (filename)
        break
    crop_coords = np.array([int(coord) for coord in crop_coords.split(',')])
    pose_coords = numerate_coords(pose_file.readlines()[1500])
    pose_result = normalize_to_camera(pose_coords, crop_coords)
    for joint, coord in annotation.iteritems():
        if joint in joints_key:
            x_dist = coord[0] - pose_result[joints_key[joint]][0]
            y_dist = coord[1] - pose_result[joints_key[joint]][1]
            dist = np.sqrt(x_dist**2 + y_dist**2)
            if not joint in accuracy:
                accuracy[joint] = []
            accuracy[joint].append(np.array([dist, pose_coords[joints_key[joint]][2]]))
#pdb.set_trace()
for joint, acc in accuracy.iteritems():
    #accuracy histogram
    plt.clf()
    acc_array = np.array(acc)
    plt.hist2d(acc_array[:,1], acc_array[:,0], bins=(10,100))
    plt.xlabel("Confidence")
    plt.ylabel("Error(pixels)")
    #plt.ylim([0,50])
    plt.title("Error histogram for joint %s" % joint)
    plt.colorbar()
    plt.savefig("%s/%s.png" % (save_dir, joint))


