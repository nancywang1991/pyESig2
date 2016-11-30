import argparse
import cPickle as pickle
import glob
import os

import numpy as np
import pandas as pd
from vid.video_sync.vid_start_end import get_len


#def getLength(filename):
#    result = subprocess.Popen(["ffprobe", filename],
#        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
#    duration = [x for x in result.stdout.readlines() if "Duration" in x]

#    t = re.search(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',duration[0]).group(0)
#    millisecs = int(re.search(r'\.[0-9][0-9],', duration[0]).group(0)[1:3])
#    x = time.strptime(t, '%H:%M:%S')
#    seconds_raw = datetime.timedelta(hours=x.tm_hour,
#                    minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
#    return seconds_raw + int(round(millisecs/100.0))

def get_len_from_csv(file, vid_num):
    vid_times = pickle.load(open(file))
    return (vid_times["end"][vid_num] - vid_times["start"][vid_num]).total_seconds()

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

def convert_detailed_labels_to_array(labels, sbj_indexes, vid_length, tracks, pretty_tracks):

    labels_array=np.zeros(shape=(len(tracks), int(round(vid_length*30))))
    for t in sbj_indexes:
        track = labels.track[t]
        if track == "Movement.arm":
            if labels.Handedness[t] == "Right":
                ind = 3
            elif labels.Handedness[t] == "Left":
                ind = 4
            else:
                ind = [3,4]
        else:
            ind = tracks.index(track)
        start = int(round(float(labels.start[t])*30))
        end = int(round(float(labels.end[t])*30))
        labels_array[ind,start:end] = 1

    labels_array[-1,:] = 1
    for track in xrange(len(tracks)-1):
        labels_array[-1,:] *= (1-labels_array[track])

    return {'tracks':tracks, 'pretty_tracks': pretty_tracks, 'labels_array': labels_array}

def convert_reduced_labels_to_array(labels, sbj_indexes, vid_length, tracks, reduced_tracks):
    track_conversion=[4,0,0,0,4,3,2,0,1,1,1,2]
    labels_array=np.zeros(shape=(len(reduced_tracks), int(round(vid_length))))
    for t in sbj_indexes:
        track = labels.track[t]
        ind = track_conversion[tracks.index(track)]
        start = int(round(float(labels.start[t])))
        end = int(round(float(labels.end[t])))
        if ind>3:
            labels_array[0,start:end]=1
            labels_array[1,start:end]=1
        else:
            labels_array[ind,start:end] = 1

    return {'tracks':reduced_tracks, 'all_tracks': tracks, 'pretty_tracks': reduced_tracks, 'labels_array': labels_array}

