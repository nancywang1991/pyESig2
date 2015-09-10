import subprocess
import pandas as pd
import sys
from util.error import varError
import pdb
import numpy as np
import cPickle as pickle
import datetime, time
import re

def getLength(filename):
    result = subprocess.Popen(["ffprobe", filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    duration = [x for x in result.stdout.readlines() if "Duration" in x]
    t = re.search(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',duration[0]).group(0)
    millisecs = int(re.search(r'\.[0-9][0-9],', duration[0]).group(0)[1:3])
    x = time.strptime(t, '%H:%M:%S')
    seconds_raw = datetime.timedelta(hours=x.tm_hour,
                    minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    return seconds_raw + int(round(millisecs/100.0))


def convert_labels_to_array(labels, sbj_indexes, vid_length, tracks):
    for t in sbj_indexes:
        track = labels.track[t]
        labels_array=np.zeros(shape=(11, int(round(vid_length))))
        ind = np.where(tracks == track)[0]
        start = int(round(float(labels.start[t])))
        end = int(round(float(labels.end[t])))
        labels_array[ind,start:end] = 1
    return {'tracks':tracks, 'labels_array': labels_array}

def main(sbj_id, day, src_file, vid_folder, dst_folder):
    labels=pd.read_csv(src_file, sep=':')
    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Speaking", "Multiple People",
              "Sleeping","Eating", "Listening.watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.where(labels.filename==file_num)[0]
        if sbj_indexes.shape[0]>0:
            vid_length = getLength(vid_folder + "\\" + sbj_id
                                          + "_" + day + "_" + file_num + ".avi")
            result = convert_labels_to_array(labels,sbj_indexes, vid_length, tracks)
            pickle.dump(result, open(dst_folder + "\\" + sbj_id +"_" + day + "_" + file_num + ".p", "wb"))


if __name__ == "__main__":
    if not(len(sys.argv) == 6):
        raise varError("Arguments should be <Subject ID> <Day><Label File>\
                         <Video directory> <Save directory>")
    main(*sys.argv[1:])
