import glob
import argparse
import os
import shutil

def main(vid_folder, sbj_ids, days, mode):
    for sbj_id in sbj_ids:
        for day in days:
            mask_folder = "%s\\%s\\%s_%s\\mask\\" % (vid_folder, sbj_id, sbj_id, day)
            if mode=="m":
                print "Masking subject %s on day %s" % (sbj_id, day)
                if not os.path.exists(mask_folder):
                    os.makedirs(mask_folder)
                for vid in glob.glob("%s\\%s\\%s_%s\\*.avi" % (vid_folder, sbj_id, sbj_id, day)):
                    vid_number = int(vid.split("\\")[-1].split(".")[0].split("_")[-1])
                    if vid_number%2==0:
                        shutil.move(vid, mask_folder)
            elif mode=="u":
                print "Unmasking subject %s on day %s" % (sbj_id, day)
                for vid in glob.glob(mask_folder + "\\*.avi"):
                    shutil.move(vid, "%s\\%s\\%s_%s\\" % (vid_folder, sbj_id, sbj_id, day))


if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('-v', '--vid_folder', default = "E:\\", help="Video directory" )
   parser.add_argument('-sbj', '--sbj_id', required=True, help="Subject id", type=str, nargs='+')
   parser.add_argument('-d', '--days', required=True, help="Day of study", type=str, nargs='+')
   parser.add_argument('-m', '--mode', required=True, help= "m=mask, u=unmask", type=str)
   args = parser.parse_args()
   main(args.vid_folder, args.sbj_id, args.days, args.mode)