import numpy as np
import csv
import argparse
import matplotlib.pyplot as plt
import pickle
import pdb
import cv2

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

def normalize_to_camera(coords, crop_coords):
    coords = numerate_coords(coords)
    norm_coords_tmp = [(coord[0] + crop_coords[1]) for coord in coords]
    norm_coords = [(coord[1] + crop_coords[0]) for coord in norm_coords_tmp]
    return norm_coords

def optical_flow_mvmt(frame, prev_frame, pose_pos):
    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    p0 = cv2.goodFeaturesToTrack(frame, mask = None, **feature_params)

    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(prev_frame, frame, p0, None, **lk_params)
    optical_pos = []
    for pos in pose_pos:
        point_dist = np.array([np.sum(np.abs(pos-p)) for p in p0])
        nearby_points = np.where(point_dist < 10)[0]
        optical_pos.append(np.mean(p1[nearby_points]))
    return optical_pos


def main(args):
    prev_poses = [normalize_to_camera(row) for row in csv.reader(open(args.file)).readlines()]
    for itr in xrange(10):
        movement = []
        new_poses = []

        prev_data = prev_poses[0]
        prev_frame = cv2.cvtColor(cv2.imread("%s/%05i.png" % (args.datadir, 0)))
        for r, row in enumerate(prev_poses[1:]):
            frame = cv2.cvtColor(cv2.imread("%s/%05i.png" % (args.datadir, r)))
            cur_data = normalize_to_camera(row)
            opt_poses = optical_flow_mvmt(frame, prev_frame, cur_data)
            movement.append(calc_dist(prev_data, cur_data))
            new_poses.append([[np.mean([cur_pose, opt_pose]) for cur_pose, opt_pose in zip(cur_poses, opt_poses)] for cur_poses in cur_data])
            prev_data = cur_data

        movement = np.array(movement)
        pickle.dump(movement, open('%s/movement_%i.p' % (args.save, itr), "wb"))
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
