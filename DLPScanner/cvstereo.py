# Camera/projector stereo functionality
# Matthew Kroesche
# ECEN 404

from numpy import *
from cv2 import *
from .pi_camera import *
from .cv_camera import *
import os

# This backend, which supports stereo calibration and capturing,
# has been designed to replace the broken backends opencv.py
# and pyimage.py.



# Macros and constants

CALIBRATION_PATH = '/home/pi/Desktop/stereo_calibration' # This is where the .npy format calibration results are saved.

IMAGE_PATH = '/home/pi/Desktop/stereo_captures' # This is where the .png format images are saved.
PCD_PATH = '/home/pi/Desktop' # This is where the .npy format pointcloud/disparity map is saved.
# (These are debug features, and should eventually be disabled as they waste precious time during processing.)

LOAD_IMAGES = True # Debug feature that, if set, loads images from stereo_captures folder rather than capturing them again.

CAM_SIZE = (640, 400)     # The resolution of the camera image arrays, in pixels (width * height)
PROJ_SIZE = (320, 200)    # The resolution of the projector image arrays, in pixels (width * height)
SCREEN_SIZE = (1280, 800) # The size of the actual screen. If this is not given it is assumed to be the same as PROJ_SIZE.

BLACK_THRESH = None    # (Optional) The black threshold of the graycode
WHITE_THRESH = None    # (Optional) The white threshold of the graycode

PRE_DELAY = 100        # The delay (in milliseconds) between the graycode pattern updating and the image being captured
POST_DELAY = 100       # The delay (in milliseconds) after an image is captured

CB_SIZE = (9, 7)       # The size of the chessboard used in calibration
WIN_SIZE = (11, 11)    # The size of the search window used in calibration
SQUARE_SIZE = 1.0      # The unit size of the chessboard squares

CRITERIA = (TERM_CRITERIA_EPS | TERM_CRITERIA_MAX_ITER, 30, 0.001) # The criteria used in calibration




# Data from calibration 2/6/2019

