import pyedflib
import pandas
import numpy as np
from datetime import datetime
import pdb
import glob

sbj_id = "c95c1e82"
merge_edf_dir = "/data1/data_release/"
save_dir = "/data1/data_release/"
pose_dir = "/data1/data_release/"

def get_sample_len(time1, time2):
    return max(0, int((time2-time1).total_seconds()*1000))

def get_purge_array(start_time, length, purge_times):
    purge_array = np.zeros(length)
    for time in purge_times.iterrows():
        time2 = datetime.strptime("01-%02i-1000 " % start_time.day + time, '%m-%d-%Y %H:%M:%S:%f')
        ind = get_sample_len(start_time, time2)
        purge_array[ind:ind+34] = 1
    return purge_array

for file in glob.glob("%s/%s_*.edf" % (merge_edf_dir, sbj_id)):
    pose_file = pandas.read_csv("%s/%s.csv" % (pose_dir, file.split("/")[-1].split(".")[0]))
    purge_times = pose_file[pose_file["purge"]==1]["time"]
    main_data = []
    if len(purge_times) > 1 :
        n_channels = len(orig_edf.getSampleFrequencies())
        orig_edf = pyedflib.EdfReader(file)
        edf_out = pyedflib.EdfWriter("%s/purged_%s" % (save_dir, file.split("/")[-1]), len(orig_edf.getSampleFrequencies()))
        edf_out.setHeader(orig_edf.getHeader())
        edf_out.setSignalHeaders(orig_edf.getSignalHeaders())
        purge_array = get_purge_array(orig_edf.getStartdatetime(), orig_edf.getNSamples(), purge_times)
        for channel in range(n_channels):
            chan_data = np.place(orig_edf.readSignal(channel), purge_array, orig_edf.getPhysicalMinimum())
        main_data.append(chan_data)
    edf_out.writeSamples(main_data)
    edf_out.close()
    orig_edf._close()