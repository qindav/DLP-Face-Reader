# Camera/projector communication
# Matthew Kroesche
# ECEN 403

# This module has been superseded by cvstereo.py.

import cv2
import numpy
import picamera
import time


# The default picamera resolution (1920 by 1080) is way too big.
# Scale down by 3 in each dimension.
RESOLUTION = (640, 360)
DELAY = 0.05 # 20 fps
RED_SCALE = .299
GREEN_SCALE = .587
BLUE_SCALE = .114




class OpenCV(object):

    def __init__(self, master):
        self.master = master
        
    def init(self):
        # Set up the camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = RESOLUTION
        # Generate the projector patterns
        self.graycode = cv2.structured_light.GrayCodePattern_create(*RESOLUTION)
        retval, self.pattern = self.graycode.generate()
        assert retval, 'Error generating pattern'
        black, white = self.graycode.getImagesForShadowMasks(None, None)
        self.pattern.extend([black, white])
        # Create storage area for captured images
        w, h = RESOLUTION
        w = (((w-1)//32) + 1) * 32
        h = (((h-1)//16) + 1) * 16
        self.color = numpy.empty((h, w, 3), dtype=numpy.uint8)
        self.flat_color = self.color.ravel()
        self.images = numpy.empty((len(self.pattern), h, w), dtype=numpy.uint8)
        # Projector setup
        cv2.namedWindow('projector')
        cv2.resizeWindow('projector', *RESOLUTION)
        # Don't do this yet!!
        #cv2.setWindowProperty('projector', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # TODO: white/black thresholds, calibration
    
    def quit(self):
        # Close the camera now that we're done with it
        self.camera.close()
    
    def snapshot(self):
        # Capture a sequence of images using the camera and the projector
        for pattern, im in zip(self.pattern, self.images):
            cv2.imshow('projector', pattern)
            time.sleep(DELAY)
            self.camera.capture(self.flat_color, 'bgr')
            # Convert to grayscale and remap
            im[...] = (self.color[0]*RED_SCALE + self.color[1]*GREEN_SCALE + self.color[2]*BLUE_SCALE).round()
            cv2.remap(im, self.mapx, self.mapy, cv2.INTER_NEAREST, im)
        # Shadow processing
        cv2.remap(self.color, self.mapx, self.mapy, cv2.INTER_NEAREST, self.color)
        # Decode the captured images
        retval, disparityMap = self.graycode.decode(
            self.images[numpy.newaxis, :-2],
            blackImages = self.images[numpy.newaxis, -2],
            whiteImages = self.images[numpy.newaxis, -1],
            )
        assert retval, 'Error decoding images'
        # Convert to point cloud
        return cv2.reprojectImageTo3D(disparityMap, self.Q)
        

