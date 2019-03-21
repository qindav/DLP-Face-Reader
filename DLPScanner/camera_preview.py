#!/usr/bin/env python

# Convenience script for debugging camera displays
# Matthew Kroesche
# ECEN 404

from DLPScanner.cvstereo import *
cv = OpenCV()
cv.init()
destroyWindow('projector')
cv.start_preview()
while True:
    key = cv.update()
    if key == 27: # [ESCAPE]
        cv.end_preview()
        break
