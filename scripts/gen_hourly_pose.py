import pandas
import numpy as np
from vid.video_sync.vid_start_end import get_disconnected_times
from movement.joint_movement_norm import normalize_to_camera
from datetime import datetime
from datetime import timedelta
import cPickle as pickle
import ezodf
import pdb

sbj_id = "cb46fd46"
conversion_file = "/home/nancy/Documents/data_release/%s.csv" % sbj_id
disconnect_times_dir = "/home/nancy/Documents/disconnect_times/"
orig_pose_dir = "/data/pose/%s/" % sbj_id
purge_dir = "/home/nancy/Documents/purge_times/"
save_dir = "/space/nancy/data_by_day/"


def time_to_vid(time, vid_start_ends):
    for s, start_end in enumerate(vid_start_ends):
        for i in len(start_end["start"]):
            if time >= start_end["start"][i] and time <= start_end["end"][i]:
                return s, i, start_end["end"][i]
            if time > start_end["end"][i]:
                return None, None, None

def print_time(time):
    return "%02i:%02i:%02i.%06i" % (time.hour, time.minute, time.second, time.microsecond)


def read_ods(filename, sheet_no=0, header=0):
    tab = ezodf.opendoc(filename=filename).sheets[sheet_no]
    return pandas.DataFrame({col[header].value:[x.value for x in col[header+1:]]
                         for col in tab.columns()})

def is_purged(cur_vid, frame):
    sbj_id, day, vid = cur_vid.split("_")
    df = read_ods("%s/%s/%s_%s.ods" % (purge_dir, sbj_id, sbj_id, day), header=1)
    rows = df.loc[df["video name" == str(vid)]]
    for r in xrange(len(rows)):
        start = rows["start time"][r]
        end = rows["end time"][r]
        time = frame/30
        if time > int(start.split(":")[0])*60 + int(start.split(":")[1]) and
            time < int(end.split(":")[0])*60 + int(end.split(":")[1]):
            return True
    return False



conversion = pandas.read_csv(conversion_file)

for d in xrange(conversion.shape[0]):

    start_end_times = [get_disconnected_times("%s/%s.txt" % (disconnect_times_dir, orig_file))[:2]
                       for orig_file in [conversion["file1"][d], conversion["file2"][d], conversion["file3"][d]] if
                       not isinstance(orig_file, float)]
    vid_start_ends = [pickle.load(open("%s/%s.csv" % (disconnect_times_dir, orig_file)))[:2]
                       for orig_file in [conversion["file1"][d], conversion["file2"][d], conversion["file3"][d]] if
                       not isinstance(orig_file, float)]
    final_start_time = datetime.strptime("01-0%i-1000 " % conversion["day"][d] + conversion["start_time"][d],
                                         '%m-%d-%Y %H:%M:%S:%f')
    final_end_time = datetime.strptime("01-0%i-1000 " % conversion["day"][d] + conversion["end_time"][d],
                                       '%m-%d-%Y %H:%M:%S:%f')

    final_start_time_orig = datetime.strptime(conversion["date"][d] + " " + conversion["start_time"][d],
                                              '%m/%d/%Y %H:%M:%S:%f')
    final_end_time_orig = datetime.strptime(conversion["date"][d] + " " + conversion["end_time"][d],
                                            '%m/%d/%Y %H:%M:%S:%f')
    result_file = pandas.DataFrame({"time":[], "missing":[], "purged": [], "head":[], "r_shoulder":[], "l_shoulder":[], "r_elbow":[], "l_elbow":[], "r_wrist":[], "l_wrist":[]})
    cur_time = final_start_time_orig
    cur_vid_end = final_start_time_orig - timedelta(seconds=1)
    pdb.set_trace()
    while cur_time < final_end_time_orig:
        fnum, vnum, cur_vid_end = time_to_vid(cur_time, vid_start_ends)
        while fnum == None:
            cur_time += timedelta(seconds=1/30.0)
            result_file.append(pandas.DataFrame([[print_time(cur_time)], [1], [0]] + [[(-1,-1,-1)] for i in xrange(7)]))
            fnum, vnum, cur_vid_end = time_to_vid(cur_time, vid_start_ends)
        cur_vid = "%s_%04i" % (conversion["file%i" % fnum+1], vnum)
        poses = open("%s/%s.txt" % (orig_pose_dir, cur_vid)).readlines()
        crop_coord = open("%s/poses/%s.txt" % (orig_pose_dir, cur_vid)).readlines()

        for p, pose in enumerate(poses):
            if not is_purged(cur_vid, p):
                norm_poses = normalize_to_camera(pose, crop_coord[p])
                result_file.append(pandas.DataFrame([[print_time(cur_time)], [0], [0]] +
                                                    [[(norm_pose[0], norm_pose[1], orig_pose[2])] for norm_pose, orig_pose in zip(norm_poses, pose)]))
            else:
                result_file.append(
                    pandas.DataFrame([[print_time(cur_time)], [0], [1]] + [[(-1, -1, -1)] for i in xrange(7)]))
    result_file.to_csv("%s/%s_day_%i.csv" % (save_dir, sbj_id, conversion["day"][d]))