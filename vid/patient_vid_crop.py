from pyESig2.vid.my_video_capture import my_video_capture
import cv2
import numpy as np
import pdb
import os
__author__ = 'wangnxr'

def gen_cropped_frames(video_path, coords_path, save_path):

    cap = cv2.VideoCapture(video_path)
    fname = video_path.split('/')[-1].split('.')[0]
    fnum = fname.split("_")[-1]
    frame_count = 0
    coords = open(coords_path).readlines()
    total_frames = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    if (total_frames-len(coords)) > 0:
        append_frame_skip = int(total_frames/(total_frames-len(coords)))
        for f in range(0,total_frames, append_frame_skip):
            coords.insert(f, coords[f])

    vid = my_video_capture(video_path, frame_rate=30)

    crop_coords_used = open("%s/%s/cropped/crop_coords.txt" % (save_path, fname), "wb")
    output_vid = my_video_capture(save_path, frame_rate=30, mode="write")

    prev_fname = fname.split("_")[:-1]
    prev_fname.append(str(int(fnum) - 1).zfill(4))
    prev_fname = "_".join(prev_fname)

    if os.path.exists("%s/%s/cropped/crop_coords.txt" % (save_path, prev_fname)):

        use_coord = np.array([int(n) for n in open("%s/%s/cropped/crop_coords.txt" % (save_path, prev_fname)).readlines()[-1].split(",")])
    else:
        use_coord = np.array([0,0,0,0])

    while vid.has_next():

        frame = vid.read()
        cur_coord = np.array([int(n) for n in coords[frame_count].split(",")])
        try:
            future_coords = [np.array([int(n) for n in coords[frame_count + f_offset].split(",")]) for f_offset in
                         xrange(5)]
        except IndexError:
            print "out of coords"

        diff = np.mean(np.sum(np.abs(future_coord-use_coord)) for future_coord in future_coords)
        if diff > 100:
            use_coord = cur_coord
        crop_coords_used.write(",".join([str(i) for i in use_coord]) + "\n")
        frame_count += 1
        if sum(use_coord) > 0:

            output_vid.write(frame[use_coord[2]:use_coord[3], use_coord[0]:use_coord[1]])

        else:
            output_vid.write(frame)

    output_vid.new_img_folder("%s/%s/cropped/" % (save_path, fname))
    output_vid.close()
    vid.close()

def gen_cropped_vid(video_path, coords_path, save_path):

    cap = cv2.VideoCapture(video_path)
    fname = video_path.split('/')[-1].split('.')[0]
    fnum = fname.split("_")[-1]
    frame_count = 0
    coords = open(coords_path).readlines()
    total_frames = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    if (total_frames-len(coords)) > 0:
        append_frame_skip = int(total_frames/(total_frames-len(coords)))
        for f in range(0,total_frames, append_frame_skip):
            coords.insert(f, coords[f])

    vid = my_video_capture(video_path, frame_rate=30)

    crop_coords_used = open("%s/%s.txt" % (save_path, fname), "wb")
    output_vid = my_video_capture(save_path, frame_rate=30, mode="write")

    prev_fname = fname.split("_")[:-1]
    prev_fname.append(str(int(fnum) - 1).zfill(4))
    prev_fname = "_".join(prev_fname)

    if os.path.exists("%s/%s/cropped/crop_coords.txt" % (save_path, prev_fname)):

        use_coord = np.array([int(n) for n in open("%s/%s/cropped/crop_coords.txt" % (save_path, prev_fname)).readlines()[-1].split(",")])
    else:
        use_coord = np.array([0,0,0,0])

    while vid.has_next():
        frame = vid.read()
        try:
            cur_coord = np.array([int(n) for n in coords[frame_count].split(",")])
            future_coords = [np.array([int(n) for n in coords[frame_count+f_offset].split(",")]) for f_offset in xrange(5)]
        except IndexError:
            pass
       
	diff = np.mean([np.sum(np.abs(future_coord-use_coord)) for future_coord in future_coords])
        if diff > 100:
            use_coord = cur_coord
        crop_coords_used.write(",".join([str(i) for i in use_coord]) + "\n")
        frame_count += 1

        if sum(use_coord) > 0:
            output_vid.write(cv2.resize(frame[use_coord[2]:use_coord[3], use_coord[0]:use_coord[1]], (256, 256)))
        else:
            output_vid.write(cv2.resize(frame, (256, 256)))
    output_vid.new_vid("%s/%s.mp4" % (save_path, fname))
    output_vid.close()
    vid.close()

