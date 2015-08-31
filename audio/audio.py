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
video_file_loc = "E:\\" + sbj_id \
                 + "_" + str(day) + "\\"
output_file_loc = "E:\\sound\\"

FFMPEG_BIN = "ffmpeg.exe"

for vid in range(0,500):
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
    
    power_array = np.zeros(num_secs*30)
    for t in range(0,(num_secs-8)*samp_rate, samp_rate*7):
        raw_audio = pipe.stdout.read(samp_rate*2*8)
        if len(raw_audio)<samp_rate*2*8:
            break
        audio_array = np.fromstring(raw_audio, dtype="int16")
        audio_array = butter_bandpass_filter(audio_array,250,400, samp_rate)
        for c in range(0,8):
            for f in range(0,30):
                power = np.sum((np.abs(np.fft.fft(audio_array[c*samp_rate + 8000/30*f:(c+1)*samp_rate + 8000/30*f]))[250:400])**2)
                power_array[t/(samp_rate)*30+c*30+f] = power
            power_array[t/(samp_rate)*30+c*30+f+1] = power
    pickle.dump(power_array, open(output_file_loc + sbj_id + "_" + str(day) + "_" + num + ".p", "wb"))
    pipe.kill()

