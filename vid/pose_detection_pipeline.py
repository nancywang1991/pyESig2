import subprocess
import argparse
import glob
import pdb
import os
from pyESig2.vid.patient_vid_crop import gen_cropped_frames

def main(args):

    for file in sorted(glob.glob('%s/*.avi' % args.dir)):
         print file
         fname = file.split('/')[-1].split('.')[0]
    #     fnum = fname.split("_")[-1]
    #     #Patient detection
    #     subprocess.call('rm %s/tmp/*' % args.dark_home, shell=True)
    #
    #     os.chdir(args.dark_home)
    #     subprocess.call('%s/darknet yolo demo %s %s %s' %
    #                     (args.dark_home, args.yolo_config, args.yolo_weights, file), shell=True)
    #
    #     # Move files over to deeppose
    #     subprocess.call('mkdir %s/%s/' % (args.save, fname), shell=True)
    #     subprocess.call('mkdir %s/%s/cropped/' % (args.save, fname), shell=True)
    #     gen_cropped_frames(file,"%s/tmp/coords.txt" %(args.dark_home), '%s/' % (args.save))
    #     # Pose detection
    #
    #     os.chdir(args.deep_home)
    #     subprocess.call(['python', '%s/scripts/evaluate_flic.py' % args.deep_home,
    #                 '--mode', 'demo', '--model', '%s/results/AlexNet_final/AlexNet_flic.py' % args.home,
    #                 '--param', '%s/results/AlexNet_final/epoch-1000.model' % args.home,
    #                 '--resultdir', '%s/%s/' % (args.save, fname), '--gpu', '1',
    #                 '--datadir', '%s/%s/cropped/' % (args.save, fname)])
    #     #Stich pose results into one video
    #     subprocess.call('ffmpeg -r 30 -i %s/%s/' %(args.save, fname) + '%05d_pred.png -c:v libx264 '
    #                    + '-pix_fmt yuv420p %s/%s/%s.avi' % (args.save, fname, fname), shell=True)
         subprocess.call(['python', '/home/wangnxr/PycharmProjects/pyESig2/movement/joint_movement_norm.py',
                         '-f', '%s/%s/joint_coords.csv' % (args.save, fname), '-s', '%s/%s' %(args.save, fname),
                         '--datadir', '%s/%s/cropped' % (args.save, fname) ])


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-home', '--home', help="Home", default="/home/wangnxr/Documents/")
    parser.add_argument('-d', '--dir', required=True, help="Video directory")
    parser.add_argument('-s', '--save', required=True, help="Save Directory" )
    parser.add_argument('-dark', '--dark_home', default='/home/wangnxr/Documents/darknet_new/darknet/', help='Darknet home' )
    parser.add_argument('-deep', '--deep_home', default='/home/wangnxr/Documents/deeppose/', help='Deeppose home')
    parser.add_argument('-w', '--yolo_weights',
                        default = '/home/wangnxr/Documents/darknet/yolo/backup/all_sbj/yolo_patient_mod_19000.weights',
                        help = 'darknet yolo weights')
    parser.add_argument('-c', '--yolo_config',
                        default = '/home/wangnxr/Documents/darknet/cfg/yolo_patient_mod.cfg',
                        help = 'darknet yolo config')
    args = parser.parse_args()
    main(args)
