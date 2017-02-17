import subprocess
import os
import pdb

download_files = ["a86a4375_vid", "a0f66459_vid", "ab2431d9_vid", "c95c1e82_vid", "cb46fd46_vid", "d6532718_vid", "d7d5f068_vid", "e5bad52f_vid", "e70923c4_vid", "fcb01f7a_pt1_vid", "fcb01f7a_pt2_vid", "fcb01f7a_pt3_vid", "ffb52f92_vid", "a0f66459", "a86a4375", "ab2431d9", "c95c1e82", "cb46fd46", "d6532718", "d7d5f068", "e5bad52f", "e70923c4", "fcb01f7a", "ffb52f92"]


keep_file = ["a86a4375_vid", "d7d5f068_vid"]

download_files = ["a86a4375_vid", "d7d5f068_vid", "a0f66459", "a86a4375", "ab2431d9", "c95c1e82", "cb46fd46", "d6532718", "d7d5f068", "e5bad52f", "e70923c4", "fcb01f7a", "ffb52f92"]

for file in download_files:
	subprocess.call("azure storage blob download ecog2015 %s /mnt/%s" % (file, file), shell=True)
        #pdb.set_trace()
	subprocess.call("glacier-cmd upload ecog-video /mnt/%s" % file, shell=True)
	#if not file in keep_file:
	#	os.remove("/mnt/%s" % file)
		


