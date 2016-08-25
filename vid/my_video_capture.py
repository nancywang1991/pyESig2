import subprocess
from sys import platform as _platform
import glob
import cv2
import os
import pdb
import shutil

if _platform == "linux" or _platform == "linux2":
    slash = "/"
elif _platform == "win32":
    slash = "\\"
    
class my_video_capture:
    def __init__(self, file_loc, frame_rate, mode="read"):
        self.file_loc = file_loc
        self.mode = mode
        self.frame_rate = frame_rate
        if mode=="write":
            self.vid_dir=file_loc
            if os.path.exists(self.vid_dir + slash + "tmp_" + mode):
                shutil.rmtree(self.vid_dir + slash + "tmp_" + mode)
            os.makedirs(self.vid_dir + slash + "tmp_" + mode)
        if mode=="read":
            self.vid_dir, self.vid_loc = os.path.split(file_loc)
            if os.path.exists(self.vid_dir + slash + "tmp_" + mode):
                shutil.rmtree(self.vid_dir + slash + "tmp_" + mode)
            os.makedirs(self.vid_dir + slash + "tmp_" + mode)
            subprocess.call("ffmpeg -i " + file_loc + " -f image2 -r " + \
                        str(frame_rate) + " " + self.vid_dir + slash + \
                        "tmp_" + self.mode + slash + "%05d.png", shell=True)
            self.total_frames = len(glob.glob(self.vid_dir + slash + "tmp_" + self.mode + slash + "*"))

        self.frame_num = 1
        self.isOpen = 1

    def get_total_frames(self):
        return self.total_frames

    def has_next(self):
        return self.frame_num<self.total_frames
    
    def read(self):
        img = cv2.imread(self.vid_dir + slash + "tmp_" + self.mode + slash + str(self.frame_num).zfill(5) + ".png")
        self.frame_num += 1
        return img

    def write(self, img):
        cv2.imwrite(self.vid_dir + slash + "tmp_" + self.mode + slash + str(self.frame_num).zfill(5) + ".png", img)
        self.frame_num += 1
    
    def rewind(self):
        self.frame_num = 1

    def rewind_to(self, frame_num):
        self.frame_num = frame_num

    def forward_to(self, frame_num):
        self.frame_num = frame_num

    def close(self):
        self.isOpen = 0
        shutil.rmtree(self.vid_dir + slash + "tmp_" + self.mode)
        self.frame_num = 1

    def new_vid(self, dst):
        subprocess.call("ffmpeg -start_number 1 -r " + str(self.frame_rate) + " -i " + self.vid_dir + slash + \
                        "tmp_" + self.mode + slash + "%05d.png -vcodec mpeg4 " + dst, shell=True)

    def new_img_folder(self, dst):
        for file in glob.glob(self.vid_dir + slash + "tmp_" + self.mode + slash + "*"):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(file, dst)
