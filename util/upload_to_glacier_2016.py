import subprocess
import os

download_files=["aa97abcd", "aa97abcd_0728_kinect", "aa97abcd_0729_kinect", "aa97abcd_0730_kinect", "aa97abcd_0731_kinect", "aa97abcd_0801_kinect", "aa97abcd_vid", "af859cc5", "af859cc5_0331_kinect", "af859cc5_0401_kinect", "af859cc5_0402_kinect", "af859cc5_0403_kinect", "af859cc5_0404_kinect", "af859cc5_vid", "b4ac1725_vid.zip", "b4ac1726.zip", "bbd9a87e.zip", "bbd9a87e_vid.zip", "c7980193", "c7980193_0616_kinect", "c7980193_0617_kinect", "c7980193_0618_kinect", "c7980193_vid", "d49ed324", "d49ed324_0519_kinect", "d49ed324_0520_kinect", "d49ed324_0521_kinect", "d49ed324_0522_kinect", "d49ed324_0523_kinect", "d49ed324_vid", "ec168864", "ec168864_1020_kinect", "ec168864_1022_kinect", "ec168864_1023_kinect", "ec168864_1024_kinect", "ec168864_vid", "ec374ad0_0512_kinect", "ec374ad0_0513_kinect", "ec374ad0_0514_kinect", "ec374ad0_0515_kinect", "ec374ad0_0516_kinect", "ec374ad0_1", "ec374ad0_2", "ec374ad0_2_vid", "ec374ad0_vid", "ed019325", "ed019325_0819_kinect", "ed019325_0820_kinect", "ed019325_0821_kinect", "ed019325_vid", "f04f2d00", "f04f2d00_0825_kinect", "f04f2d00_0826_kinect", "f04f2d00_0827_kinect", "f04f2d00_0828_kinect", "f04f2d00_vid", "f3b79359", "f3b79359_0922_kinect", "f3b79359_0923_kinect", "f3b79359_0924_kinect", "f3b79359_0925_kinect", "f3b79359_0926_kinect", "f3b79359_vid", "f64993a3", "f64993a3_vid"]
keep_file = ["a86a4375_vid", "d7d5f068_vid"]

for file in download_files:
	subprocess.call("azure storage blob download ecog2016v2 %s /mnt/%s" % (file, file), shell=True)
	subprocess.call("glacier-cmd upload ecog-video /mnt/%s" % file, shell=True)
	#if not file in keep_file:
		#os.remove("/mnt/%s" % file)
		


