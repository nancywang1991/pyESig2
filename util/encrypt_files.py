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
    if (args.step<=0):
    	parent = os.path.dirname(args.file)
    	subprocess.call("openssl enc -d -des -in %s -out %s -pass pass:%s" % (args.file, args.file.split(".")[0] + ".tar", password), shell=True)
    	os.remove(args.file)
    if args.step<=1:
        #pdb.set_trace()
    	subprocess.call("tar -xvzf %s.tar" % args.file, shell=True)
    	os.remove("%s.tar" % args.file.split(".")[0])
    if args.step<=2:
    	new_folder = glob.glob("%s/*/*/*/*/*/*/*/*" % parent)[0]
    	subprocess.call("mv %s %s" %("/".join(new_folder.split("/")[:-2]), parent), shell=True)
    if args.step<=3:
    	for file in glob.glob(parent + "/*/*/*.avi"):
        	subprocess.call("openssl enc -e -des -in %s -out %s -pass pass:%s" % (file, file + ".enc", password), shell=True)
    if args.step<=4:
	for file in glob.glob(parent + "/*/*/*"):
            if not file.split(".")[-1] == "enc" and not os.path.isdir(file):
                os.remove(file)
