#!/usr/bin/env python

# Convenience script for stereo OpenCV calibration
# Matthew Kroesche
# ECEN 404

from ecen403.cvstereo import *
cv = OpenCV()
cv.init()
cv.calibrate()
