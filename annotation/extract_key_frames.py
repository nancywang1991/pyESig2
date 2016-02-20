## Online toolboxes
import os
import sys
import subprocess
import pdb

def main_scpt(video_path, save_loc):
    parent, child = os.path.split(video_path)
    if not os.path.isfile(save_loc + "\\" + child.split(".")[0] + ".jpg"):
        subprocess.call("ffmpeg -i " + video_path + " -f image2 -ss 1 " + \
                        save_loc + "\\" + child.split(".")[0] + ".jpg", shell=True)


if __name__=='__main__':
        if not(len(sys.argv)==3):
                 print "Arguments should be <data folder> <result folder> "

        file_loc = os.path.normpath(sys.argv[1])
        save_loc = os.path.normpath(sys.argv[2])
##        vids = [x for x in os.listdir(file_loc) if (x[-3:]=="avi") ]
        if not os.path.isdir(save_loc):
            os.makedirs(save_loc)
        for dir in os.listdir(file_loc):
            if os.path.isdir(file_loc + "\\" + dir):
                for f in os.listdir(file_loc + "\\" + dir):
                    if f.split(".")[1] == "avi":
                        main_scpt(file_loc + "\\" + dir + "\\" + f, save_loc)





