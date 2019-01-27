# Camera/projector stereo functionality
# Matthew Kroesche
# ECEN 404

from cv2 import *
from ecen403.pi_camera import *
from ecen403.cv_camera import *


CAM_SIZE = (640, 480)     # The resolution of the camera image arrays, in pixels (width * height)
PROJ_SIZE = (320, 240)    # The resolution of the projector image arrays, in pixels (width * height)
SCREEN_SIZE = (1280, 800) # The resolution of the Raspberry Pi screen, in pixels (width * height)

BLACK_THRESH = None    # (Optional) The black threshold of the graycode
WHITE_THRESH = None    # (Optional) The white threshold of the graycode

PRE_DELAY = 100        # The delay (in milliseconds) between the graycode pattern updating and the image being captured
POST_DELAY = 100       # The delay (in milliseconds) after an image is captured

CB_SIZE = (7, 7)       # The size of the chessboard used in calibration
WIN_SIZE = (11, 11)    # The size of the search window used in calibration
SQUARE_SIZE = 1.0      # The unit size of the chessboard squares

CRITERIA = (TERM_CRITERIA_EPS | TERM_CRITERIA_MAX_ITER, 30, 0.001) # The criteria used in calibration


# Right now these are all None, but they can be updated after calibrate() has been called.
K1 = None # Intrinsic matrix of first camera
D1 = None # Distortion coefficients of first camera
K2 = None # Intrinsic matrix of second camera
D2 = None # Distortion coefficients of second camera
R = None  # Rotation matrix between two cameras
T = None  # Translation vector between two cameras






