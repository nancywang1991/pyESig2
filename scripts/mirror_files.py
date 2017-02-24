
import argparse
import os
import time
import shutil
import xml.etree.ElementTree as ET
import winsound
import pdb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Listen for file changes and mirror changed files to a second location.')
    parser.add_argument('-s', '--source', dest='source', action='store',
        default=None, help='The source folder', required=True)
    parser.add_argument('-k', '--keyframe', dest='keyframe', action='store',
        default=None, help='The keyframes folder', required=True)
    args = parser.parse_args()

    if not args.source:
        raise ValueError(
            "You must provide "
            "a source folder and keyframe folder")
    source_folder = os.path.normpath(args.source)
    last_time = os.stat(os.path.normpath(source_folder + "/" + max(sorted(os.listdir(source_folder))))).st_mtime
    sorted_keyframes = sorted(os.listdir(os.path.normpath(args.keyframe)))
    # currently only ctrl+c will terminate
    while (True):
        try:
            stat = os.stat(source_folder)
        except OSError as e:
            print "Encountered a OSError, skipping file:"
            print e
            continue
        max_file = max(sorted(os.listdir(source_folder)))
        pdb.set_trace()
        if os.stat(os.path.normpath(source_folder+"/"+max_file)).st_mtime > last_time:
            ind = sorted_keyframes.index(max_file.split(".")[0][:-2]+".jpg")
            if ind == len(sorted_keyframes):
                print "Yay, all done!"
            else:
                for i in range(1,11):
                    new_f_name = sorted_keyframes[ind+i]
                    new_xml_f = os.path.normpath(source_folder+"/"+new_f_name.split(".")[0] + "_1.xml")
                    shutil.copyfile(os.path.normpath(source_folder+"/"+max_file), new_xml_f)
                    tree = ET.parse(new_xml_f)
                    root = tree.getroot()
                    for image in root.iter("image"):
                        image.text = new_f_name.split(".")[0]
                        image.set("updated","yes")
                    tree.write(new_xml_f)
                    last_time = os.stat(new_xml_f).st_mtime
                    print "Frame %i pose copied" % (int+i)
                winsound.beep(300,500)

