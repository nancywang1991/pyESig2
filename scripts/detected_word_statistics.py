import enchant
import pdb

d = enchant.Dict("en_US")
orig_file = open("/home/wangnxr/Documents/Deepspeech/data/fisher-swbd-ecog/ver1_test2.csv")
predicted_file = open("/home/wangnxr/Documents/deepspeech_results.txt")
#result_file = open("", "wb")

accuracy_dict = {}

for l, line in enumerate(orig_file):
    _, file, _, transcript = line.split(",")
    transcript_words = transcript.split(" ")
    prediction = predicted_file.read()
    for word in prediction.split(" "):
        if d.check(word):
            if word in accuracy_dict:
                if word in transcript_words:
                    accuracy_dict[word]["orig_correct"] += 1
                else:
                    accuracy_dict[word]["orig_incorrect"] += 1
            else:
                accuracy_dict[word] = {"orig_correct":0, "orig_incorrect": 0, "guess_correct": 0 , "guess_incorrect": 0}
        else:
            guess = d.suggest(word)[0]
            if guess in accuracy_dict:
                if guess in transcript_words:
                    accuracy_dict[guess]["guess_correct"] += 1
                else:
                    accuracy_dict[guess]["guess_incorrect"] += 1
            else:
                accuracy_dict[guess] = {"orig_correct":0, "orig_incorrect": 0, "guess_correct": 0 , "guess_incorrect": 0}
pdb.set_trace()