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
import numpy as np

def get_len(filename):
    
   result = subprocess.Popen(["ffprobe", filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
   return float(json.loads(result.stdout.read())['streams'][0]['duration'])

def get_disconnected_times(disconnect_file_loc):
    disconnect_info = open(disconnect_file_loc, "rb")
    start = []
    end = []
    start_line = disconnect_info.readline()
    end_line = disconnect_info.readline()
    
    match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', start_line)
    start_time = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S')
    match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', end_line)
    end_time = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S')

    disconnect_info.readline()
    for line in disconnect_info:
        
        match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', line)
        match2 = re.search(r' \d{2}:\d{2}:\d{2}\r\n', line)
        

        start.append(datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S'))
        end.append(datetime.strptime(match.group()[:11] + match2.group()[1:-2], '%m-%d-%Y %H:%M:%S'))

    return start_time, end_time, start, end

def check_disconnect(cur_time, vid_len, start):
    disconnections = []
    for i, t in enumerate(start):
        if (t>=cur_time and t<=(cur_time + vid_len)):
            disconnections.append(i)

    return disconnections
            

def main():
   root_folder = "D:\\NancyStudyData\\ecog\\raw\\"
   sbj_ids = ['a86a4375', 'be66b17c', 'cb46fd46', 'da3971ee', 'fcb01f7a']
   sbj_ids = ['c95c1e82']
   sbj_ids = ["d6532718", "cb46fd46" ]
   sbj_ids = ["d6532718" ]
   days = ['8']
   save_folder = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"

   for sbj_id in sbj_ids:
       for day in days:
            disconnect_file= "C:\\Users\\wangnxr\\Documents" + \
                               "\\rao_lab\\video_analysis\\disconnect_times\\" \
                               + sbj_id + "_" + str(day) + ".txt"
            if os.path.isfile(disconnect_file):
                print disconnect_file
                start_time, end_time, start, end = get_disconnected_times(disconnect_file)
                vid_count = 0
                cur_time = start_time
                vid_name = root_folder + sbj_id + "\\" + sbj_id + "_" + day + \
                                "\\" + sbj_id + "_" + day + "_" + str(vid_count).zfill(4) + ".avi"
                with open(save_folder + sbj_id + "_" + day + ".csv", "wb") as csvfile:

                   timewriter = csv.writer(csvfile)
                   pos = check_disconnect(cur_time, timedelta(seconds = 1), start)
                   for t in pos:
                       cur_time += end[t] - start[t] - timedelta(seconds = 0.5)
                   video_start_times = []
                   video_end_times = []
                   while os.path.exists(vid_name):
                       timewriter.writerow([vid_name, cur_time.year, cur_time.month,
                                            cur_time.day, cur_time.hour, cur_time.minute, cur_time.second])
                       video_start_times.append(cur_time)
                       vid_len = timedelta(seconds = get_len(root_folder + sbj_id + "\\" + sbj_id + "_" + day +
                                        "\\" + sbj_id + "_" + day + "_" + str(vid_count).zfill(4) + ".avi"))

                       pos = check_disconnect(cur_time, vid_len, start)
                       cur_time += vid_len
                       video_end_times.append(cur_time)
                       for t in pos:
                           cur_time += end[t] - start[t] - timedelta(seconds = 0.5)

                       vid_count += 1
                       vid_name = root_folder + sbj_id + "\\" + sbj_id + "_" + day + \
                                  "\\" + sbj_id + "_" + day + "_" + str(vid_count).zfill(4) + ".avi"
                   result = {"start": np.array(video_start_times), "end": np.array(video_end_times)}
                pickle.dump(result, open(save_folder + sbj_id + "_" + day + ".p", "wb"))
            
if __name__ == "__main__":
   main()
