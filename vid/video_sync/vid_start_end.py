import json
import os
import csv
from datetime import time, datetime, timedelta
import re
import subprocess
import cPickle as pickle
import numpy as np
import argparse
import pdb
import glob

def get_len(filename):

    result = subprocess.Popen(["ffprobe", filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
                              stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    result = json.loads(result.stdout.read())
    #print result['streams'][0]
    #pdb.set_trace()
    return float(result['streams'][0]['duration'])

def get_disconnected_times(disconnect_file_loc):
    disconnect_info = open(disconnect_file_loc, "rb")
    start = []
    end = []
    start_line = disconnect_info.readline()
    end_line = disconnect_info.readline()

    match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}:\d{3}', start_line)
    start_time = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S:%f')
    match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}:\d{3}', end_line)
    end_time = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S:%f')

    disconnect_info.readline()
    for line in disconnect_info:

        match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}:\d{3}', line)
        match2 = re.search(r' \d{2}:\d{2}:\d{2}:\d{3}\r\n', line)

        start.append(datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S:%f'))
        end.append(datetime.strptime(match.group()[:11] + match2.group()[1:-2], '%m-%d-%Y %H:%M:%S:%f'))

    return start_time, end_time, start, end

def check_disconnect(cur_time, vid_len, start):
    disconnections = []
    for i, t in enumerate(start):
        if (t>=cur_time and t<=(cur_time + vid_len)):
            disconnections.append(i)

    return disconnections


def main(vid_folder, save_folder, disconnect_fldr, sbj_ids, days, vid_offset=0.000024):
    for sbj_id in sbj_ids:
        for day in days:
            disconnect_file= os.path.normpath("%s/%s_%s.txt" %(disconnect_fldr, sbj_id, day))
            if os.path.isfile(disconnect_file):
                print disconnect_file
                start_time, end_time, start, end = get_disconnected_times(disconnect_file)
                vid_count = 0
                cur_time = start_time

                vid_name = glob.glob(os.path.normpath("%s/%s/%s_%s/*_%04i.avi" %(vid_folder, sbj_id, sbj_id, day, vid_count)))[0]
                vid_de_id_name = "%s_%s_%04i.avi" % (sbj_id, day, vid_count)
                with open(os.path.normpath("%s/%s_%s.csv" %(save_folder, sbj_id, day)), "wb") as csvfile:
                    timewriter = csv.writer(csvfile)
                    pos = check_disconnect(cur_time, timedelta(seconds = 1), start)
                    for t in pos:
                        cur_time += end[t] - start[t]
                    video_start_times = []
                    video_end_times = []
                    while os.path.exists(vid_name):
                        #pdb.set_trace()
                        vid_len = timedelta(seconds = get_len(vid_name))
                        vid_len -= timedelta(seconds=vid_offset*vid_len.total_seconds())
                        if vid_len > timedelta(seconds=2):
                            pos = check_disconnect(cur_time, timedelta(seconds = 2), start)
                            for t in pos:
                                cur_time += end[t] - start[t]

                        timewriter.writerow([vid_de_id_name, cur_time.year, cur_time.month,
                                             cur_time.day, cur_time.hour, cur_time.minute, cur_time.second, cur_time.microsecond])

                        video_start_times.append(cur_time)
                        if vid_len > timedelta(seconds=2):
                            pos = check_disconnect(cur_time + timedelta(seconds = 2), vid_len- timedelta(seconds = 2), start)
                        else:
                            pos = check_disconnect(cur_time , vid_len, start)
                        cur_time += vid_len
                        for t in pos:
                            cur_time += end[t] - start[t]

                        video_end_times.append(cur_time)
                        vid_count += 1
                        try:
                            vid_name = glob.glob(os.path.normpath("%s/%s/%s_%s/*_%04i.avi" % (vid_folder, sbj_id, sbj_id, day, vid_count)))[0]
                            vid_de_id_name = "%s_%s_%04i.avi" % (sbj_id, day, vid_count)
                        except IndexError:
                            break
                    pos = check_disconnect(cur_time, timedelta(seconds = 1), start)
                    for t in pos:
                        cur_time += end[t] - start[t]
                    result = {"start": np.array(video_start_times), "end": np.array(video_end_times)}
                print result["end"][-1] - end_time
                pickle.dump(result, open(os.path.normpath("%s/%s_%s.p" %(save_folder, sbj_id, day)), "wb"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--disc_fldr', default = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\disconnect_times\\", help="Disconnect folder")
    parser.add_argument('-s', '--save', default = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\", help="Save directory" )
    parser.add_argument('-v', '--vid_folder', default = "E:\\", help="Video directory" )
    parser.add_argument('-sbj', '--sbj_id', required=True, help="Subject id", type=str, nargs='+')
    parser.add_argument('-d', '--days', required=True, help="Day of study", type=str, nargs='+')
    args = parser.parse_args()
    main(args.vid_folder, args.save, args.disc_fldr, args.sbj_id, args.days)
