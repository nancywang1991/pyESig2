#!/usr/bin/env python

import numpy as np
import cv2
import os
import pdb

# local modules
from pyESig.vid.my_video_capture import my_video_capture
#from common import clock, draw_str

help_message = '''
USAGE: facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] [<video_source>]
'''

def detect(img, cascade):
   
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=1, minSize=(2, 2), flags = cv2.CASCADE_SCALE_IMAGE)
    
    
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
        center_x = (x1+x2)/2
        center_y = (y1+y2)/2
        cur_dist = np.sqrt((c_x-center_x)**2 + (c_y-center_y)**2)
        if cur_dist<dist:
            closest = (x1,y1,x2,y2)
            dist = cur_dist
    return closest

def crop_face(cascades, img):
    rects = []
    
    height, width, depth = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    for cascade in cascades:
        rect = detect(gray, cascade)
        if (len(rect)>0):
            rects.append(rect)
    if (len(rects)>0):
        rect_final = np.vstack(tuple(rects))
        c_x = width/2
        c_y = height/2
        (x1,y1,x2,y2) = find_center_rect(rect_final, (c_x,c_y))
        #draw_rects(img, rects, (255, 0,0))
        face_im = img[y1:y2,x1:x2]
        #face_im = cv2.resize(img[y1:y2,x1:x2], (32,32))
        face_im = cv2.cvtColor(face_im, cv2.COLOR_BGR2GRAY)
        face_im = cv2.equalizeHist(face_im)

        #cv2.imshow('facedetect', img)
        
##        if 0xFF & cv2.waitKey(5) == 27:
##            break
        #cv2.imwrite("D:\\NancyStudyData\\face\\fcb01f7a_9\\" + num + "_" + str(frame_cnt) + ".png", face_im)
        return (True, face_im)
    else:
        return (False, gray)

def crop_eyes(cascades, img):
    rects = []
    
    height, width = img.shape
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(img)
    
    for cascade in cascades:
        rect = detect(gray, cascade)
        if (len(rect)>0):
            rects.append(rect)
    if (len(rects)>0):
        
        rect_final = np.vstack(tuple(rects))
        c_x = width/2
        c_y = height/2
        (x1,y1,x2,y2) = find_center_rect(rect_final, (c_x,c_y))
        #for rect in rects:
        #   draw_rects(img, rect, (255, 0,0))
        
        eye_im = cv2.resize(img[y1:y2,x1:x2], (32,32))
        #face_im = cv2.cvtColor(face_im, cv2.COLOR_BGR2GRAY)
        #face_im = cv2.equalizeHist(face_im)

        #cv2.imshow('facedetect', img)       
        #cv2.waitKey()
        #pdb.set_trace()
        #cv2.imwrite("D:\\NancyStudyData\\face\\fcb01f7a_9\\" + num + "_" + str(frame_cnt) + ".png", face_im)
        return (True, eye_im)
    else:
        return (False, gray)


sbj_ids = ['ad4ae8f3', 'a9e06539', 'b3c91874', 'bfb65b46', 'd5378b46', 'deb4cf78', 'e1556efa', 'ea430431']
sbj_ids = ['a86a4375']
days = ['2']

for day in days:
    for sbj_id in sbj_ids:
        if not os.path.isdir("D:\\face\\" + sbj_id + "_"+ day + "\\"):
            os.makedirs("D:\\face\\" + sbj_id + "_"+ day + "\\")
        if __name__ == '__main__':
            import sys, getopt
            print help_message
            for n in range(125,500):
                
                num = str(n).zfill(4)
                sys.argv = ["C:\\Python27\\lib\\site-packages\\pyESig\\vid\\face_detect.py",\
                            "D:\\NancyStudyData\\ecog\\raw\\" + sbj_id + "\\" + sbj_id + "_"+ day + "\\" + sbj_id + "_"+ day + "_" + num + ".avi"]
                            #"E:\\NancyStudyData2\\raw\\cb46fd46\\cb46fd46_5\\cb46fd46_5_" + num + ".avi"]
                            #"E:\\fcb01f7a_9\\Sikes~Kaitlin_5c0e5194-475e-415b-951b-dbc2e4cc8d18_" + num + ".avi"]
                args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
                try:
                    video_src = video_src[0]
                except:
                    video_src = 0
                args = dict(args)
                cascade_fns = []
                cascades = []
                cascade_fns.append(args.get('--cascade',
                        "C:\\Python27\\lib\\site-packages\\pyESig\\vid\\haarcascades\\haarcascade_frontalface_alt.xml"))
                cascade_fns.append(args.get('--cascade',
                        "C:\\Python27\\lib\\site-packages\\pyESig\\vid\\haarcascades\\haarcascade_profileface.xml"))
                nested_fn  = args.get('--cascade', "C:\\Python27\\lib\\site-packages\\pyESig\\vid\\haarcascades\\haarcascade_eye.xml")
                #cascade_fn  = args.get('--cascade', "C:\\Python27\\lib\\site-packages\\pyESig\\vid\\haarcascades\\Mouth.xml")

                for cascade_fn in cascade_fns:
                    cascades.append(cv2.CascadeClassifier(cascade_fn))
                nested = cv2.CascadeClassifier(nested_fn)
                
                cam = my_video_capture(video_src, 4)
                frame_cnt = 0
                while cam.has_next():
                    print "video:" + str(n) + " || frame:" + str(frame_cnt)
                    faces = []
                    for i in xrange(4):
                        if cam.has_next():
                            img = cam.read()
                            detected, face = crop_face(cascades,img)
                            face = cv2.resize(face, (32,32))
                            if (detected == True):
                                faces.append(face)
                    if(len(faces) > 3 ):
                        cv2.imwrite("D:\\face\\" + sbj_id + "_" + day + "\\" + num + "_" + str(frame_cnt) + "_1.png", faces[0])
                        cv2.imwrite("D:\\face\\" + sbj_id + "_" + day + "\\" + num + "_" + str(frame_cnt) + "_2.png", faces[1])
                        cv2.imwrite("D:\\face\\" + sbj_id + "_" + day + "\\" + num + "_" + str(frame_cnt) + "_3.png", faces[2])
                        cv2.imwrite("D:\\face\\" + sbj_id + "_" + day + "\\" + num + "_" + str(frame_cnt) + "_4.png", faces[3])
                    frame_cnt += 1                        
                cam.close()
                cv2.destroyAllWindows()

