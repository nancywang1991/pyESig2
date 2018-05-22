import matplotlib
matplotlib.use("agg")
import argparse
import csv
import glob
import numpy as np
import pdb
import scipy.stats
import matplotlib.pyplot as plt
from scipy import signal
import cPickle as pickle
import pyedflib
from datetime import timedelta
import copy
import os

test_maps = []
def transcript2synsets(transcript, syn_dict):
    synsets = []
    for word in transcript.split(" "):
        try:
            synsets += syn_dict[word]
        except KeyError:
            pass
    return synsets

def ecog_spectrogram(ecog_clip, f_min=10, f_max=200):
    displaymat_tmp = np.zeros(shape=(len(ecog_clip), f_max - f_min))
    displaymat = np.zeros(shape=(len(ecog_clip), 3))
    freq_ratio = (ecog_clip.shape[1])/1000
    for c in xrange(len(ecog_clip)):
        displaymat_tmp[c,:] = np.log(np.abs(np.fft.fft(ecog_clip[c]) ** 2)[f_min*freq_ratio:f_max*freq_ratio:freq_ratio]).T
    displaymat[:,0] = np.mean(displaymat_tmp[:, 20:50], axis=1)
    displaymat[:,1] = np.mean(displaymat_tmp[:, 65:95], axis=1)
    displaymat[:,2] = np.mean(displaymat_tmp[:, 125:175], axis=1)
    return displaymat

def ecog_map_single_sentence_multi_channel(ecog_clip, prev_clip, transcript, syn_dict, map_dict, save_dict, f_min=10, f_max=200):
    #print transcript
    synsets = transcript2synsets(transcript, syn_dict)
    spectrogram = ecog_spectrogram(ecog_clip, f_min, f_max) - ecog_spectrogram(prev_clip[:,-(ecog_clip.shape[1]):], f_min, f_max)
    #if (spectrogram.max() > 10 or spectrogram.min() < -10):
    #    return
    #print spectrogram.max()
    #print spectrogram.min()
    save_dict["power"].append(spectrogram)
    save_dict["synset"].append(synsets)
    save_dict["transcript"].append(transcript)
    for synset in synsets:
        try:
            map_dict[synset]["map"] += spectrogram
            map_dict[synset]["count"] += 1
        except KeyError:
            map_dict[synset] = {"map": copy.copy(spectrogram), "count": 1}
    return

def time_clip2edf_pos(clip_name, vid_start_end, day_start):
    sbj, day, vid_num, start, end = clip_name.split("/")[-1][:-4].split("_")
    clip_start = vid_start_end["start"][int(vid_num)] + timedelta(seconds=np.floor(float(start)))
    edf_start = int((clip_start-day_start).total_seconds()*1000)
    edf_dur = int((np.ceil(float(end))-np.floor(float(start)))*1000)
    return edf_start, edf_dur

def save_synset_maps(map_dict, save_dir, channels, f_lo, f_hi):
    for synset, synset_map in map_dict.iteritems():
        if synset_map["count"]>50:
            final_map = synset_map["map"]/synset_map["count"]
            plt.clf()
            X1 = np.tile(range(len(channels)), (final_map.shape[1]+1,1))
            Y1 = np.tile(range(4), (len(final_map),1)).T
            plt.pcolormesh(X1, Y1, final_map.T, vmin=-0.5, vmax=0.5)
            plt.title("Log power change for synset %s" % synset)
            plt.ylabel("frequency")
            plt.xlabel("channel")
            plt.xticks(np.arange(len(channels))[::10], channels[::10])
            plt.yticks(np.arange(3), ["beta", "gamma", "high gamma"])
            plt.savefig("%s/%s.png" %(save_dir, synset))


def main(ecog_file, syn_dict, transcript, vid_start_end, f_min, f_max, save_dir):
    map_dict = {}
    save_dict = {"power":[], "synset":[], "transcript": []}
    ecog = pyedflib.EdfReader(ecog_file)
    sbj, day = ecog_file.split("/")[-1].split(".")[0].split("_")
    good_channels = []
    for c in xrange(ecog.signals_in_file):
        test_clip = ecog.readSignal(c, start=200000, n=100)
        if not all(test_clip == 0) and not all(test_clip[0]==test_clip):
                good_channels.append(c)
    for l, line in enumerate(open(transcript).readlines()):
        if l % 100==0:
            print l
        try:
            filename, words = line.split(",")
        except:
            _, filename, _, words = line.split(",")
            line_sbj, line_day = filename.split("/")[-1][:-4].split("_")[:2]
            if not (line_sbj==sbj and line_day == day and len(filename.split("/")[-1][:-4].split("_"))==5):
                continue
        edf_start, edf_dur = time_clip2edf_pos(filename, pickle.load(open(vid_start_end)), ecog.getStartdatetime())
        ecog_clip = np.zeros(shape=(len(good_channels), edf_dur))
        prev_clip = np.zeros(shape=(len(good_channels), 10000))
        for c, chan in enumerate(good_channels):
            prev_clip[c,:] = ecog.readSignal(chan, start=edf_start-10000, n=10000)
            ecog_clip[c,:] = ecog.readSignal(chan, start=edf_start, n=edf_dur) 
        ecog_map_single_sentence_multi_channel(ecog_clip, prev_clip, words, pickle.load(open(syn_dict)), map_dict, save_dict, f_min=f_min, f_max=f_max)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle.dump(save_dict, open(save_dir + "/power_feature_maps.p", "wb"))
    save_synset_maps(map_dict, save_dir, good_channels, f_min, f_max)



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
