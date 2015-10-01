import subprocess
import pandas as pd
import sys
from util.error import varError
import pdb
import numpy as np
import cPickle as pickle
import datetime, time
import re
import random.random

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


def convert_labels_to_array(labels, sbj_indexes, vid_length, tracks, pretty_tracks):

    labels_array=np.zeros(shape=(len(tracks), int(round(vid_length))))
    for t in sbj_indexes:
        track = labels.track[t]
        ind = tracks.index(track)
        start = int(round(float(labels.start[t])))
        end = int(round(float(labels.end[t])))
        labels_array[ind,start:end] = 1
    #add rest track
    labels_array[-1,:] = 1
    for track in xrange(len(tracks)-1):
        labels_array[-1,:] *= (1-labels_array[track])

    return {'tracks':tracks, 'pretty_tracks': pretty_tracks, 'labels_array': labels_array}

def convert_reduced_labels_to_array(labels, sbj_indexes, vid_length, tracks, reduced_tracks):
    track_conversion=[2,0,0,0,2,4,3,4,1,1,1,3]
    labels_array=np.zeros(shape=(len(reduced_tracks), int(round(vid_length))))
    for t in sbj_indexes:
        track = labels.track[t]
        ind = track_conversion[tracks.index(track)]
        start = int(round(float(labels.start[t])))
        end = int(round(float(labels.end[t])))
        labels_array[ind,start:end] = 1

    return {'tracks':reduced_tracks, 'all_tracks': tracks, 'pretty_tracks': reduced_tracks, 'labels_array': labels_array}

def convert_random_labels_to_array(labels, sbj_indexes, vid_length, tracks, reduced_tracks):
    track_conversion=[2,0,0,0,2,4,3,4,1,1,1,3]
    labels_array=np.zeros(shape=(len(reduced_tracks), int(round(vid_length))))
    for t in sbj_indexes:
        track = labels.track[t]
        ind = track_conversion[tracks.index(track)]
        start = int(round(float(labels.start[t])))
        end = int(round(float(labels.end[t])))
        dur = end-start
        rand_start = random.randint(0,len(labels_array)-dur)
        while labels_array[ind,rand_start:rand_start+dur].sum()>0:
            rand_start = random.randint(0,len(labels_array)-dur)
        labels_array[ind,rand_start:rand_start+dur] = 1
    return {'tracks':reduced_tracks, 'all_tracks': tracks, 'pretty_tracks': reduced_tracks, 'labels_array': labels_array}

def extract_all_labels(sbj_id, day, src_folder, vid_folder, dst_folder):
    labels=pd.read_csv(src_folder + sbj_id + "_" + day + ".txt", sep=':')

    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    pretty_tracks = ["Laugh", "Head_mv", "Other_mv",
              "Arm_mv", "Speak", "Mult_ppl",
              "Sleep","Eat", "Watch",
              "Listen_fam",
              "Listen_staff", "Rest"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.hstack([np.where(np.array(labels.filename)== file_num)[0],
                       np.where(np.array(labels.filename)== file_num + '-rs')[0]])

        if sbj_indexes.shape[0]>0:

            vid_length = getLength(vid_folder + "\\"  + sbj_id
                                          + "_" + day + "\\" + sbj_id
                                          + "_" + day + "_" + file_num + ".avi")
            result = convert_labels_to_array(labels,sbj_indexes, vid_length, tracks, pretty_tracks)

            pickle.dump(result, open(dst_folder + "\\" + sbj_id +"_" + day + "_" + file_num + ".p", "wb"))

def extract_reduced_labels(sbj_id, day, src_folder, vid_folder, dst_folder):
    labels=pd.read_csv(src_folder + sbj_id + "_" + day + ".txt", sep=':')

    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    tracks_reduced = ["Mvmt", "Sound", "Rest", "Other"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.hstack([np.where(np.array(labels.filename)== file_num)[0],
                       np.where(np.array(labels.filename)== file_num + '-sk')[0]])

        if sbj_indexes.shape[0]>0:

            vid_length = getLength(vid_folder + "\\"  + sbj_id
                                          + "_" + day + "\\" + sbj_id
                                          + "_" + day + "_" + file_num + ".avi")
            result = convert_reduced_labels_to_array(labels,sbj_indexes, vid_length, tracks, tracks_reduced)
            pickle.dump(result, open(dst_folder +  "\\" + sbj_id +"_" + day + "_" + file_num + ".p", "wb"))

def extract_random_labels(sbj_id, day, src_folder, vid_folder, dst_folder):
    labels=pd.read_csv(src_folder + sbj_id + "_" + day + ".txt", sep=':')

    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    tracks_reduced = ["Mvmt", "Sound", "Rest", "Other"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.hstack([np.where(np.array(labels.filename)== file_num)[0],
                       np.where(np.array(labels.filename)== file_num + '-sk')[0]])

        if sbj_indexes.shape[0]>0:

            vid_length = getLength(vid_folder + "\\"  + sbj_id
                                          + "_" + day + "\\" + sbj_id
                                          + "_" + day + "_" + file_num + ".avi")
            result = convert_random_labels_to_array(labels,sbj_indexes, vid_length, tracks, tracks_reduced)
            pickle.dump(result, open(dst_folder +  "\\" + sbj_id +"_" + day + "_" + file_num + ".p", "wb"))

if __name__ == "__main__":
    if not(len(sys.argv) == 7):
        raise varError("Arguments should be <Subject ID> <Day><Label File>\
                         <Video directory> <Save directory>")
    extract_random_labels(*sys.argv[1:])
