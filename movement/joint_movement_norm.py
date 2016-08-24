import numpy as np
import csv
import argparse
import matplotlib.pyplot as plt
import pickle
import pdb

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
    #neck = np.mean([coords[2], coords[4]])
    #shoulder_length = calc_dist([coords[2]],[coords[4]])
    #norm_coords = [(coord - neck) for coord in coords]
    return coords

def main(args):
    movement = []
    with open(args.file) as csvfile:
        reader = csv.reader(csvfile)

        prev_data = normalize_to_neck(reader.next())
        for row in reader:
            cur_data = normalize_to_neck(row)
            movement.append(calc_dist(prev_data, cur_data))
            prev_data = cur_data

    movement = np.array(movement)
    pickle.dump(movement, open('%s/movement.p' % args.save, "wb"))
    f, axes = plt.subplots(7, 1, sharex='col', figsize=(7, 9))
    plt.title("Joint movement over time for file %s" % args.file.split('/')[-1].split('.')[0])

    for i in xrange(7):
        axes[i].plot(np.array(range(len(movement)))/30.0, movement[:,i])
        axes[i].set_title(joint_map[i])
        axes[i].set_ylim([0,60])
    axes[-1].set_xlabel('seconds')
    axes[3].set_ylabel('Normalized distance')

    plt.tight_layout()

    plt.savefig('%s/movement_fig.png' % args.save)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help="Filename")
    parser.add_argument('-s', '--save', required=True, help="Save directory" )
    args = parser.parse_args()
    main(args)
