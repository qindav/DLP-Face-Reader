#!/usr/bin/env python

# Convenience script for debugging camera displays
# Matthew Kroesche
# ECEN 404

from cv2 import *
from DLPScanner.pi_camera import *
from DLPScanner.cv_camera import *

picam = PiCamera()
picam.set_resolution(640, 480)
cvcam = CVCamera(0)
cvcam.set_resolution(640, 480)
cvcam.set_n(5)

namedWindow('Pi Camera')
namedWindow('CV Camera')

while True:
    pi_im = picam.capture()
    cv_im = cvcam.capture()
    imshow('Pi Camera', pi_im)
    imshow('CV Camera', cv_im)
    key = waitKey(1)
    if key == 27:
        break
