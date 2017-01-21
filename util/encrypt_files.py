import argparse
import getpass
import subprocess
import os
import glob
import pdb
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help="original encrypted file")
    parser.add_argument('-st', '--step', type=int, default=0, help="step to start at")
    args = parser.parse_args()
    password = getpass.getpass()
    parent = os.path.dirname(args.file)
    filename=os.path.basename(args.file).split("_")[0]
    if (args.step<=0):
    	subprocess.call("openssl enc -d -des -in %s -out %s -pass pass:%s" % (args.file, args.file.split(".")[0] + ".tar", password), shell=True)
    	os.remove(args.file)
    if args.step<=1:
        #pdb.set_trace()
    	subprocess.call("tar -xvzf %s.tar -C /%s/" % (args.file, parent), shell=True)
    	os.remove("%s.tar" % args.file.split(".")[0])
    if args.step<=2:
    	new_folder = glob.glob("%s/*/*/*/*/*/%s/*/*" % (parent, filename))
        #pdb.set_trace()
        if len(new_folder) == 0:
	    new_folder = glob.glob("%s/*/*/*/*/*/*/%s/*/*" % (parent, filename))
        new_folder = new_folder[0]
    	subprocess.call("mv %s %s/%s" %("/".join(new_folder.split("/")[:-2]), parent, filename), shell=True)
    if args.step<=3:
    	for file in glob.glob(parent + "/%s/*/*.avi" % filename):
        	subprocess.call("openssl enc -e -des -in %s -out %s -pass pass:%s" % (file, file + ".enc", password), shell=True)
    if args.step<=4:
	for file in glob.glob(parent + "/%s/*/*" % filename):
            if not file.split(".")[-1] == "enc" and not os.path.isdir(file):
                os.remove(file)
