import argparse
import csv
import glob
import numpy as np
import pdb
import scipy.stats
import matplotlib.pyplot as plt
from scipy import signal
import pickle
import pyedflib

def transcript2synsets(transcript, syn_dict):
    synsets = []
    for word in transcript:
        try:
            synsets.append(syn_dict[word])
        except LookupError:
            pass
    return synsets

def ecog_spectrogram(ecog_clip, f_min=10, f_max=200):
    displaymat = np.zeros(shape=(len(ecog_clip), f_max - f_min))
    freq_ratio = (ecog_clip.shape[1])/1000
    for c in xrange(len(ecog_clip)):
        displaymat[c, :] = np.log(np.abs(np.fft.fft(ecog_clip) ** 2)[f_min*freq_ratio:f_max*freq_ratio:])
    return displaymat

def ecog_map_single_sentence_multi_channel(ecog_clip, transcript, syn_dict, map_dict, f_min=10, f_max=200):
    synsets = transcript2synsets(transcript, syn_dict)
    spectrogram = ecog_spectrogram(ecog_clip, f_min, f_max)
    for synset in synsets:
        try:
            map_dict[synset]["map"] += spectrogram
            map_dict[synset]["count"] += 1
        except KeyError:
            map_dict[synset] = {"map": spectrogram, "count": 1}
    return

def time_clip2edf_pos(clip_name, vid_start_end, day_start):
    sbj, day, vid_num, start, end = clip_name.split("/")[-1].split(".")[0].split("_")
    clip_start = vid_start_end["start"][int(vid_num)] + np.floor(float(start))
    edf_start = int((clip_start-day_start).get_seconds()*1000)
    edf_dur = (np.ceil(end)-np.floor(start))
    return edf_start, edf_dur

def save_synset_maps(map_dict, save_dir):
    for synset, synset_map in map_dict.iteritems():
        final_map = synset_map["map"]/synset_map["count"]
        plt.clf()
        plt.pcolormesh(final_map)
        plt.title("Log power for synset %s" % synset)
        plt.xlabel("frequency")
        plt.ylabel("channel")
        plt.savefig("%s/%s.png" %(save_dir, synset))


def main(ecog_file, syn_dict, transcript, vid_start_end, f_min, f_max, save_dir):

    map_dict = {}
    ecog = pyedflib.EdfReader(ecog_file)
    for line in open(transcript):
        filename, words = transcript.split(",")
        edf_start, edf_dur = time_clip2edf_pos(filename, pickle.load(open(vid_start_end)), ecog.getStartdatetime())
        ecog_clip = np.zeros(shape=(len(ecog_file, edf_dur*1000)))
        for c in xrange(len(ecog)):
            ecog_clip[c,:] = ecog.readSignal(c, start=edf_start, n=edf_dur)
        ecog_map_single_sentence_multi_channel(ecog_clip, words, syn_dict, map_dict, f_min=f_min, f_max=f_max)
    save_synset_maps(map_dict, save_dir)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--ecog", required=True, help="ecog edf file")
    parser.add_argument("-syn", "--syn_dict", required=True, help="synset dictionary file")
    parser.add_argument("-trans", "--transcript", required=True, help="transcript file")
    parser.add_argument('-s', '--save_dir', required=True, help="Save directory")
    parser.add_argument("-v", "--vid_start_end", required=True, help="vid_start_end file")
    parser.add_argument('-f_min', '--frequency_min', required=True, help="minimum frequency", type=int)
    parser.add_argument('-f_max', '--frequency_max', required=True, help="maximum frequency", type=int)
    args = parser.parse_args()

    main(args.ecog, args.syn_dict, args.transcript, args.vid_start_end, args.frequency_min, args.frequency_max, args.save_dir)
