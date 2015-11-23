from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import timeit
from matplotlib import cm
import gc

import ctypes
import _ctypes
import pygame
import sys
import pdb
import numpy as np
from skvideo.io import VideoWriter
import matplotlib.pyplot as plt
from multiprocessing import Process
from threading import Thread
import cPickle as pickle
import os
from matplotlib import image
import time
import matplotlib
import datetime

if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread

# colors for drawing different bodies
SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                  pygame.color.THECOLORS["blue"],
                  pygame.color.THECOLORS["green"],
                  pygame.color.THECOLORS["orange"],
                  pygame.color.THECOLORS["purple"],
                  pygame.color.THECOLORS["yellow"],
                  pygame.color.THECOLORS["violet"]]

sbj_folder = "E:\\nov22\\"
sbj_folder_store = r'C:\\Users\\UW CSE NSL\\Documents\\'

def process_frames(folder, vid_cnt, frame_list, body_list, time_list):
    start = time.time()
    if not os.path.isdir(folder):
        os.makedirs(folder)
    vid_file = folder + "video.avi"
    if os.path.exists(vid_file):
        os.remove(vid_file)
    out = VideoWriter(vid_file, fps=15, fourcc='H264', frameSize=(1920,1080))
    out.open()

    for d, frame in enumerate(frame_list):
        frame = frame_list[d]

        #dest_image = cv2.cvtColor(frame[:,:,:3], cv2.COLOR_BGR2RGB)
        out.write(frame[:,:,2::-1])
        #print "Finished video frame " + str(d) + " after " + str(time.time()-start) + " seconds\n"
        #image.imsave(folder + "\\" + str(d).zfill(4) + "_rgb.png", frame[:,:,:3])
    out.release()
    print "Finished video saving after " + str(time.time()-start) + " seconds\n"
    pickle.dump(body_list, open(folder + "\\body" + ".p", "wb"))
    print "Finished body saving after " + str(time.time()-start) + " seconds\n"
    pickle.dump(time_list, open(folder + "\\timestamps" + ".p", "wb"))

def process_depth(folder, vid_cnt, depth_list):
    start = time.time()
    if not os.path.isdir(folder):
        os.makedirs(folder)
    for d, depth in enumerate(depth_list):
        image.imsave(folder + "\\" + str(d).zfill(4) + ".png", depth, vmin=0, vmax=8000, cmap=cm.gray)
    print "Finished depth saving after " + str(time.time()-start) + " seconds\n"

class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect recording")

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color, body and depth frames
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                                       PyKinectV2.FrameSourceTypes_Body |
                                                       PyKinectV2.FrameSourceTypes_Depth)
                                                       #PyKinectV2.FrameSourceTypes_Audio)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data
        self._bodies = None



    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);

        # Right Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight);

        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft);

        # Right Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight);

        # Left Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft);


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()


    def run(self):
        # -------- Main Program Loop -----------

        last_video = pygame.time.get_ticks()
        vid_cnt = 0
        processes_vid = []
        processes_depth = []
        frame_list = []
        depth_list = []
        body_list = []
        time_list = []

        while not self._done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'],
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

            # --- Game logic should go here

            # --- Getting frames and drawing
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data



            if self._kinect.has_new_color_frame():
                pygame.time.wait(66-(pygame.time.get_ticks()-last_video))
                last_video = pygame.time.get_ticks()
                frame = self._kinect.get_last_color_frame()
                depth = self._kinect.get_last_depth_frame()
                self._bodies = self._kinect.get_last_body_frame()
                time_list.append(datetime.datetime.now())
                self.draw_color_frame(frame, self._frame_surface)
                src_image = np.reshape(frame, (1080,1920,4))
                src_depth = np.reshape(depth, (424, 512))
                frame_bodies = []
                if self._bodies is not None:
                    for i in range(0, self._kinect.max_body_count):
                        body = self._bodies.bodies[i]
                        if body.is_tracked:
                            frame_bodies.append(body.joints.contents)
                            body_list.append(frame_bodies)
                frame_list.append(src_image)
                depth_list.append(src_depth)


                if len(frame_list) > 15*10:
                    print "Processing Chunk #" + str(vid_cnt) + "\n"
                    folder = sbj_folder + str(vid_cnt).zfill(4) + "\\"
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                    processes_vid.append(Thread(target=process_frames, args=(folder, vid_cnt, frame_list, body_list,time_list,)))
                    processes_depth.append(Thread(target=process_depth, args=(folder, vid_cnt, depth_list,)))
                    processes_vid[-1].start()
                    processes_depth[-1].start()
                    if len(processes_vid)>50:
                        processes_vid.pop()
                    vid_cnt +=1
                    frame_list = []
                    depth_list = []
                    time_list = []
                    body_list=[]
                    gc.collect()
                frame = None

            if self._kinect.has_new_audio_frame():
                audio = self._kinect.get_last_audio_frame()


            # --- draw skeletons to _frame_surface
            if self._bodies is not None:
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked:
                        continue

                    joints = body.joints
                    # convert joint coordinates to color space
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.draw_body(joints, joint_points, SKELETON_COLORS[i])

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size)
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            #self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()
        print "Processing Chunk #" + str(vid_cnt) + "\n"
        folder = sbj_folder + str(vid_cnt).zfill(4) + "\\"
        if not os.path.isdir(folder):
            os.makedirs(folder)
        processes_vid.append(Thread(target=process_frames, args=(folder, vid_cnt, frame_list, body_list,time_list,)))
        processes_depth.append(Thread(target=process_depth, args=(folder, vid_cnt, depth_list,)))
        processes_vid[-1].start()
        processes_depth[-1].start()
        for p in processes_vid:
            p.join()
        for p in processes_depth:
            p.join()



if __name__== "__main__":
    game = BodyGameRuntime()
    game.run()
