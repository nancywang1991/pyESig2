import glob
import cPickle as pickle
import pdb
import argparse
import subprocess

sbj_id = "a0f66459"

def main(sbj_id):
    save_dir = "~/transcriptions/"
    audio_dir = "/data1/voice_activity_orig/"
    transcript_dir = "/data1/voice_activity_orig/"
    synset_file = "/data1/voice_activity_orig/word2synset_dict.p"

    word2synset = pickle.load(open(synset_file,"r"))
    for trans_file in glob.glob("%s/%s/*_trans.csv" % (transcript_dir, sbj_id)):
        day = trans_file.split("/")[-1].split("_")[1]
        save_file = "%s/%s/%s_%s_trans_clean.csv" % (save_dir, sbj_id, sbj_id, day)
        cur_ind = 0
        try:
            last_file_done = open(save_file).readlines()[-1].split(",")[0]
            for n, line in enumerate(open(trans_file)):
                if line.split(",")[0] == last_file_done:
                    cur_ind = n
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
                    subprocess.call("ffplay %s" % audio, shell=True)
                    corrects = raw_input("corrects (separated by comma), r to replay:").split(",")
                    while corrects == ["r"]:
                        subprocess.call("ffplay %s" % audio, shell=True)
                        corrects = raw_input("corrects (separated by comma), r to replay:").split(",")
                    if not corrects == [""]:
                        result.write(",".join([audio_file, transcript[:-1], " ".join([words_to_do[int(correct)] for correct in corrects])]) + "\n")
                        #result.write(",".join([audio_file, transcript[:-1],corrects[0]]) + "\n")
                    else:
                        result.write(",".join([audio_file, transcript[:-1], " "]) + "\n")
                    result.flush()
        print subset, total, subset/total

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sbj_id", help="subject id")
    args = parser.parse_args()
    main(args.sbj_id)

