from pyESig2.vid.my_video_capture import my_video_capture
import cv2
import numpy as np
import pdb
__author__ = 'wangnxr'

def gen_cropped_frames(video_path, coords_path, save_path):

    cap = cv2.VideoCapture(video_path)
    fname = video_path.split('/')[-1].split('.')[0]
    fnum = fname.split("_")[-1]
    frame_count = 0
    coords = open(coords_path).readlines()
    total_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    if (cap.get(total_frames)-len(coords)) > 0:
        append_frame_skip = int(total_frames/(total_frames-len(coords)))
        for f in range(0,total_frames, append_frame_skip):
            coords.insert(f, coords[f])

    vid = my_video_capture(video_path, frame_rate=30)

    crop_coords_used = open("%s/%s/crop_coords.txt" % (save_path, fname), "wb")
    output_vid = my_video_capture(save_path, frame_rate=30, mode="write")

    if int(fnum) > 0:
        prev_fname = fname.split("_")[:-1]
        prev_fname.append(str(int(fnum)-1).zfill(4))
        prev_fname = "_".join(prev_fname)
        use_coord = np.array([int(n) for n in open("%s/%s/crop_coords.txt" % (save_path, prev_fname)).readlines()[-1].split(",")])
    else:
        use_coord = np.array([0,0,0,0])
    pdb.set_trace()
    while vid.has_next():
        frame = vid.read()
        cur_coord = np.array([int(n) for n in coords[frame_count].split(",")])
        diff = np.sum(np.abs(cur_coord-use_coord))
        if diff > 30:
            use_coord = cur_coord
        crop_coords_used.write("_".join([str(i) for i in use_coord]) + "\n")
        frame_count += 1
        if sum(use_coord) > 0:
            output_vid.write(frame[use_coord[2]:use_coord[3], use_coord[0]:use_coord[1]])
        else:
            output_vid.write(frame)
    output_vid.new_img_folder("%s/%s/images/" % (save_path, fname))
    output_vid.close()
    vid.close()


