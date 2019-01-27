# Camera interface for Raspberry Pi camera
# Matthew Kroesche
# ECEN 404

import numpy
import picamera
import picamera.array



class PiCamera(object):

    def __init__(self, resolution):
        self.cam = picamera.PiCamera()
        self.cam.resolution = resolution

    def close(self):
        self.cam.close()

    def capture(self):
        raw = picamera.array.PiRGBArray(self.cam)
        self.cam.capture(raw, format='bgr')
        return raw.array