class OpenCV(object):

    def __init__(self, master):
        self.master = master



    def init(self):
        # Create the graycode patterns
        self.graycode = structured_light.GrayCodePattern_create(*PROJ_SIZE)
        retval, self.pattern = self.graycode.generate()
        assert retval, 'Error generating structured light patterns'
        black, white = self.graycode.getImagesForShadowMasks(None, None)
        self.pattern.extend((white, black))
        if WHITE_THRESH is not None:
            self.graycode.setWhiteThreshold(WHITE_THRESH)
        if BLACK_THRESH is not None:
            self.graycode.setBlackThreshold(BLACK_THRESH)
        # Initialize the cameras
        self.cam1 = PiCamera(CAM_SIZE)
        self.cam2 = CVCamera(0, CAM_SIZE, n=5) # because 6 is too many and 4 is too few
        self.clear_frames()
        # Initialize the projector
        namedWindow('projector')
        resizeWindow('projector', *PROJ_SIZE)
        # Rectify if calibration data already exists
        if K1 is not None:
            self.rectify(K1, D1, K2, D2, R, T)
        # Otherwise we need to call calibrate() first in this case.
        


    def quit(self):
        # Close the cameras and the projector
        self.cam1.close()
        self.cam2.close()
        destroyWindow('projector')


    def clear_frames(self):
        # Reset the capture frames
        self.frames1 = []
        self.frames2 = []


    def rectify(self, K1, D1, K2, D2, R, T):
        # Set up the calibration data
        R1, P1, R2, P2, self.Q, ROI1, ROI2 = stereoRectify(K1, D1, K2, D2, CAM_SIZE, R, T)
        self.map1x, self.map1y = initUndistortRectifyMap(K1, D1, R1, P1, CAM_SIZE, CV2_32FC1)
        self.map2x, self.map2y = initUndistortRectifyMap(K2, D2, R2, P2, CAM_SIZE, CV2_32FC1)



    def capture(self):
        # Capture a single image with both cameras
        waitKey(PRE_DELAY)
        frame1 = self.cam1.capture()
        frame1 = resize(frame1, CAM_SIZE)
        frame1 = cvtColor(frame1, COLOR_RGB2GRAY)
        self.frames1.append(frame1)
        frame2 = self.cam2.capture()
        frame2 = resize(frame2, CAM_SIZE)
        frame2 = cvtColor(frame2, COLOR_RGB2GRAY)
        self.frames2.append(frame2)
        waitKey(POST_DELAY)
            
        


    def snapshot(self):
        # Capture and process a sequence of stereo images
        self.clear_frames()
        for pattern in self.pattern:
            imshow('projector', pattern)
            self.capture()
        # Rectify the images
        for frame in self.frames1:
            remap(frame, self.map1x, self.map1y, INTER_NEAREST, frame, BORDER_CONSTANT)
        for frame in self.frames2:
            remap(frame, self.map2x, self.map2y, INTER_NEAREST, frame, BORDER_CONSTANT)
        patternImages = [self.frames1[:-2], self.frames2[:-2]]
        whiteImages = [self.frames1[-2], self.frames2[-2]]
        blackImages = [self.frames1[-1], self.frames2[-1]]
        # Decode and reconstruct the pointcloud
        retval, disparityMap = self.graycode.decode(patternImages, blackImages=blackImages, whiteImages=whiteImages)
        assert retval, 'Error decoding pattern images'
        pointcloud = reprojectImageTo3D(disparityMap, self.Q, handleMissingValues=True)
        return pointcloud




    def calibrate(self):
        # Calibrate the cameras
        self.clear_frames()
        namedWindow('cam1')
        resizeWindow('cam1', *CAM_SIZE)
        namedWindow('cam2')
        resizeWindow('cam2', *CAM_SIZE)
        objpoints = []
        grid = [(i*SQUARE_SIZE, j*SQUARE_SIZE, 0) for i in range(CB_SIZE[0]) for j in range(CB_SIZE[1])]
        imgpoints1 = []
        imgpoints2 = []
        # Capture a series of calibration images
        while True:
            print('Press any key to capture an image. Press [ESCAPE] to quit.')
            namedWindow('backdrop')
            resizeWindow('backdrop', *SCREEN_SIZE)
            retval = waitKey()
            if retval == 27:
                break # escape means we're done capturing
            self.capture()
            destroyWindow('backdrop')
            imshow('cam1', self.frames1[-1])
            imshow('cam2', self.frames2[-1])
            waitKey(1) # Update the images
            ret1, corners1 = findChessboardCorners(self.frames1[-1], CB_SIZE, None)
            if ret1:
                print('Found corners using camera #1.')
                ret2, corners2 = findChessboardCorners(self.frames2[-1], CB_SIZE, None)
                if ret2:
                    print('Found corners using camera #2.')
                    corners1 = cornerSubPix(self.frames1[-1], corners1, WIN_SIZE, (-1, -1), CRITERIA)
                    corners2 = cornerSubPix(self.frames2[-1], corners2, WIN_SIZE, (-1, -1), CRITERIA)
                    imgpoints1.append(corners1)
                    imgpoints2.append(corners2)
                    objpoints.append(grid[:])
                    frame1 = drawChessboardCorners(self.frames1[-1], CB_SIZE, corners1, ret1)
                    frame2 = drawChessboardCorners(self.frames2[-1], CB_SIZE, corners2, ret2)
                    imshow('cam1', frame1)
                    imshow('cam2', frame2)
                    waitKey(1) # Update the images
                    print('Successfully found %d calibration data points.' % len(objpoints))
                else:
                    print('Failed to find corners using camera #2.')
            else:
                print('Failed to find corners using camera #1.')
        # Clean up
        destroyWindow('cam1')
        destroyWindow('cam2')
        # Obtain calibration data
        retval, K1, D1, K2, D2, R, T, E, F = stereoCalibrate(objpoints, imgpoints1, imgpoints2, None, None, None, None, CAM_SIZE)
        assert retval, 'Error calibrating cameras'
        print('K1 =\n%r\n' % K1)
        print('D1 =\n%r\n' % D1)
        print('K2 =\n%r\n' % K2)
        print('D2 =\n%r\n' % D2)
        print('R =\n%r\n' % R)
        print('T =\n%r\n' % T)
        # Set up remap and perspective transform data needed by snapshot().
        self.rectify(K1, D1, K2, D2, R, T)
            
        




