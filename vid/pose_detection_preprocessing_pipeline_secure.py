import subprocess
import argparse
import glob
import pdb
import os
from pyESig2.vid.patient_vid_crop import gen_cropped_vid
import shutil
import getpass

def main(args, password):

    for file in sorted(glob.glob('%s/*.avi.enc' % args.dir)):
        if not args.use_prev:
            print file
            fname = file.split('/')[-1].split('.')[0]
            fnum = fname.split("_")[-1]
            #Patient detection
            subprocess.call('wipe %s/tmp/*' % args.dark_home, shell=True)
            subprocess.call('openssl enc -d -des -pass:%s -in %s -out %s' %(password, file, file[:-4]), shell=True)
            os.chdir(args.dark_home)
            subprocess.call('%s/darknet yolo demo %s %s %s' %
                        (args.dark_home, args.yolo_config, args.yolo_weights, file[:-4]), shell=True)

        # Move files over to videobase
        gen_cropped_vid(file[:-4],"%s/tmp/coords.txt" %(args.dark_home), '%s/' % (args.save))
        subprocess.call('wipe %s' % file[:-4], shell=True)
        #shutil.move("%s/tmp/coords.txt" %(args.dark_home), '%s/%s.txt' % (args.save, fname))

        for file in glob.glob("%s/*.avi" % args.save):
            subprocess.call('openssl enc -des -pass:%s -in %s -out %s' % (password, file, file + ".enc"), shell=True)

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-home', '--home', help="Home", default="/home/wangnxr/Documents/")
    parser.add_argument('-d', '--dir', required=True, help="Video directory")
    parser.add_argument('-s', '--save', required=True, help="Save Directory" )
    parser.add_argument('-dark', '--dark_home', default='/home/wangnxr/Documents/darknet/', help='Darknet home' )
    parser.add_argument('-w', '--yolo_weights',
                        default = '/home/wangnxr/Documents/darknet/model/yolo_patient_mod_23000.weights',
                        help = 'darknet yolo weights')
    parser.add_argument('-c', '--yolo_config',
                        default = '/home/wangnxr/Documents/darknet/cfg/yolo_patient_mod.cfg',
                        help = 'darknet yolo config')
    parser.add_argument('-use_prev','--use_prev', default=0, help = "use previous?")
    password = getpass.getpass()
    args = parser.parse_args()
    main(args, password)
