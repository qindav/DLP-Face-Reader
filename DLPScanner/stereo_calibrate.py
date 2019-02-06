#!/usr/bin/env python

# Convenience script for stereo OpenCV calibration
# Matthew Kroesche
# ECEN 404

from DLPScanner.cvstereo import *
cv = OpenCV()
cv.init()
destroyWindow('projector')
cv.calibrate()
