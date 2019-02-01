#!/usr/bin/env python

# Script to capture images used for Charuco calibration
# Matthew Kroesche
# ECEN 403

# This script is intended to be used in tandem with charuco_capture.py.
# It captures a sequence of images of a special Aruco calibration board
# with a circle grid projected onto it.
# See stereo_calibrate.py and cvstereo.py for code to calibrate two
# cameras to each other

import pygame
import picamera
import time
import os


# Constants
GRID_SIZE = (7, 6)
NUM_IMAGES = 20
TIME_DELTA = 1.0 # seconds
CALIBRATION_DIR = '/home/pi/Desktop/charuco_calibration'
RESOLUTION = (1920, 1080) # pixels
SCREEN_SIZE = (455, 390) # pixels
SCREEN_DELTA = (455, 0)  # pixels


# Generator function for the camera
def generate():
    for i in range(1, NUM_IMAGES+1):
        # "Flash" effect
        screen.fill((255, 255, 255))
        pygame.display.flip()
        time.sleep(0.1)
        screen.fill((0, 0, 0))
        screen.blit(surface, (xo, yo))
        pygame.display.flip()
        # Wait before capture
        time.sleep(TIME_DELTA)
        for e in pygame.event.get():
            if (e.type == pygame.KEYDOWN) and (e.key == pygame.K_ESCAPE):
                return
        yield os.path.join(CALIBRATION_DIR, 'image%.3d.png' % i)


# Draw the circles on the screen
pygame.display.init()
screen = pygame.display.set_mode((0, 0))
pygame.mouse.set_visible(False)
surface = pygame.Surface(SCREEN_SIZE)
w, h = SCREEN_SIZE
for i in range(w//(GRID_SIZE[0]*2), w, w//GRID_SIZE[0]):
    for j in range(h//(GRID_SIZE[1]*2), h, h//GRID_SIZE[1]):
        pygame.draw.circle(surface, (255, 255, 255), (i, j), w//(GRID_SIZE[0]*6))
xo = (screen.get_width ()-w)//2 + SCREEN_DELTA[0]
yo = (screen.get_height()-h)//2 + SCREEN_DELTA[1]
screen.blit(surface, (xo, yo))
pygame.display.flip()


# Open the camera and start capturing
cam = picamera.PiCamera()
cam.resolution = RESOLUTION
cam.capture_sequence(generate(), 'png', use_video_port=True)

# Finish
cam.close()
pygame.display.quit()
