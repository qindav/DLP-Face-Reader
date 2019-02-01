#!/usr/bin/env python

# Camera calibration
# Matthew Kroesche
# ECEN 403

# This code is intended to be used in tandem with calibrate.py.
# It is used for calibrating a single camera; for stereo calibration
# see stereo_calibrate.py.

import picamera

print 'Setting up camera...'
cam = picamera.PiCamera()
cam.rotation = 180
cam.preview_fullscreen = False
cam.preview_window = (0, 50, 900, 900)
cam.start_preview()
print 'Done setting up.'

i = 1
while True:
    raw_input('Press [ENTER] to capture.')
    print 'Capturing image %d...' % i
    fname = '/home/pi/Desktop/calibration/image%d.jpg' % i
    cam.capture(fname)
    i += 1
