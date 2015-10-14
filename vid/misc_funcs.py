import cPickle as pickle
import numpy as np
import os
import re
import pdb
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

def has_video(disconnect_file_loc, samp_rate=30):
    disconnect_info = open(disconnect_file_loc, "rb")
    start_line = disconnect_info.readline()
    end_line = disconnect_info.readline()
    
    match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', start_line)
    start_time = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S')
    match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', end_line)
    end_time = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S')

    total_frames = (end_time-start_time).total_seconds()*samp_rate
    has_video = np.zeros(total_frames) + 1
    disconnect_info.readline()

    for line in disconnect_info:
        
        match = re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', line)
        match2 = re.search(r' \d{2}:\d{2}:\d{2}\r\n', line)

        pad_time_start = datetime.strptime(match.group(), '%m-%d-%Y %H:%M:%S')
        pad_time_start_time = datetime.strptime(match.group()[-8:], '%H:%M:%S')
        pad_time_end = datetime.strptime(match2.group()[1:-2], '%H:%M:%S')
        diff = pad_time_start - start_time
        
        frame_start = int((diff.total_seconds())*samp_rate)
        diff2 = pad_time_end - pad_time_start_time
        pad_length = int((diff2.total_seconds())*samp_rate)

        has_video[frame_start:frame_start + pad_length] = 0
    return has_video
    

