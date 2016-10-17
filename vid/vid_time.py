from pyESig.vid.my_video_capture import my_video_capture
import glob
import json
import os
import csv
from datetime import time, datetime, timedelta
import re
import subprocess
import pdb
import cPickle as pickle
from pyESig2.vid.vid_start_end import get_disconnected_times

def get_len(filename):
    
   result = subprocess.Popen(["ffprobe", filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
   return float(json.loads(result.stdout.read())['streams'][0]['duration'])

def check_disconnect(cur_time, vid_len, start):
    disconnections = []
    for i, t in enumerate(start):
        if (t>=cur_time and t<=(cur_time + vid_len)):
            disconnections.append(i)

    return disconnections
            

def main():
   root_folder = "D:\\NancyStudyData\\ecog\\raw\\"
   sbj_ids = ['a86a4375', 'be66b17c', 'cb46fd46', 'da3971ee', 'fcb01f7a']
   days = ['3','4','5','6','7','8','9','10']
   sbj_ids = ['a86a4375']
   days = ['2']
   save_folder = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"

   for sbj_id in sbj_ids:
       for day in days:
            result = []
            start_time, end_time, start, end = get_disconnected_times("C:\\Users\\wangnxr\\Documents" + \
                               "\\rao_lab\\video_analysis\\disconnect_times\\" \
                               + sbj_id + "_" + str(day) + ".txt")
           
            vid_count = 0
            cur_time = start_time
            vid_name = root_folder + sbj_id + "\\" + sbj_id + "_" + day + \
                            "\\" + sbj_id + "_" + day + "_" + str(vid_count).zfill(4) + ".avi"
            with open(save_folder + sbj_id + "_" + day + ".csv", "wb") as csvfile:
               timewriter = csv.writer(csvfile)
               while os.path.exists(vid_name):
                   pos = check_disconnect(cur_time, timedelta(seconds = 1), start)
                   for t in pos:
                       cur_time += end[t] - start[t] - timedelta(seconds = 0.5)
                   timewriter.writerow([str(vid_count), cur_time.year, cur_time.month,
                                        cur_time.day, cur_time.hour, cur_time.minute, cur_time.second])
                   result.append([vid_count, cur_time])
                   vid_len = timedelta(seconds = get_len(root_folder + sbj_id + "\\" + sbj_id + "_" + day +
                                    "\\" + sbj_id + "_" + day + "_" + str(vid_count).zfill(4) + ".avi"))
                   
                   pos = check_disconnect(cur_time, vid_len, start)
                   cur_time += vid_len
                   for t in pos:
                       cur_time += end[t] - start[t] - timedelta(seconds = 0.5)
                   vid_count += 1
                   vid_name = root_folder + sbj_id + "\\" + sbj_id + "_" + day + \
                              "\\" + sbj_id + "_" + day + "_" + str(vid_count).zfill(4) + ".avi"
                   
            pickle.dump(result, open(save_folder + sbj_id + "_" + day + ".p", "wb"))
            
if __name__ == "__main__":
   main()