# Intrinsic matrix of first camera
K1 = array([[3.35352268e+02, 0.00000000e+00, 2.96520990e+02],
            [0.00000000e+00, 1.95760960e+03, 2.21613711e+02],
            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

# Distortion coefficients of first camera
D1 = array([[-0.48329117, -9.01649549,  0.08715038,  0.0470222 , 15.107458  ]])

# Intrinsic matrix of second camera
K2 = array([[ 1.34497282e+03,  0.00000000e+00, -1.12959734e+02],
            [ 0.00000000e+00,  3.97796121e+02,  1.52226040e+02],
            [ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])

# Distortion coefficients of second camera
D2 = array([[ 5.35864795e+00, -7.94115712e+02,  2.22187683e-01,  2.21337076e+00,  7.84735964e+03]])

# Rotation matrix between two cameras
R = array([[ 0.97237908, -0.05004974,  0.22797797],
           [ 0.11890107,  0.94672185, -0.29929964],
           [-0.20085186,  0.31813953,  0.92652349]])

# Translation vector between two cameras
T = array([[-1.40581396],
           [ 0.16046477],
           [ 2.12343594]])





# Stereo camera class


class OpenCV(object):

    def __init__(self, master=None):
        # self.master is unused and currently only exists for modularity purposes
        self.master = master



    def init(self):
        # Initialize the stereo camera setup
        # First, create the graycode patterns
        self.graycode = structured_light.GrayCodePattern_create(*PROJ_SIZE)
        retval, self.pattern = self.graycode.generate()
        assert retval, 'Error generating structured light patterns'
        black, white = self.graycode.getImagesForShadowMasks(None, None)
        self.pattern.extend((white, black))
        if WHITE_THRESH is not None:
            self.graycode.setWhiteThreshold(WHITE_THRESH)
        if BLACK_THRESH is not None:
            self.graycode.setBlackThreshold(BLACK_THRESH)
        # Resize the pattern images if necessary
        if SCREEN_SIZE and (SCREEN_SIZE != PROJ_SIZE):
            self.pattern = [resize(im, SCREEN_SIZE) for im in self.pattern]
        # Initialize the cameras
        self.cam1 = PiCamera()
        self.cam2 = CVCamera(0)
        self.cam1.set_resolution(*CAM_SIZE)
        self.cam2.set_resolution(*CAM_SIZE)
        self.cam2.set_n(5) # 5 "grabs" for every actual capture, for some reason or another.
        self.clear_frames()
        # Initialize the projector
        namedWindow('projector', WINDOW_NORMAL)
        setWindowProperty('projector', WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN)
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
        R1, R2, P1, P2, self.Q, ROI1, ROI2 = stereoRectify(K1, D1, K2, D2, CAM_SIZE, R, T)
        self.map1x, self.map1y = initUndistortRectifyMap(K1, D1, R1, P1, CAM_SIZE, CV_32FC1)
        self.map2x, self.map2y = initUndistortRectifyMap(K2, D2, R2, P2, CAM_SIZE, CV_32FC1)



    def capture(self):
        # Capture a single image with both cameras
        waitKey(PRE_DELAY)
        frame1 = self.cam1.capture()
        frame1 = resize(frame1, CAM_SIZE)
        frame1 = cvtColor(frame1, COLOR_BGR2GRAY)
        self.frames1.append(frame1)
        frame2 = self.cam2.capture()
        frame2 = resize(frame2, CAM_SIZE)
        frame2 = cvtColor(frame2, COLOR_BGR2GRAY)
        self.frames2.append(frame2)
        waitKey(POST_DELAY)
            
        


    def snapshot(self):
        # Capture and process a sequence of stereo images
        self.clear_frames()
        if LOAD_IMAGES:
            # Debugging ONLY: Load a sequence of previously captured images
            for fname in sorted(os.listdir(IMAGE_PATH)):
                im = imread(os.path.join(IMAGE_PATH, fname))
                if fname.startswith('cam1'):
                    self.frames1.append(im)
                elif fname.startswith('cam2'):
                    self.frames2.append(im)
            if not (self.frames1 and self.frames2):
                return None # Error signal: haven't previously captured anything
        else:
            # Capture a new sequence of images
            for pattern in self.pattern:
                imshow('projector', pattern)
                self.capture()
            # Save the images if necessary
            if IMAGE_PATH:
                for i, frame in enumerate(self.frames1):
                    path = os.path.join(IMAGE_PATH, 'cam1_image%.2d.png' % i)
                    print('Saving %s' % path)
                    imwrite(path, frame)
                for i, frame in enumerate(self.frames2):
                    path = os.path.join(IMAGE_PATH, 'cam2_image%.2d.png' % i)
                    print('Saving %s' % path)
                    imwrite(path, frame)
        # Rectify the images
        for frame in self.frames1:
            remap(frame, self.map1x, self.map1y, INTER_NEAREST, frame, BORDER_CONSTANT)
        for frame in self.frames2:
            remap(frame, self.map2x, self.map2y, INTER_NEAREST, frame, BORDER_CONSTANT)
        patternImages = [self.frames1[:-2], self.frames2[:-2]]
        whiteImages = [self.frames1[-2], self.frames2[-2]]
        blackImages = [self.frames1[-1], self.frames2[-1]]
        patternImages = numpy.array(patternImages)
        whiteImages = numpy.array(whiteImages)
        blackImages = numpy.array(blackImages)
        # Decode and reconstruct the pointcloud
        retval, disparityMap = self.graycode.decode(patternImages, blackImages=blackImages, whiteImages=whiteImages)
        if not retval:
            return None # Error signal
        disparityMap = numpy.float32(disparityMap)
        pointcloud = reprojectImageTo3D(disparityMap, self.Q, handleMissingValues=True)
        if PCD_PATH:
            numpy.save(os.path.join(PCD_PATH, 'disparity.npy'), disparityMap)
            numpy.save(os.path.join(PCD_PATH, 'pointcloud.npy'), pointcloud)
        # TODO: error checking
        return pointcloud




    def calibrate(self):
        # Calibrate the cameras
        self.clear_frames()
        namedWindow('cam1')
        namedWindow('cam2')
        # cam2 is physically to the left of cam1 when you're facing it, so put it to the left on the screen.
        moveWindow('cam2', 50, 50)
        moveWindow('cam1', 100+CAM_SIZE[0], 50)
        # Initialize the calibration result arrays
        objpoints = []
        grid = [(i*SQUARE_SIZE, j*SQUARE_SIZE, 0) for i in range(CB_SIZE[0]) for j in range(CB_SIZE[1])]
        imgpoints1 = []
        imgpoints2 = []
        waitKey(1) # Update the windows
        # Capture a series of calibration images
        while True:
            print('Press any key to capture an image. Press [ESCAPE] to finish calibrating.')
            # Camera preview loop
            while True:
                # Show the mirrored captures, since this behavior is more intuitive.
                imshow('cam1', self.cam1.capture()[:, ::-1])
                imshow('cam2', self.cam2.capture()[:, ::-1])
                retval = waitKey(1)
                if retval != -1:
                    break
            if retval == 27:
                break # escape means we're done capturing
            self.capture()
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
                    print('Successfully found %d calibration data points.' % len(objpoints))
                    print('Press any key to continue to the next capture. Press [ESCAPE] to finish calibrating.')
                    if waitKey() == 27:
                        break
                else:
                    print('Failed to find corners using camera #2.')
            else:
                print('Failed to find corners using camera #1.')
        # Clean up
        destroyWindow('cam1')
        destroyWindow('cam2')
        waitKey(1) # Delete windows on screen
        # Obtain calibration data
        if objpoints:
            objpoints = numpy.array(objpoints, numpy.float32)
            imgpoints1 = numpy.array(imgpoints1, numpy.float32)
            imgpoints2 = numpy.array(imgpoints2, numpy.float32)
            if CALIBRATION_PATH:
                print('Saving calibration capture results...')
                numpy.save(os.path.join(CALIBRATION_PATH, 'objpoints.npy'), objpoints)
                numpy.save(os.path.join(CALIBRATION_PATH, 'imgpoints1.npy'), imgpoints1)
                numpy.save(os.path.join(CALIBRATION_PATH, 'imgpoints2.npy'), imgpoints2)
        else:
            if CALIBRATION_PATH and os.listdir(CALIBRATION_PATH):
                # Use previously stored capture data if possible
                objpoints = numpy.load(os.path.join(CALIBRATION_PATH, 'objpoints.npy'))
                imgpoints1 = numpy.load(os.path.join(CALIBRATION_PATH, 'imgpoints1.npy'))
                imgpoints2 = numpy.load(os.path.join(CALIBRATION_PATH, 'imgpoints2.npy'))
            else:
                # Do nothing since the user didn't capture anything.
                print('No calibration information.')
                return
        # OpenCV calibration routine
        print('Calibrating...')
        retval, K1, D1, K2, D2, R, T, E, F = stereoCalibrate(objpoints, imgpoints1, imgpoints2, None, None, None, None, CAM_SIZE, flags=0)
        assert retval, 'Error calibrating cameras'
        print('K1 =\n%r\n' % K1)
        print('D1 =\n%r\n' % D1)
        print('K2 =\n%r\n' % K2)
        print('D2 =\n%r\n' % D2)
        print('R =\n%r\n' % R)
        print('T =\n%r\n' % T)
        # Set up remap and perspective transform data needed by snapshot().
        self.rectify(K1, D1, K2, D2, R, T)
            
        




