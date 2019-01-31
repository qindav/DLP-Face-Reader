# Camera interface for OpenCV camera
# Matthew Kroesche
# ECEN 404

import cv2


class CVCamera(object):

    def __init__(self, id):
        self.cam = cv2.VideoCapture(id)
        assert self.cam.isOpened(), 'Error opening CV camera'

    def close(self):
        self.cam.release()

    def capture(self):
        for i in range(self.n):
            retval, im = self.cam.read()
            assert retval, 'Error capturing image with CV camera'
        return im

    def set_resolution(self, w, h):
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    def set_n(self, n):
        # n is the total number of times read() needs to be called
        # for each capture. You'd think it would always be 1, but for
        # the USB camera it's 5 for some screwy reason.
        self.n = n



