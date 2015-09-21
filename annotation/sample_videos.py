import glob
import random
import os
import csv
import pdb

def select_videos(vids, num_vids_select):
    random.shuffle(vids)
    return vids[:num_vids_select]

def subdir(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

main_folder = "D:\\NancyStudyData\\ecog\\raw\\"
result_folder = ("C:\\Users\\wangnxr\\Documents\\" +
                    "rao_lab\\video_analysis\\manual_annotations\\")
sbj_dirs = ["e70923c4"]

for sbj in sbj_dirs:
    with open(result_folder+sbj+"_to_label.csv","wb") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        date_dirs = subdir(main_folder+sbj)
        for date in date_dirs:
            files = glob.glob(main_folder+sbj+"\\"+date+"\\*.avi")
            res = select_videos(files, len(files)/10)
            for r in res:
                basename = os.path.basename(r)
                csvwriter.writerow([basename[:-9], basename[-8:-4]])
        
