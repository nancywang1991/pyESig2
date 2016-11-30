import argparse
import glob
import subprocess
import os

def main(dir):
    if not os.path.exists(dir + "\\converted"):
        os.makedirs(dir + "\\converted")
    for file in glob.glob(dir + "\*.avi"):
        subprocess.call("ffmpeg -i %s -c:v h263 -c:a copy -vf scale=352:288 %s" % (file, dir + "\\converted\\" + file.split(".")[0].split("\\")[-1] + ".mov"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vid_folder', default="E:\\", help="Video directory")
    args = parser.parse_args()
    main(args.vid_folder)