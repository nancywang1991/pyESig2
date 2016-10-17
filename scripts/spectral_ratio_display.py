__author__ = 'wangnxr'
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
from pyESig2.vid.vid_time import get_disconnected_times
from datetime import time, datetime, timedelta
from pyESig2.vid.my_video_capture import my_video_capture
import pickle
import cv2
import pdb

def plot_2d_coords(result, ratio1, ratio2, save_fldr, day, start_time, duration, type="fast"):
    #samples = np.random.choice(len(result), 0.2*len(result))
    #plt.scatter(result[samples,0], result[samples,1], s=0.01)

    x = np.arange(6)
    ys = [i+x+(i*x)**2 for i in range(150)]
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    count = 0

    f, ax = plt.subplots(1,1, sharex='col', figsize=(6,6))
    scatterplots = []
    for m_s in range(150):
        scatterplots.append(ax.scatter(result[m_s:m_s+1,0], result[m_s:m_s+1,1], s=2, c=colors[m_s], edgecolors="face"))

    ax.set_title("Time %02i:%02i:%02i" % (start_time.hour, start_time.minute, start_time.second))
    ax.set_ylim([-3,3])
    ax.set_xlim([-3,3])
    ax.set_xlabel("Ratio %i:%i Hz" %(ratio1[0], ratio1[1] ))
    ax.set_ylabel("Ratio %i:%i Hz" %(ratio2[0], ratio2[1] ))
    #plt.tight_layout()
    f.savefig("%s/%i_%05d.png" % (save_fldr, day, count))

    for m in range(0,duration-150,1):
        cur_time = start_time + timedelta(seconds=(m+150))
        ax.set_title("Time %02i:%02i:%02i" % (cur_time.hour, cur_time.minute, cur_time.second))
        if m%60==0:
            print "At time %02i:%02i:%02i" % (cur_time.hour, cur_time.minute, cur_time.second)
        if type == "fast":
            scatterplots[0].remove()
            scatterplots.pop(0)
            scatterplots.append(ax.scatter(result[m+150:m+151,0], result[m+150:m+151,1], s=2, c=colors[m%150], edgecolors="face"))
        else:
            scatterplots = []
            for m_s in range(m, m+150):
                scatterplots.append(ax.scatter(result[m_s:m_s+1,0], result[m_s:m_s+1,1], s=2, c=colors[m_s-m], edgecolors="face"))
        f.savefig("%s/%i_%05d.png" % (save_fldr, day, count))
        count += 1
    plt.close('all')
    plt.clf()

def concat_images(imga, imgb):
    """
    Combines two color image ndarrays side-by-side.
    """
    ha,wa = imga.shape[:2]
    hb,wb = imgb.shape[:2]
    max_height = np.max([ha, hb])
    total_width = wa+wb
    new_img = np.zeros(shape=(max_height, total_width, 3), dtype=np.uint8)
    new_img[:ha,:wa]=imga
    new_img[:hb,wa:wa+wb]=imgb
    return new_img

def disconnected(starts, ends, cur_time):
    for i in xrange(len(starts)):
        if cur_time >= starts[i] and cur_time <= ends[i]:
            return True
    return False

def main(sbj_id, day, result, video_loc, disconnect_file, save_fldr, comp):
    img_fldr = "%s/images" % save_fldr
    img_fldr_final = "%s/images_final" % save_fldr
    if not os.path.exists(img_fldr):
        os.makedirs(img_fldr)
    if not os.path.exists(img_fldr_final):
        os.makedirs(img_fldr_final)
    start_time, end_time, start, end = get_disconnected_times(disconnect_file)
    duration = 60*40
    video_starts = pickle.load(open("C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\%s_%i.p" % (sbj_id, day), "rb"))

    plot_2d_coords(result, (4,9), (25,55), img_fldr, day, start_time, duration, type="fast")

    for i, video_start in enumerate(video_starts["start"]):
        if (start_time+timedelta(seconds=150))<=video_start:
            vid_counter=i-1
            break
    frame_counter=(start_time+timedelta(seconds=150)-video_starts["start"][vid_counter]).seconds+1

    cur_vid = my_video_capture("%s/%s_%i_%04i.avi" %(video_loc, sbj_id, day, vid_counter), 1)
    movie = my_video_capture(img_fldr_final, 20, mode="write")
    for s in range(0,duration-150,1):
        plot = cv2.imread("%s/%i_%05d.png" % (img_fldr, day, s))
        cur_time = start_time + timedelta(seconds=(s+150))
        if not disconnected(start, end, cur_time):
            if vid_counter < len(video_starts["start"]) and cur_time >= video_starts["start"][vid_counter+1]:
                vid_counter += 1
                frame_counter = 1
                cur_vid.close()
                cur_vid = my_video_capture("%s/%s_%i_%04i.avi" %(video_loc, sbj_id, day, vid_counter), 1)
            cur_vid.forward_to(frame_counter)
            frame = cur_vid.read()
            frame_counter += 1
        else:
            frame = np.zeros((480,640,3), np.uint8)
        concat = concat_images(plot, frame)
        movie.write(concat)
    cur_vid.close()
    movie.new_vid("%s/movie_comp%i_for_bing.avi" % (save_fldr, comp))
    movie.close()

if __name__ == "__main__":
    sbj_id = "cb46fd46"
    day = 7
    result_fldr = "E:/ratio_mapping/visualizations/"
    for comp in range(0,1):
        result = pickle.load(open("%s/%s_%i_ratio_multi_day_4_9_25_55_comp_%i.p" % (result_fldr, sbj_id, day, comp)))
        disconnect_file = "C:/Users/wangnxr/Documents/rao_lab/video_analysis/disconnect_times/%s_%i.txt" % (sbj_id, day)
        video_loc = "E:/cb_7/"
        main(sbj_id, day, result, video_loc, disconnect_file, result_fldr, comp)





