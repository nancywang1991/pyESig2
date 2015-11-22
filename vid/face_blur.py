#!/usr/bin/env python

import numpy as np
import cv2
import os
import sys
from pyESig2.util.error import varError
import pdb

# local modules
from pyESig2.vid.my_video_capture import my_video_capture
#from common import clock, draw_str

help_message = '''
USAGE: facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] [<video_source>]
'''

def detect(img, cascade, minNeigh):
   
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=minNeigh, minSize=(10, 10), flags = cv2.CASCADE_SCALE_IMAGE)
    
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def find_center_rect(rects, (c_x,c_y)):
    closest = (0,0,0,0)
    dist = 100000
    for x1, y1, x2, y2 in rects:
        center_x = (x1+x2+100)/2
        center_y = (y1+y2+100)/2
        cur_dist = np.sqrt((c_x-center_x)**2 + (c_y-center_y)**2)
        if cur_dist<dist:
            closest = (x1+25,y1+25,x2+75,y2+75)
            dist = cur_dist
    return closest

def face_blur(vid_src):

        #cascade_fn = "C:\\Python27\\lib\\site-packages\\pyESig\\vid\\haarcascades\\haarcascade_frontalface_alt.xml"
        
        #cascade = cv2.CascadeClassifier(cascade_fn)
        
        cam = my_video_capture(vid_src, 30)
        frame_cnt = 1
        
        while cam.has_next():
            img = cam.read()
            height, width, depth = img.shape
            #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #gray = cv2.equalizeHist(gray)
            min_neigh = 1
            #t = clock()
            # if frame_cnt%90==1:
            #     rects = detect(gray[50:-50,50:-50], cascade, min_neigh)
            #     rects = []
            #     # while len(rects) == 0 and cam.has_next():
            #     #     img_tmp = cam.read()
            #     #     height, width, depth = img_tmp.shape
            #     #     gray = cv2.cvtColor(img_tmp, cv2.COLOR_BGR2GRAY)
            #     #     gray = cv2.equalizeHist(gray)
            #     #     rects = detect(gray[50:-50,50:-50], cascade, min_neigh)
            #     cam.rewind_to(frame_cnt)
            #     img = cam.read()
            #     c_x = width/2
            #     c_y = height/2
            #     (x1,y1,x2,y2) = find_center_rect(rects, (c_x,c_y))
            x1 = 0
            x2 = 50
            y1 = 60
            y2 = 160
            sub_face = img[y1:y2, x1:x2]
            sub_face=cv2.GaussianBlur(sub_face, (23,23),15)
            img[y1:y2, x1:x2] = sub_face

            #cv2.imshow('facedetect', img)
            #pdb.set_trace()
            if 0xFF & cv2.waitKey(5) == 27:
                break
            cam.write(img, frame_cnt)
            frame_cnt += 1
            print frame_cnt
        fileName, fileExt = os.path.splitext(vid_src)
        cam.new_vid(fileName + "_2" + fileExt)
        cam.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    face_blur("D:\\NancyStudyData\\ecog\\raw\\e70923c4\\e70923c4_7\\e70923c4_7_0068_2.avi")