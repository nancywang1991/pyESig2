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
        #pdb.set_trace()
        if args.use_prev==0 or not os.path.exists("%s/%s.mp4.enc" %(args.s_temp, os.path.basename(file).split(".")[0])) :
            print file
            fname = file.split('/')[-1].split('.')[0]
            fnum = fname.split("_")[-1]
            #Patient detection
            subprocess.call('rm %s/tmp/*' % args.dark_home, shell=True)
            subprocess.call('openssl enc -d -des -pass pass:%s -in %s -out %s' %(password, file, file[:-4]), shell=True)
            os.chdir(args.dark_home)
            subprocess.call('%s/darknet yolo demo %s %s %s -i ' %
                        (args.dark_home, args.yolo_config, args.yolo_weights, file[:-4]), shell=True)

            # Move files over to videobase
            gen_cropped_vid(file[:-4],"%s/tmp/%scoords.txt" %(args.dark_home, os.path.basename(file[:-4])), '%s/' % (args.s_temp))
            subprocess.call('rm %s' % file[:-4], shell=True)
        #shutil.move("%s/tmp/coords.txt" %(args.dark_home), '%s/%s.txt' % (args.save, fname))

            for file in glob.glob("%s/*.mp4" % args.s_temp):
                subprocess.call('openssl enc -des -pass pass:%s -in %s -out %s' % (password, file, file + ".enc"), shell=True)
                subprocess.call('rm %s' % file, shell=True)

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-home', '--home', help="Home", default="/home/wangnxr/Documents/")
    parser.add_argument('-d', '--dir', required=True, help="Video directory")
    parser.add_argument('-s_temp', '--s_temp', required=True, help="Patient Extracted Video Save Directory")
    parser.add_argument('-dark', '--dark_home', default='/home/wangnxr/Documents/darknet/', help='Darknet home' )
    parser.add_argument('-w', '--yolo_weights',
                        default = '/home/wangnxr/Documents/darknet/models/yolo_patient_mod_23000.weights',
                        help = 'darknet yolo weights')
    parser.add_argument('-c', '--yolo_config',
                        default = '/home/wangnxr/Documents/darknet/cfg/yolo_patient_mod.cfg',
                        help = 'darknet yolo config')
    parser.add_argument('-use_prev','--use_prev', default=0, help = "use previous?")
    parser.add_argument('-gpu', '--gpu_id', default=0, type=int, help = "which gpu to use")
    parser.add_argument('-pass', '--password', help="password for secure processing")
    args = parser.parse_args()
    if not hasattr(args, "password"):
        password = getpass.getpass()

    main(args, password)
