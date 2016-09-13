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

    def get_time(self):
        return self.time

    def get_img(self):
        return img

    def isActive(self):
        return self.active


def script_init():
    labels, ratios, fig, pixel_points = rc.main()
    all_markers = {}
    for i in xrange(len(labels)):
        marker_cur = Marker(labels[i], ratios[i], pixel_points[i])
        if int(pixel_points[i][0]) not in all_markers:
            all_markers[int(pixel_points[i][0])] = {}
        if int(pixel_points[i][1]) not in all_markers[int(pixel_points[i][0])]:
            all_markers[int[pixel_points][i][0]][int[pixel_points][i][1]] = []
        all_markers[int[pixel_points][i][0]][int[pixel_points][i][1]].append()
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    window = pygame.display.set_mode((800, 600), pygame.locals.DOUBLEBUF)
    screen = pygame.display.get_surface()

    size = canvas.get_width_height()

    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0,0))
    pygame.display.flip()

pygame.init()
script_init()
while True:
    pass