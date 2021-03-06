__author__ = 'wangnxr'

import pyESig2.preprocess.spectral_ratios as spec_ratio
import pyESig2.preprocess.ecog_fft_extract as fft_extract
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sbj_id', required=True, help="Subject id")
parser.add_argument('-d', '--days', required=True, help="Day of study", type=int, nargs='+' )
parser.add_argument('-e', '--ecog_processed',
                        help='FFT extracted ecog file location')
parser.add_argument('-e_raw', '--ecog_raw',
                        help='Raw FFT location')
parser.add_argument('-dl', '--dl_raw', default=True,
                        help='Download raw files?')
#parser.add_argument('-r1', '--ratio1', help='First ratio pair', nargs=2, type=int)
#parser.add_argument('-r2', '--ratio2', help='Second ratio pair', nargs=2, type=int)
parser.add_argument('-save', '--save', help='save directory')
args = parser.parse_args()

for day in args.days:
    print "Download File day %i" % day
    subprocess.call("mkdir %s/%s" % (args.ecog_raw, args.sbj_id), shell=True)
    subprocess.call("mkdir %s/%s" % (args.ecog_processed, args.sbj_id), shell=True)
    subprocess.call("mkdir %s/%s" % (args.save, args.sbj_id),shell=True)
    subprocess.call("mkdir %s/%s/figures" % (args.save, args.sbj_id),shell=True)

    if args.dl_raw==True:
        subprocess.call("azure storage blob download main %s_%i.edf %s/%s/%s_%i.edf" %
                    (args.sbj_id, day, args.ecog_raw, args.sbj_id, args.sbj_id, day), shell=True)

    print "Extract fft"
    fft_extract.main(0.5,85,args.sbj_id, day, 1,0.5, "%s/%s/" %(args.ecog_raw, args.sbj_id),
                     "%s/%s/" %(args.ecog_processed, args.sbj_id))

print "Calculate and plot ratios"
for comp in range(2,8):
    for ratio1_0 in range(4,5,1):
        for ratio1_1 in range(ratio1_0+5, ratio1_0+6, 1):
            for ratio2_0 in range(25, 26, 3):
                for ratio2_1 in range(ratio2_0+30, ratio2_0+35, 5):
                    print "Processing %i:%i and %i:%i" %(ratio1_0, ratio1_1, ratio2_0, ratio2_1)
                    spec_ratio.main("%s/%s/" % (args.ecog_processed, args.sbj_id), args.sbj_id, args.days,
                                    (ratio1_0, ratio1_1), (ratio2_0, ratio2_1), "%s/%s/" %(args.save, args.sbj_id), comp)
                    #for day in args.days:
                    #    subprocess.call("avconv -start_number 1 -r 60 -i %s/%s/figures/%i_%%05d.png -vcodec mpeg4 %s/%s/%s_%i_ratios_%i_%i_%i_%i.avi"
                    #                % (args.save, args.sbj_id, day, args.save, args.sbj_id, args.sbj_id, day, ratio1_0, ratio1_1, ratio2_0, ratio2_1), shell=True)
                    subprocess.call("rm %s/%s/figures/*" % (args.save, args.sbj_id), shell=True)



