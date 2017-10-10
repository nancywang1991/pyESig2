import pandas
import glob
import os
import numpy as np

transcription_folders = ["/data1/sharedata/speech/transcription/maria/todo/", "/data1/sharedata/speech/transcription/maria/todo_2_fullpt/",
                         "/data1/sharedata/speech/transcription/maya/todo/", "/data1/sharedata/speech/transcription/maya/todo2/"]
output_file_train = "/home/wangnxr/Documents/DeepSpeech/data/natural_ecog/ver1_train.txt"
output_file_test = "/home/wangnxr/Documents/DeepSpeech/data/natural_ecog/ver1_test.txt"

data = {}
for file in glob.glob("%s/*.txt" % (transcription_folders)):
    filename, transcription = file.open().readlines()[0].split(" ")
    fsize = os.path.getsize(file)
    if not transcription == "<n>":
        data[file] = [fsize, transcription]

with open(output_file_train, "wb") as writer_train:
    with open(output_file_test, "wb") as writer_test:
        writer_train.write("wav_filename,wav_filesize,transcript/n")
        writer_test.write("wav_filename,wav_filesize,transcript/n")
        for key, value in data.iteritems():
            if np.random.rand<0.9:
                writer_train.write(key+ "," + ",".join(value) + "/n")
            else:
                writer_test.write(key + "," + ",".join(value) + "/n")


