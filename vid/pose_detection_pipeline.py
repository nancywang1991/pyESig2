import subprocess
import argparse
import glob
import pdb
import os
from pyESig2.vid.patient_vid_crop import gen_cropped_frames
from pyESig2.vid.pose_detection_preprocessing_pipeline_secure import main as patient_extract
import getpass

def main(args, password):
    print "Processing %s" % os.path.basename(args.save)
    if not os.path.exists(args.save):
        os.makedirs(args.save)
    if not os.path.exists(args.s_temp):
        os.makedirs(args.s_temp)
    patient_extract(args, password)
    os.chdir(args.deep_home)
    subprocess.call("python python/pose/demo_secure.py -v %s -s %s -gpu %i" % (args.s_temp, args.save, args.gpu_id), shell=True)
    subprocess.call("scp -r %s wangnxr@visiongpu.cs.washington.edu:/mnt/transferred_results/pose/" % (args.save), shell=True)
    subprocess.call("scp -r %s/crop_coords wangnxr@visiongpu.cs.washington.edu:/mnt/transferred_results/pose/%s/" % (args.s_temp, os.path.basename(args.save)), shell=True)

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-home', '--home', help="Home", default="/home/wangnxr/Documents/")
    parser.add_argument('-d', '--dir', required=True, help="Video directory")
    parser.add_argument('-s_temp', '--s_temp', required=True, help="Patient Extracted Video Save Directory")
    parser.add_argument('-s', '--save', required=True, help="Save Directory" )
    parser.add_argument('-dark', '--dark_home', default='/home/wangnxr/Documents/darknet/', help='Darknet home' )
    parser.add_argument('-deep', '--deep_home', default='/home/wangnxr/Documents/caffe-heatmap/', help='Caffe-heatmap home')
    parser.add_argument('-w', '--yolo_weights',
                        default='/home/wangnxr/Documents/darknet/models/yolo_patient_mod_23000.weights',
                        help='darknet yolo weights')
    parser.add_argument('-c', '--yolo_config',
                        default='/home/wangnxr/Documents/darknet/cfg/yolo_patient_mod.cfg',
                        help='darknet yolo config')
    parser.add_argument('-gpu', '--gpu_id', default=0, type=int, help = "which gpu to use")
    parser.add_argument('-use_prev','--use_prev', default=1, help = "use previous?")
    parser.add_argument('-pass', '--password', help="Password for secure processing")
    args = parser.parse_args()
    if not args.password:
        password = getpass.getpass()
    main(args, password)
