# Highlight-able menu in Pygame
#
# To run, use:
#     python pygame-menu-mouseover.py
#
# You should see a window with three grey menu options on it.  Place the mouse
# cursor over a menu option and it will become white.

import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pygame
import pygame.locals
import pyESig2.cluster.ratio_cluster as rc
import matplotlib.pyplot as plt
import pdb
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.cm as cm
from pyESig2.vid.vid_time import get_disconnected_times
from datetime import time, datetime, timedelta
from pyESig2.scripts.spectral_ratio_display import disconnected
import cPickle as pickle
import skvideo
import subprocess
import cv2
from pyESig2.vid.vid_start_end import get_disconnected_times
import os

class Marker:
    active = True

    def __init__(self, cluster_id, pos, screen_pos, time):
        self.cluster_id = cluster_id
        self.time = time
        self.pos = pos
        self.screen_pos = screen_pos

    def get_screen_pos(self):
        return self.screen_pos

    def set_screen_pos(self, new_pos):
        self.screen_pos = new_pos

    def set_cluster_id(self, c):
        self.cluster_id = c

    def get_time(self):
        return self.time

    def isActive(self):
        return self.active

class MouseButtons:
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5

def script_init(sbj_id, day, disconnect_file):
    labels, ratios, fig, pixel_points = rc.main(sbj_id, day)
    all_markers = {}
    start_time, end_time, start, end = get_disconnected_times(disconnect_file)

    for i in xrange(len(labels)):
        marker_cur = Marker(labels[i], ratios[i], pixel_points[i], start_time + timedelta(seconds=i))
        if int(pixel_points[i][0]) not in all_markers:
            all_markers[int(pixel_points[i][0])] = {}
        if int(pixel_points[i][1]) not in all_markers[int(pixel_points[i][0])]:
            all_markers[int(pixel_points[i][0])][int(pixel_points[i][1])] = []
        all_markers[int(pixel_points[i][0])][int(pixel_points[i][1])].append(marker_cur)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    window = pygame.display.set_mode((1400, 600), pygame.locals.DOUBLEBUF)
    screen = pygame.display.get_surface()

    size = canvas.get_width_height()

    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0,0))
    pygame.display.flip()
    return all_markers, screen

def text_objects(text, font):
    textSurface = font.render(text, True, (0,0,0))
    return textSurface, textSurface.get_rect()

def wait_screen(screen):
    largeText = pygame.font.Font('freesansbold.ttf',80)
    TextSurf, TextRect = text_objects("Recalculating", largeText)
    TextRect.center = ((800/2),(600/2))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()

def find_selected_marker(all_markers, mouse_pos):
    potentials = []
    for x in xrange(-4,5):
        for y in xrange(-4,5):
            if int(mouse_pos[0]+x) in all_markers and int(mouse_pos[1]+y) in all_markers[int(mouse_pos[0]+x)]:
                potentials.append([marker for marker in all_markers[int(mouse_pos[0]+x)][int(mouse_pos[1]+y)] if marker.isActive()])
    if len(potentials)>1:
        potentials = np.hstack(potentials)
        distance = [np.linalg.norm((mouse_pos[0]-potential.screen_pos[0], mouse_pos[1]-potential.screen_pos[1])) for potential in potentials]
        selected = potentials[np.argmin(distance)]
    else:
        try:
            selected = potentials[0][0]
        except IndexError:
            pdb.set_trace()

    return selected

def inactivate_markers(all_markers, cluster):
    for y_bin in all_markers.itervalues():
        for x_bin in y_bin.itervalues():
            for marker in x_bin:
                if not marker.cluster_id==cluster:
                    marker.active=False

