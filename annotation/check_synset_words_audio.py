import glob
import cPickle as pickle
import pdb
import argparse
import subprocess
import os

def main(sbj_id):
    save_dir = "%s/transcriptions/" % os.getenv("HOME")
    audio_dir = "/data1/voice_activity_orig/"
    transcript_dir = "/data1/voice_activity_orig_old/"
    synset_file = "/data1/voice_activity_orig_old/word2synset_dict.p"

    word2synset = pickle.load(open(synset_file,"r"))
    for trans_file in glob.glob("%s/%s/*_trans.csv" % (transcript_dir, sbj_id)):
        
        day = trans_file.split("/")[-1].split("_")[1]
        print "Starting sbj %s day %s" % (sbj_id, day)
        if not os.path.exists("%s/%s/" % (save_dir, sbj_id)):
            os.makedirs("%s/%s/" % (save_dir, sbj_id))
        save_file = "%s/%s/%s_%s_trans_clean.csv" % (save_dir, sbj_id, sbj_id, day)
        cur_ind = 0
        try:
            last_file_done = open(save_file).readlines()[-1].split(",")[0]
            for n, line in enumerate(open(trans_file)):
                if line.split(",")[0] == last_file_done:
                    cur_ind = n
                    print "On line %i" % n 
                    break
        except (IOError, IndexError) as e:
            pass
        subset = 0
        total = 0
        with open(save_file, "a") as result:
            for line in open(trans_file).readlines()[cur_ind+1:]:
                audio_file, transcript = line.split(",")
                length = float(".".join(audio_file.split("_")[-1].split(".")[:2])) - float(audio_file.split("_")[-2])
                total += length
                words_to_do = []
                for word in transcript.split(" "):
                    if word in word2synset and len(word)>4:
                        words_to_do.append(word)
                if not words_to_do == []:
                    print ", ".join(["%i-%s" %(n, word) for n, word in enumerate(words_to_do)])
                    subset += length
                    audio = "%s/%s" % (audio_dir, "/".join(audio_file.split("/")[-3:]))
                    subprocess.call("aplay %s" % audio, shell=True)
                    corrects = raw_input("words (separated by space), r to replay:").split(",")
                    while corrects == ["r"]:
                        subprocess.call("aplay %s" % audio, shell=True)
                        corrects = raw_input("words (separated by space), r to replay:").split(",")
                    if not corrects == [""]:
                        result.write(",".join([audio_file, transcript[:-1], " ".join([correct for correct in corrects])]) + "\n")
                        #result.write(",".join([audio_file, transcript[:-1],corrects[0]]) + "\n")
                    else:
                        result.write(",".join([audio_file, transcript[:-1], " "]) + "\n")
                    result.flush()
        print subset, total

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sbj_id", help="subject id", required=True)
    args = parser.parse_args()
    main(args.sbj_id)

