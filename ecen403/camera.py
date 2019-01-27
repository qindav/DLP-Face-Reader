# Pi camera class that behaves like an OpenCV VideoCapture object
# Matthew Kroesche
# ECEN 404

import numpy
import picamera
import picamera.array




class PiVideoCapture(object):

    # Convenience class to emulate the behavior of an
    # OpenCV camera that uses the Raspberry Pi camera ribbon

    def __init__(self, resolution=None):
        self.cam = picamera.PiCamera()
        if resolution is not None:
            self.cam.resolution = resolution

    def __del__(self):
        self.cam.close()

    def isOpened(self):
        return not self.cam.closed

    def release(self):
        self.cam.close()

    def read(self):
        raw = picamera.array.PiRGBArray(self.cam)
        try:
            self.cam.capture(raw, format='bgr')
        except:
            return False, None
        return True, raw.array

