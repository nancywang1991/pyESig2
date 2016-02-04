import subprocess as sp
import numpy as np
import pdb
from pyESig2.freq.signal_filter import butter_bandpass_filter
import pickle
import gc
import glob
import matplotlib.pyplot as plt
import pdb
import os
import subprocess
import json
from datetime import timedelta

def get_len(filename):

   result = subprocess.Popen(["ffprobe", filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
   stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
   return float(json.loads(result.stdout.read())['streams'][0]['duration'])

sbj_id_all = ["d6532718", "cb46fd46", "e70923c4", "fcb01f7a", "a86a4375", "c95c1e82" ]
dates_all = [[4,5,6,7],[7,8,9,10],[4,5,6,7],[5,6,7,8,9,10,11,12], [4,5,6,7], [4,5,6,7]]
# for sbj_id in sbj_id_all:
#      for day in dates_all[sbj_id_all.index(sbj_id)]:
#         video_file_loc = "D:\\NancyStudyData\\ecog\\raw\\" + sbj_id + "\\" \
#                          + sbj_id + "_" + str(day) + "\\"
#         output_file_loc = "E:\\sound\\"  + sbj_id + "\\" + str(day) + "\\"
#
#         FFMPEG_BIN = "ffmpeg.exe"
#         num_vids = len(glob.glob(video_file_loc + "*.avi"))
#
#         for vid in range(0,num_vids):
#             gc.collect()
#             print "Working on video #" + str(vid+1)
#             num = str(vid).zfill(4)
#             fname = video_file_loc + sbj_id + "_" + str(day) + "_" + num + ".avi"
#             vid_len = timedelta(seconds = get_len(fname))
#             savefile = output_file_loc + sbj_id + "_" + str(day) + "_" + num + ".p"
#             if (vid_len.seconds > 120):
#                 subprocess.Popen(["rm", savefile], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
# pdb.set_trace()
for sbj_id in sbj_id_all[3:4]:
    samp_rate = 4000
    num_secs = 200
    #mvmt_file_loc = "C:\\Users\\wangnxr\\Documents\\rao_lab" \
    #                + "\\video_decode\\mvmt_result_agg\\"
    for day in dates_all[sbj_id_all.index(sbj_id)]:
        video_file_loc = "D:\\NancyStudyData\\ecog\\raw\\" + sbj_id + "\\" \
                         + sbj_id + "_" + str(day) + "\\"
        output_file_loc = "E:\\sound\\"  + sbj_id + "\\" + str(day) + "\\"

        FFMPEG_BIN = "ffmpeg.exe"
        num_vids = len(glob.glob(video_file_loc + "*.avi"))

        for vid in range(0,num_vids):
            gc.collect()
            print "Working on video #" + str(vid)
            num = str(vid).zfill(4)
            fname = video_file_loc + sbj_id + "_" + str(day) + "_" + num + ".avi"
            vid_len = timedelta(seconds = get_len(fname))
            f_rate = 30
            print vid_len.seconds
            if not (os.path.isfile(output_file_loc + sbj_id + "_" + str(day) + "_" + num + ".p")):
                command = [ FFMPEG_BIN,
                            '-i', fname,
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
                #plt.plot(audio_array[::100])
                #plt.show()
                #pdb.set_trace()
                audio_array = butter_bandpass_filter(audio_array,50,3500, samp_rate*2)
                audio_len = len(audio_array)/samp_rate
                power_array = np.zeros((len(audio_array)*30)/samp_rate)

                print "writing " + str(vid)
                for c in range(0,audio_len):
                    for f in range(0,f_rate):
                        signal_window = audio_array[c*win_size + offset*f:(c+1)*win_size + offset*f]
                        power = np.mean((np.abs(np.fft.fft(signal_window*np.hamming(len(signal_window))))[100:3500])**2)
                        power_array[c*f_rate+f] = power
                if len(power_array)>30:
                    power_array[-30:]=power_array[-31]
                print "wrote " + str(vid)
                pickle.dump(power_array, open(output_file_loc + sbj_id + "_" + str(day) + "_" + num + ".p", "wb"))
                pipe.kill()