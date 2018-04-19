import pandas
import numpy as np
from vid.video_sync.vid_start_end import get_disconnected_times
from movement.joint_movement_norm import normalize_to_camera
from datetime import datetime
from datetime import timedelta
import cPickle as pickle
import pdb
import os

sbj_id = "d6532718"
conversion_file = "C:/Users/Nancy/OneDrive - UW/Documents/Documents/brunton_lab/data_release/%s.csv" % sbj_id
mvmt_dir = "C:/Users/Nancy/Downloads/"
save_dir = "C:/Users/Nancy/Downloads/"
vid_start_ends_dir = "C:/Users/Nancy/OneDrive - UW/Documents/Documents/rao_lab/video_analysis/vid_real_time/"

def vid_to_time(vid_num, frame_num, vid_start_ends, conversion):
    time = vid_start_ends["start"][vid_num] + timedelta(seconds=frame_num*1/30.0)
    date = "%i/%i/%i" % (time.month, time.day, time.year)
    try:
        day = int(conversion[conversion["date"]==date]["day"])
    except:
        pdb.set_trace()
    return day, print_time(time)

def print_time(time):
    return "%02i:%02i:%02i.%06i" % (time.hour, time.minute, time.second, time.microsecond)

conversion = pandas.read_csv(conversion_file)
mvmt_files_tmp = []
with open("%s/%s_files.txt" % (mvmt_dir, sbj_id[:3])) as mvmt_file_raw:
    for mvmt_file in mvmt_file_raw:
        _, _, type, mvmt, filename = mvmt_file.split("/")
        _, file_num, vid_num, _, frame_num = filename.split(".")[0].split("_")
        mvmt_files_tmp.append(pandas.DataFrame([[type, mvmt, int(file_num), int(vid_num), int(frame_num)]], columns=["type", "mvmt", "file_num", "vid_num", "frame_num"]))
mvmt_files = pandas.concat(mvmt_files_tmp)

types = ["train", "test", "val"]
result = []
for type in types:
    for file_num in xrange(12):
        if os.path.exists("%s/%s_%i.p" % (vid_start_ends_dir, sbj_id, file_num)):
            vid_start_end = pickle.load(open("%s/%s_%i.p" % (vid_start_ends_dir, sbj_id, file_num)))
            for _, file in mvmt_files[(mvmt_files["type"]==type) & (mvmt_files["file_num"]==file_num)].iterrows():
                day, time = vid_to_time(int(file["vid_num"]), int(file["frame_num"]), vid_start_end, conversion)
                result.append(pandas.DataFrame([[file["type"], file["mvmt"], day, time]], columns=["type", "mvmt", "day", "time"]))
result_final = pandas.concat(result, ignore_index=True)
result_final.to_csv("%s/%s_mvmt_initiation.csv" % (save_dir, sbj_id))