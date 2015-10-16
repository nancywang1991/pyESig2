import numpy as np
import pdb
from pyESig2.analysis.mu_drop_funcs import butter_bandpass_filter
import matplotlib.pyplot as plt
import subprocess as sp
from scipy.io.wavfile import read

#-------------------------------Main Function--------------------------------
def display_audio_signals(file,  start_sec, end_sec):
    rate, audio_array = read(file)
    # num_secs = 120
    # FFMPEG_BIN = "ffmpeg.exe"
    # command = [ FFMPEG_BIN,
    #             '-i',file,
    #             '-vn',
    #             '-f', 'wav',
    #             '-c:a', 'pcm_mulaw',
    #             '-ar', str(samp_rate*2),
    #             '-ac', '1', '-']
    # pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**9)
    # win_size = samp_rate
    # raw_audio = pipe.stdout.read(win_size*2*num_secs)
    # audio_array = np.fromstring(raw_audio, dtype="int16")
    # #audio_array = butter_bandpass_filter(audio_array, 250,400, samp_rate)
    # audio_array = (audio_array/10000.0)**9

    plt.plot(audio_array[start_sec*rate:end_sec*rate:10], color='blue')
    plt.axis('off')
    #plt.xticks([])
    #plt.yticks([])
    plt.ylim([-20000,20000])
#    plt.xlim([0,2*rate])
    plt.show()



#---------------------------------Subject Params-------------------------------

#sbj_id = "fcb01f7a"
#n_channels = 84
sbj_id = "e70923c4"
#n_channels = 86
#sbj_id = "a86a4375"
#n_channels = 104
#sbj_id = "ffb52f92"
#n_channels = 106
#sbj_id = "d6532718"
date = '5'
vid_file_loc = "C:\\Users\\wangnxr\\Videos\\"
vid_num = 608


#--------------------------------Signal Extraction-----------------------------

file = (vid_file_loc + sbj_id + "_" + str(date) + "_"
            + str(vid_num).zfill(4) + ".wav")
display_audio_signals(file, 109, 111)



