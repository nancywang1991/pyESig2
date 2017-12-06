import pyedflib
import pandas
import numpy as np
from vid.video_sync.vid_start_end import get_disconnected_times
import datetime

sbj_id = "cb46fd46"
conversion_file = "/home/nancy/Documents/data_release/%s.csv" % sbj_id
disconnect_times_dir = "/home/nancy/Documents/disconnect_times/"
orig_edf_dir = "/data/decrypted_edf/%s/" % sbj_id
save_dir = "/space/data_by_day/"

def get_sample_len(time1, time2):
    return max(0, int((time2-time1).total_seconds()*1000))

conversion = pandas.read_csv(conversion_file)

for day in conversion:
    orig_files = ["%s/%s.edf" % (orig_edf_dir, orig_file) for orig_file in [day["file1"],day["file2"],day["file3"]] if len(orig_file)> 0]
    start_end_times = [get_disconnected_times("%s/%s.txt" % (disconnect_times_dir, orig_file))[:2]
                       for orig_file in [day["file1"], day["file2"], day["file3"]] if len(orig_file) > 0]
    final_start_time = datetime.strptime("01-0%i-1000 " % day["day"] + day["start_time"], '%m-%d-%Y %H:%M:%S:%f')
    final_end_time = datetime.strptime("01-0%i-1000 " % day["day"] + day["end_time"], '%m-%d-%Y %H:%M:%S:%f')

    final_start_time_orig = datetime.strptime(day["start_date"] + " " + day["start_time"], '%m-%d-%Y %H:%M:%S:%f')
    final_end_time_orig = datetime.strptime(day["start_date"] + " " + day["end_time"], '%m-%d-%Y %H:%M:%S:%f')

    # Set up final edf file
    edf_files = [pyedflib.EdfReader(file) for file in orig_files]
    n_channels = edf_files[0].getSignalLabels().index('ECGR')
    edf_out = pyedflib.EdfWriter("%s/%s_day_%i.edf" % (save_dir, sbj_id, day["day"]), n_channels)

    # De-identify date of patient stay and update start time
    edf_out.setHeader(edf_files[0].getHeader())
    edf_out.setStartdatetime(final_start_time)

    # Set signal header
    edf_out.setSignalHeaders(edf_files[0].getSignalHeaders[1:n_channels+1])

    # write data
    physical_min = edf_files[0].getPhysicalMaximum(1)
    main_data = []
    for channel in range(1, n_channels+1):
        chan_data = [physical_min]*get_sample_len(final_start_time_orig, start_end_times[0][0])
        for f, file in edf_files:
            if final_end_time_orig < start_end_times[f][1]:
                chan_data += file.readSignal(channel)[:get_sample_len(start_end_times[f][0], final_end_time_orig)]
            else:
                chan_data += file.readSignal(channel)
            if f+1 < len(start_end_times):
                chan_data += [physical_min]*get_sample_len(start_end_times[f][1], start_end_times[f+1][0])
        main_data.append(chan_data)
    edf_out.writeSamples(main_data)
    edf_out.close()





