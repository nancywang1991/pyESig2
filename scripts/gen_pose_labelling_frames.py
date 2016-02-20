import os
import pdb

sbj_id = "ea430431"
keyframes_folder = "D:\\keyframes\\" + sbj_id + "\\images\\"
annotation_list_file = "D:\\keyframes\\" + sbj_id + "\\annotation_list.txt"

with open(annotation_list_file, "wb") as annotations:
    frames = os.listdir(keyframes_folder)
    frames.sort()
    for f in frames:
        if f[-3:] == "jpg":
            annotations.writelines(f.split(".")[0]+"_1.xml\n")