def extract_all_labels(sbj_id, day, src_folder, vid_folder, dst_folder):
    labels=pd.read_csv(src_folder + sbj_id + "_" + str(day) + ".txt", sep=':')

    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    pretty_tracks = ["Laugh", "Head_mv", "Other_mv",
              "Arm_mv_right", "Arm_mv_left" "Speak", "Mult_ppl",
              "Sleep","Eat", "Watch",
              "Listen_fam",
              "Listen_staff", "Rest"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.hstack([np.where(np.array(labels.filename)== file_num)[0],
                       np.where(np.array(labels.filename)== file_num + '-rs')[0]])

        if sbj_indexes.shape[0]>0:

            vid_length = get_len(vid_folder + "\\"  + sbj_id
                                          + "_" + str(day) + "\\" + sbj_id
                                          + "_" + str(day) + "_" + file_num + ".avi")
            result = convert_labels_to_array(labels,sbj_indexes, vid_length, tracks, pretty_tracks)

            pickle.dump(result, open(dst_folder + "\\" + sbj_id +"_" + day + "_" + file_num + ".p", "wb"))

def extract_detailed_labels(sbj_id, day, labels_file, vid_start_end_folder, dst_folder):

    labels=pd.read_csv(labels_file, sep=':', dtype=str)

    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    pretty_tracks = ["Laugh", "Head_mv", "Other_mv",
              "Arm_mv_right", "Arm_mv_left", "Speak", "Mult_ppl",
              "Sleep","Eat", "Watch",
              "Listen_fam",
              "Listen_staff", "Rest"]

    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.hstack([np.where(np.array(labels.filename)== file_num)[0],
                       np.where(np.array(labels.filename)== file_num + '-rs')[0]])

        if sbj_indexes.shape[0]>0 and os.path.exists("%s\\%s_%s.p" % (vid_start_end_folder, sbj_id, day)):

            vid_length = get_len_from_csv("%s\\%s_%s.p" % (vid_start_end_folder, sbj_id, day), i )
            result = convert_detailed_labels_to_array(labels,sbj_indexes, vid_length, tracks, pretty_tracks)

            pickle.dump(result, open(dst_folder + "\\" + sbj_id + "_" + day + "_" + file_num + ".p", "wb"))

def extract_reduced_labels(sbj_id, day, labels_file, vid_folder, dst_folder):

    labels=pd.read_csv(labels_file, sep=':', dtype=str)
    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    tracks_reduced = ["Mvmt", "Sound", "Rest", "Other"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.hstack([np.where(np.array(labels.filename)== file_num)[0],
                       np.where(np.array(labels.filename)== file_num + '-rs')[0]])

        if sbj_indexes.shape[0]>0:

            vid_length = get_len(vid_folder + "\\"  + sbj_id
                                          + "_" + str(day) + "\\" + sbj_id
                                          + "_" + str(day) + "_" + file_num + ".avi")
            result = convert_reduced_labels_to_array(labels,sbj_indexes, vid_length, tracks, tracks_reduced)
            pickle.dump(result, open(dst_folder +  "\\" + sbj_id +"_" +str(day) + "_" + file_num + ".p", "wb"))

def extract_labeller_reduced_labels(sbj_id, day, src_folder, vid_folder, dst_folder, labeller):

    labels=pd.read_csv(src_folder + sbj_id + "_" + str(day) + ".txt", sep=':', dtype=str)

    tracks = ["Laughing", "Movement.Head", "Movement.Other",
              "Movement.arm", "Speaking", "Multiple_people",
              "Sleeping","Eating", "Listening.Watching_Media",
              "Listening.Listening_to_family_member",
              "Listening.Listening_to_staff", "Rest"]
    tracks_reduced = ["Mvmt", "Sound", "Rest", "Other"]
    for i in xrange(800):
        file_num = str(i).zfill(4)
        sbj_indexes = np.where(np.array(labels.filename)== file_num + '-' + labeller)[0]

        if sbj_indexes.shape[0]>0:

            vid_length = get_len(vid_folder + "\\"  + sbj_id
                                          + "_" + str(day) + "\\" + sbj_id
                                          + "_" + str(day) + "_" + file_num + ".avi")
            result = convert_reduced_labels_to_array(labels,sbj_indexes, vid_length, tracks, tracks_reduced)
            pickle.dump(result, open(dst_folder +  "\\" + sbj_id + "_" + str(day) +
                                     "_" + file_num + "_" + labeller + ".p", "wb"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', required=True, help="Label directory")
    parser.add_argument('-v', '--vid_dir', required=True, help="Video directory or video_start_time directory")
    parser.add_argument('-sbj', '--sbj_id', help="subject ID")
    parser.add_argument('-day', '--day', help="day", type=int)
    parser.add_argument('-s', '--save', required=True, help="Save directory" )
    parser.add_argument('-m', '--mode', help="Mode of label extraction", default="detailed" )
    args = parser.parse_args()
    for file in glob.glob(args.dir + "\\*"):
        #pdb.set_trace()
        sbj_id, day = file.split("\\")[-1].split(".")[0].split("_")
        if args.mode == "detailed":
            extract_detailed_labels(sbj_id, day, file, args.vid_dir, args.save)
