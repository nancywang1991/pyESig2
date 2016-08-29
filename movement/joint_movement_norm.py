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
from test_flic_dataset import draw_joints
import os
import subprocess

joint_map = ['left hand', 'left elbow', 'left shoulder', 'head', 'right shoulder', 'right elbow', 'right hand']

def calc_dist(a,b):
    final_dist = []
    for i, coord in enumerate(a):
        final_dist.append(np.sqrt((coord[0]-b[i][0])**2 + (coord[1]-b[i][1])**2))
    return final_dist

def numerate_coords(coords):
    final_coords = []
    for coord in coords:
        x = int(coord.split('(')[-1].split(',')[0])
        y = int(coord.split(')')[0].split(',')[-1])
        final_coords.append((x,y))
    return final_coords

def normalize_to_neck(coords):
    coords = numerate_coords(coords)
    neck = np.mean([coords[2], coords[4]])
    #shoulder_length = calc_dist([coords[2]],[coords[4]])
    norm_coords = [(coord - neck) for coord in coords]
    return norm_coords

def normalize_to_camera(coords, crop_coord):

    norm_coords = [(coord[0] + crop_coord[0], coord[1] + crop_coord[1]) for coord in coords]
    
    return norm_coords

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
             optical_pos.append(pos + np.mean(p1[nearby_points]-p0[nearby_points], axis=0))
    return optical_pos


def main(args):

    crop_coords = [(int(crop_coord.split(',')[0]),int(crop_coord.split(',')[2])) for crop_coord in open("%s/cropped/crop_coords.txt" % args.save).readlines()]   

    prev_poses = [numerate_coords(row) for row in csv.reader(open(args.file))]
    for itr in xrange(3):
        prev_poses_normalized = [normalize_to_camera(row, crop_coord) for row, crop_coord in zip(prev_poses, crop_coords)]
        movement = []
        new_poses = []
        prev_data = prev_poses[0]
        prev_frame = cv2.cvtColor(cv2.resize(cv2.imread("%s/%05i.png" % (args.datadir, 1)), (220,220)),  cv2.COLOR_BGR2GRAY)
        if not os.path.exists('%s/poses_%i/' % (args.save, itr)):
            os.makedirs('%s/poses_%i/' % (args.save, itr))
        pdb.set_trace()
        for r, row in enumerate(prev_poses[1:]):
            img_pred = cv2.resize(cv2.imread("%s/%05i.png" % (args.datadir, r+1)), (220,220))
            img_pred = draw_joints(img_pred, row, True, 1)
            cv2.imwrite('%s/poses_%i/%05i.png' % (args.save, itr, r+1), img_pred)
            print r
            frame = cv2.cvtColor(cv2.resize(cv2.imread("%s/%05i.png" % (args.datadir, r+2)), (220,220)),  cv2.COLOR_BGR2GRAY)
            opt_poses = optical_flow_mvmt(frame, prev_frame, row)
            movement.append(calc_dist(prev_data, prev_poses_normalized[r+1]))
            new_poses.append([tuple(np.int(np.round(np.mean([cur_pose, opt_pose], axis=0)))) for cur_pose, opt_pose in zip(row, opt_poses)])
            prev_data = prev_poses[r+1]

        movement = np.array(movement)
        pickle.dump(movement, open('%s/movement_%i.p' % (args.save, itr), "wb"))
        #Stich pose results into one video
        subprocess.call('ffmpeg -r 30 -i %s/poses_%i/' %(args.save, itr) + '%05d.png -c:v libx264 '
                       + '-pix_fmt yuv420p %s/poses_itr_%i.avi' % (args.save, itr), shell=True)
        f, axes = plt.subplots(7, 1, sharex='col', figsize=(7, 9))
        plt.title("Joint movement over time for file %s in iteration %i" % (args.file.split('/')[-1].split('.')[0], itr))

        for i in xrange(7):
            axes[i].plot(np.array(range(len(movement)))/30.0, movement[:,i])
            axes[i].set_title(joint_map[i])
            axes[i].set_ylim([0,60])
        axes[-1].set_xlabel('seconds')
        axes[3].set_ylabel('Normalized distance')

        plt.tight_layout()
        plt.savefig('%s/movement_fig_%i.png' % (args.save, itr))
        prev_poses = new_poses
        pickle.dump(prev_poses, open('%s/adjusted_poses_%i.p' % (args.save, itr), "wb"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help="Filename")
    parser.add_argument('-s', '--save', required=True, help="Save directory" )
    parser.add_argument('-d', '--datadir', required=True, help="Video frame directory" )
    args = parser.parse_args()
    main(args)
