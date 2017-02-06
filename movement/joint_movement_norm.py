import matplotlib as mpl
mpl.use('Agg')
import sys
sys.path.append('/home/wangnxr/Documents/deeppose/tests')
import numpy as np
import csv
import argparse
import matplotlib.pyplot as plt
import pickle
import pdb
import cv2
import glob
#from test_flic_dataset import draw_joints
import os
import subprocess
from scipy.signal import savgol_filter
import copy

joint_map = ['head', 'right wrist', 'left wrist', 'right elbow', 'left elbow',  'right shoulder', 'left shoulder']

def calc_dist(a,b):
    final_dist = []
    for i, coord in enumerate(b):
        if np.all(np.array(coord) > -1000) and np.all(np.array(a[i]) > -1000):
            final_dist.append(np.sqrt((coord[0]-a[i][0])**2 + (coord[1]-a[i][1])**2))
        else:
            final_dist.append(-1000)
    return final_dist

def calc_dist_vectors(a,b):
    final_dist = []
    for i, coord in enumerate(b):
        if np.all(np.array(coord)>-1000) and np.all(np.array(a[i])>-1000):
            final_dist.append(np.array((coord[0]-a[i][0], coord[1]-a[i][1])))
        else:
            final_dist.append(-1000)
    return np.hstack(final_dist)

def numerate_coords(coords):
    final_coords = []
    #print coords.split(')\n')[0].split('),')
    for coord in coords.split(')\n')[0].split('),'):
        (x,y,c) = coord.split('(')[1].split(',')
        final_coords.append(np.array((float(x),float(y), float(c))))
    return np.array(final_coords)

def normalize_to_neck(coords):
    coords = numerate_coords(coords)
    neck = np.mean([coords[2], coords[4]])
    #shoulder_length = calc_dist([coords[2]],[coords[4]])
    norm_coords = [(coord - neck) for coord in coords]
    return norm_coords

def normalize_to_camera(coords, crop_coord):
    if sum(crop_coord) <= 0:
        rescale_factor = (640/256.0, 480/256.0)
    else:
        rescale_factor = ((crop_coord[1]-crop_coord[0])/256.0, (crop_coord[3]-crop_coord[2])/256.0)

    norm_coords = [np.array((coord[0]*rescale_factor[0] + crop_coord[0], coord[1]*rescale_factor[1] + crop_coord[2])) for coord in coords]
    return np.array(norm_coords)

def filter_confidence(coords, confidence, thresh=0.25):
    for j in xrange(confidence.shape[1]):
        for i in xrange(len(coords)):
            if confidence[i][j]<thresh:
                coords[i][j] = (-1000,-1000)
    return coords

def optical_flow_mvmt(frame, prev_frame, pose_pos):
   
    frame_tmp = np.zeros(shape=(640,480), dtype=np.uint8)
    frame_tmp[:frame.shape[0], :frame.shape[1]]=frame
    frame = frame_tmp
    frame_tmp = np.zeros(shape=(640,480), dtype=np.uint8)
    frame_tmp[:prev_frame.shape[0], :prev_frame.shape[1]]=prev_frame
    prev_frame = frame_tmp

    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 200,
                       qualityLevel = 0.05,
                       minDistance = 7,
                       blockSize = 7 )

    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
   
    p0 = cv2.goodFeaturesToTrack(frame, mask = None, **feature_params)
   
    # calculate optical flow 
    try:
         p1, st, err = cv2.calcOpticalFlowPyrLK(prev_frame, frame, p0, None, **lk_params)
    except:
         pdb.set_trace()

    optical_pos = []
    p0 = np.array([p[0] for p in p0])
    p1 = np.array([p[0] for p in p1])
    for pos in pose_pos:

        point_dist = np.array([np.abs(pos[0]-p[0]) + np.abs(pos[1]-p[1]) for p in p0])

        nearby_points = np.where(point_dist < 30)[0]
        if len(nearby_points)==0:
             optical_pos.append(pos)
        else:
             optical_pos.append(pos + np.median(p1[nearby_points]-p0[nearby_points], axis=0))
    return optical_pos

def my_savgol_filter(xy, win_size, order, axis=0):
    
    for j in xrange(7):
        flag = 0
        last_valid = 0
        for i in xrange(len(xy)):
            if xy[i,j,0]<0 and xy[i,j,1]<0 and flag==0:
                if (i-last_valid)>5:
                    cur_win_size=min(win_size, i-last_valid + 1-(i-last_valid)%2)
                    xy[j,last_valid:i]=savgol_filter(xy[j,last_valid:i], cur_win_size, order, axis)
                flag=1
            elif xy[i,j,0]>0 and xy[i,j,1]>0 and flag==1:
                last_valid=i
                flag=0
    return xy

def main(joints_file, save_folder, crop_coord):
    filename = "_".join(os.path.basename(joints_file).split('.')[0].split("_")[:3])
    try:
        crop_coords = np.array([np.array([int(coord) for coord in crop_coord.split(',')]) for crop_coord in open(os.path.normpath("%s/%s.txt" % (crop_coord, filename))).readlines()])
    except IOError:
        print "Crop coords for %s not found" % (filename)
        return

    print "Processing %s" % (filename)
    poses = np.array([numerate_coords(row) for row in (open(joints_file)).readlines()])

    poses_normalized = np.array([normalize_to_camera(row, crop_coord) for row, crop_coord in zip(poses, crop_coords)])
    poses_normalized = filter_confidence(poses_normalized, poses[:,:,2])
    poses_normalized = my_savgol_filter(poses_normalized, 25, 3, axis=0)
    #pdb.set_trace()

    movement = []
    movement_vectors = []

    for r in xrange(len(poses_normalized)-1):

        movement.append(calc_dist(poses_normalized[r], poses_normalized[r+1]))
        movement_vectors.append(calc_dist_vectors(poses_normalized[r], poses_normalized[r+1]))
    #pdb.set_trace()
    movement = np.array(movement)
    pickle.dump(np.array(movement), open(os.path.normpath('%s/%s_movement.p' % (save_folder, filename)), "wb"))
    #Stich pose results into one video
    f, axes = plt.subplots(7, 1, sharex='col', figsize=(7, 9))
    plt.title("Joint movement over time for file %s" % (filename))

    for i in xrange(7):
        axes[i].plot(np.array(range(len(movement)))/30.0, movement[:,i])
        axes[i].set_title(joint_map[i])
        axes[i].set_ylim([0,3])
    axes[-1].set_xlabel('seconds')
    axes[3].set_ylabel('Normalized distance')

    plt.tight_layout()
    plt.savefig(os.path.normpath('%s/movement_fig_%s.png') % (save_folder, filename))
    plt.close()
    plt.clf()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--crop', required=True, help="Directory of crop coords")
    parser.add_argument('-d', '--dir', required=True, help="Joint coordinate directory")
    parser.add_argument('-s', '--save', required=True, help="Save directory" )
    args = parser.parse_args()
    for file in glob.glob(os.path.join(args.dir,"*.txt")):
        main(file, args.save, args.crop)
