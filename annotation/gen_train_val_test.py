__author__ = 'wangnxr'
import os
import glob
import random
import pdb

main_dir = "D:\\keyframes\\"
for label_dir in glob.glob(main_dir + "\*"):
    print label_dir
    if not os.path.isdir(label_dir + "\\ImageSets\\Main\\"):
        os.makedirs(label_dir + "\\ImageSets\\Main\\")
    train = open(label_dir + "\\ImageSets\\Main\\" + "patient_train.txt", "wb")
    val = open(label_dir + "\\ImageSets\\Main\\" + "patient_val.txt", "wb")
    test = open(label_dir + "\\ImageSets\\Main\\" + "patient_test.txt", "wb")
    train2 = open(label_dir + "\\ImageSets\\Main\\" + "train.txt", "wb")
    val2 = open(label_dir + "\\ImageSets\\Main\\" + "val.txt", "wb")
    test2 = open(label_dir + "\\ImageSets\\Main\\" + "test.txt", "wb")
    for f in glob.glob(label_dir + "\\annotations\\*"):

        r = random.randint(0,100)
        if r > 50:
            test.write(f.split("\\")[-1].split(".")[0] + "\n")
        elif r >25:
            val.write(f.split("\\")[-1].split(".")[0]+ "\n")
        else:
            train.write(f.split("\\")[-1].split(".")[0]+ "\n")
    train.close()
    val.close()
    test.close()