import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import pdb
from pyESig.analysis.mu_drop_funcs import butter_bandpass_filter
import pickle
import gc

sbj_id = "fcb01f7a"
day = 16
samp_rate = 8000
num_secs = 120
#mvmt_file_loc = "C:\\Users\\wangnxr\\Documents\\rao_lab" \
#                + "\\video_decode\\mvmt_result_agg\\"
video_file_loc = "D:\\" + sbj_id \
                 + "_" + str(day) + "\\"
output_file_loc = "D:\\sound\\"

FFMPEG_BIN = "ffmpeg.exe"

for vid in range(0,743):
    gc.collect()
    print "Working on video #" + str(vid+1)
    num = str(vid).zfill(4)
    command = [ FFMPEG_BIN,
            '-i', video_file_loc + sbj_id + "_" + str(day) + "_" + num + ".avi",
            '-vn', 
            '-f', 'wav',
            '-c:a', 'pcm_mulaw', 
            '-ar', str(samp_rate*2),
            '-ac', '1', '-']
    pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**9)
    

    win_size = samp_rate
    f_rate = 30
    offset = samp_rate/f_rate
    raw_audio = pipe.stdout.read(win_size*2*num_secs)
    audio_array = np.fromstring(raw_audio, dtype="int16")
    audio_array = butter_bandpass_filter(audio_array,250,400, samp_rate)
    audio_len = len(audio_array)/samp_rate
    power_array = np.zeros(audio_len*30)
    for c in range(0,audio_len):
        for f in range(0,f_rate):
            signal_window = audio_array[c*win_size + offset*f:(c+1)*win_size + offset*f]
            power = np.mean((np.abs(np.fft.fft(signal_window*np.hamming(len(signal_window))))[250:400])**2)
            power_array[c*f_rate+f] = power
    pickle.dump(power_array, open(output_file_loc + sbj_id + "_" + str(day) + "_" + num + ".p", "wb"))
    pipe.kill()