def redraw(all_markers):
    colors = cm.rainbow(np.linspace(0, 1, 10))
    estimator = KMeans(10, n_init=10, max_iter=1000)
    positions = []
    for y_bin in all_markers.itervalues():
        for x_bin in y_bin.itervalues():
            for marker in x_bin:
                if marker.isActive():
                    positions.append(marker.pos)
    positions = np.array(positions)
    labels = estimator.fit_predict(positions)

    fig, pixel_points, ax = rc.cluster_scatter(labels, positions, colors, size=1000/float(len(labels)))
    width, height = fig.canvas.get_width_height()
    all_markers_new = {}

    for y_bin in all_markers.itervalues():
        for x_bin in y_bin.itervalues():
            for marker in x_bin:
                if marker.isActive():
                    screen_pos = ax.transData.transform(marker.pos[:2])
                    marker.set_screen_pos((screen_pos[0], height-screen_pos[1]))
                    marker.set_cluster_id(estimator.predict(marker.pos.reshape(1,-1)))
                    if int(marker.screen_pos[0]) not in all_markers_new:
                        all_markers_new[int(marker.screen_pos[0])] = {}
                    if int(marker.screen_pos[1]) not in all_markers_new[int(marker.screen_pos[0])]:
                        all_markers_new[int(marker.screen_pos[0])][int(marker.screen_pos[1])] = []
                    all_markers_new[int(marker.screen_pos[0])][int(marker.screen_pos[1])].append(marker)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    #window = pygame.display.set_mode((800, 600), pygame.locals.DOUBLEBUF)
    screen = pygame.display.get_surface()

    size = canvas.get_width_height()

    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0,0))
    pygame.display.flip()

    return all_markers_new

def display_image(selected, video_loc, vid_start_end, disconnect_file):
    start_time, end_time, start, end = get_disconnected_times(disconnect_file)
    video_starts = pickle.load(open("%s\%s_%i.p" % (vid_start_end, sbj_id, day), "rb"))
    if not disconnected(start, end, selected.time):
        vid_counter = len(video_starts)
        for i, video_start in enumerate(video_starts["start"]):
            if selected.time<=video_start:
                vid_counter=i-1
                break
        vid_time = (selected.time-video_starts["start"][vid_counter]).seconds

        subprocess.call("ffmpeg -ss %i -i %s/%s_%i_%04i.avi -t 1 -f image2 -update 1 tmp.png" % (vid_time, video_loc, sbj_id, day, vid_counter), shell=True)
    #window = pygame.display.set_mode((1400, 600), pygame.locals.DOUBLEBUF)
    screen = pygame.display.get_surface()

    surf = pygame.image.load("tmp.png")
    os.remove("tmp.png")
    screen.blit(surf, (600,0))
    pygame.display.update()



def main(sbj_id, day, vid_start_end, disconnect_fldr, video_loc):

    disconnect_file = "%s\\%s_%i.txt" % (disconnect_fldr, sbj_id, day)
    pygame.init()
    all_markers, screen = script_init(sbj_id, day, disconnect_file)
    while True:
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONUP and event.button==MouseButtons.LEFT:
                wait_screen(screen)
                selected = find_selected_marker(all_markers, pygame.mouse.get_pos())
                #pdb.set_trace()
                inactivate_markers(all_markers, selected.cluster_id)
                all_markers = redraw(all_markers)
                pygame.event.get()
            elif event.type == pygame.MOUSEBUTTONUP and event.button==MouseButtons.RIGHT:
                selected = find_selected_marker(all_markers, pygame.mouse.get_pos())
                display_image(selected, video_loc, vid_start_end, disconnect_file)

if __name__=="__main__":
    vid_start_end = "C:\\Users\\wangnxr\\Documents\\rao_lab\\video_analysis\\vid_real_time\\"
    disconnect_fldr = "C:/Users/wangnxr/Documents/rao_lab/video_analysis/disconnect_times/"
    video_loc = "E:/cb_7/"
    sbj_id = "cb46fd46"
    day = 7
    main(sbj_id, day, vid_start_end, disconnect_fldr,  video_loc)

