import argparse
import pdb
import glob
import os
import shutil
import subprocess
import numpy as np

def main(dir, test_day):
    if not os.path.exists("%s/test/" % dir ):
        os.makedirs("%s/test/" % dir )
    if not os.path.exists("%s/val/" % dir):
        os.makedirs("%s/val/" % dir)
    # Make testset
    for subdir in os.listdir(dir + "/train/"):
        if len(glob.glob("%s/train/%s/*" % (dir, subdir))) == 0:
            os.removedirs("%s/train/%s/*" % (dir, subdir))
        else:
            if not os.path.exists("%s/test/%s" % (dir, subdir)):
                os.makedirs("%s/test/%s" %  (dir, subdir))
            subprocess.call("mv %s/train/%s/*_%i_* %s/test/%s/" % (dir, subdir, test_day, dir, subdir), shell=True)

            if not os.path.exists("%s/val/%s" % (dir, subdir)):
                os.makedirs("%s/val/%s" % (dir, subdir))
            subprocess.call("mv %s/train/%s/*_*_*[5-9]9_ %s/val/%s/" % (dir, subdir, test_day, dir, subdir), shell=True)
    # Balance test set
    min_set_size = min([len(glob.glob("%s/test/%s/*" % (dir,subdir))) for subdir in os.listdir(dir + "/test/")])
    for subdir in os.listdir(dir + "/test/"):
        to_remove = len(glob.glob("%s/test/%s/*" % (dir,subdir))) - min_set_size
        to_remove_list = np.random.shuffle(glob.glob("%s/test/%s/*" % (dir,subdir)))[:to_remove]
        for file in to_remove_list:
            os.remove(file)
    # Balance val set
    min_set_size = min([len(glob.glob("%s/val/%s/*" % (dir, subdir))) for subdir in os.listdir(dir + "/val/")])
    for subdir in os.listdir(dir + "/val/"):
        to_remove = len(glob.glob("%s/val/%s/*" % (dir, subdir))) - min_set_size
        to_remove_list = np.random.shuffle(glob.glob("%s/val/%s/*" % (dir, subdir)))[:to_remove]
        for file in to_remove_list:
            os.remove(file)
    # Make train set total size be a power of 24
    to_remove = len(glob.glob("%s/train/%s/*" % (dir, subdir)))%24
    to_remove_list = np.random.shuffle(glob.glob("%s/train/mv_0/*" % (dir)))[:to_remove]
    for file in to_remove_list:
        os.remove(file)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--dir', type=str, help = "main directory of files", required=True)
    parser.add_argument('-td', '--test_day', type=int, help="Day set aside for testing", required=True)
    args = parser.parse_args()
    main(args.dir, args.test_day)