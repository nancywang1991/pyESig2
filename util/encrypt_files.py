import argparse
import getpass
import subprocess
import os
import glob

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help="original encrypted file")
    args = parser.parse_args()
    parent = os.path.dirname(args.file)
    password = getpass.getpass()
    subprocess.call("openssl enc -d -des -in %s -out %s -pass pass:%s" % (args.file, args.file.split(".")[0] + ".tar", password), shell=True)
    os.remove(args.file)
    subprocess.call("tar -xvzf %s.tar" % args.file.split(".")[0])
    os.remove("%s.tar" % args.file.split(".")[0])
    new_folder = glob.glob("%s/*/*/*/*/*/*/*/*/*" % parent)[0]
    subprocess.call("mv %s %s" %("/".join(new_folder.split("/")[:-2]), parent), shell=True)
    for file in glob.glob(parent + "/*/*/*.avi"):
        subprocess.call("openssl enc -e -des -in %s -out %s -pass pass:%s" % (file, file + ".enc", password), shell=True)
    for file in glob.glob(parent + "/*/*/*"):
        if not file.split(".")[-1] == "enc" and not os.path.isdir(file):
            os.remove(file)