import subprocess
import glob
import pdb
import numpy as np

def get_closest_silence(file, start_t):
    proc = subprocess.Popen("ffmpeg -i %s -af silencedetect=noise=-10db:d=2 -f null -" % file)
    output = proc.stdout.read()
    silences_start = []
    silences_end = []
    for line in output:
        if "silence_start" in line:
            silences_start.append(float(line.split(":")[-1]))
        elif "silence_end" in line:
            silences_end.append(float(line.split(":")[-1]))
    try:
        min_ind = np.argmin(start_t-np.array(silences_start))
    except:
        pdb.set_trace()
    return [silences_start[min_ind], silences_end[min_ind]]



audio_snippet_dir = ""
source_vid_dir = ""
clean_file_output_dir = ""

for file in glob.glob(audio_snippet_dir + "/*.wav"):
    filename = "_".join(file.split("/")[-1].split("_")[:3])
    sbj_id, day, vid_num = filename.split("_")
    start_t, end_t = file.split("/")[-1].split("_")[-1][:-4].split("-")
    source_vid = "%s/%s/%s_%s/%s.avi" % (clean_file_output_dir)
    subprocess.call("ffmpeg -i %s -vn -acodec copy tmp_audio.wav" % source_vid )
    silence_t = get_closest_silence("tmp_audio.wav", sbj_id, sbj_id, day, filename, float(start_t))
    subprocess.call("sox tmp_audio.wav -n trim %f %f noiseprof speech.noise-profil" % (silence_t[0], silence_t[1]), shell=True)
    subprocess.call("sox tmp_audio.wav -n %s/%s noisered speech.noise_profil 0.5" % (clean_file_output_dir, file.split("/")))
