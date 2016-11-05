import os
import csv
from datetime import time, datetime, timedelta
import pdb
import cPickle as pickle
import argparse

def main(file, vid_start_end, save_fldr):
    timestamps = csv.reader(open(file))
    next(timestamps, None)
    writefile = open(save_fldr + "processed_timestamps_real_time.csv", "wb")
    new_timestamp_file = csv.writer(writefile)
    new_timestamp_file.writerow(["subject ID", "file number", "word", "Is_patient?", "mode", "year", "month", "day", "hour", "minute", "second", "microsecond"])
    for timestamp in timestamps:
        print timestamp
        vid_name, time_start, time_end, word, patient, mode = timestamp
        #pdb.set_trace()
        sbj_id, day, vid = vid_name.split("_")
        #pdb.set_trace()
        print "%s\\%s_%s.p" % (vid_start_end, sbj_id, day)
        if os.path.isfile("%s\\%s_%i.p" % (vid_start_end, sbj_id, int(day))):
            video_starts = pickle.load(open("%s\\%s_%i.p" % (vid_start_end, sbj_id, int(day)), "rb"))
            new_start = video_starts["start"][int(vid)] + timedelta(seconds=float(time_start))
            new_timestamp_file.writerow([sbj_id, day, word, patient, mode, new_start.year, new_start.month, new_start.day, new_start.hour, new_start.minute, new_start.second, new_start.microsecond])
    writefile.close()
            
if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('-f', '--file', default = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\manual_annotations\\oops\\fully_processed_timestamps.csv", help="File to convert")
   parser.add_argument('-s', '--save', default = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\manual_annotations\\oops\\", help="Save directory" )
   parser.add_argument('-start', '--start', default = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\", help="Start end directory" )
   args = parser.parse_args()
   main(args.file, args.start, args.save)
