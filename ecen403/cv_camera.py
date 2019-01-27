# Camera interface for OpenCV camera
# Matthew Kroesche
# ECEN 404

import cv2


class CVCamera(object):

    def __init__(self, id, resolution, n):
        self.cam = cv2.VideoCapture(id)
        assert self.cam.isOpened(), 'Error opening CV camera'
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.n = n
        # n is the total number of times read() needs to be called
        # for each capture. You'd think it would always be 1, but for
        # the USB camera it's 5 for some screwy reason.

    def close(self):
        self.cam.release()

    def capture(self):
        for i in range(self.n):
            retval, im = self.cam.read()
            assert retval, 'Error capturing image with CV camera'
        return im



