# Camera interface for Raspberry Pi camera
# Matthew Kroesche
# ECEN 404

# Used by cvstereo.py as a modular camera interface.

import numpy
import picamera
import picamera.array



class PiCamera(object):

    def __init__(self):
        self.cam = picamera.PiCamera()

    def close(self):
        self.cam.close()

    def capture(self):
        raw = picamera.array.PiRGBArray(self.cam)
        self.cam.capture(raw, format='bgr')
        return raw.array

    def set_resolution(self, w, h):
        self.cam.resolution = (w, h)
