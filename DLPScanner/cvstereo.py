# Camera/projector stereo functionality
# Matthew Kroesche
# ECEN 404

from numpy import *
from cv2 import *
import os

from .pi_camera import *
from .cv_camera import *
from .pcd import *
from .bench import *

# This backend, which supports stereo calibration and capturing,
# has been designed to replace the broken backends opencv.py
# and pyimage.py.

Bench.on = False # Disable benchmarking



# Macros and constants

CALIB_PATH = None # This is where the .png format calibration images and
# .npy format calibration results are saved.
CAPTURE_PATH = None # This is where the .png format captured images and
# .npy format pointcloud/disparity data are saved.
# (These are debug features, and should ultimately be disabled as they waste precious time.)

REUSE_CALIB_DATA   = False # Debug feature that, if set, loads images from CALIB_PATH rather than capturing them again
REUSE_CAPTURE_DATA = False # Debug feature that, if set, loads images from CAPTURE_PATH folder rather than capturing them again.

CAM_SIZE = (640, 400)     # The resolution of the camera image arrays, in pixels (width * height)
PROJ_SIZE = (320, 200)    # The resolution of the projector image arrays, in pixels (width * height)
SCREEN_SIZE = (1280, 800) # The size of the actual screen. If this is not given it is assumed to be the same as PROJ_SIZE.

BLACK_THRESH = None    # (Optional) The black threshold of the graycode
WHITE_THRESH = None    # (Optional) The white threshold of the graycode

PRE_DELAY = 50         # The delay (in milliseconds) between the graycode pattern updating and the image being captured
POST_DELAY = 20        # The delay (in milliseconds) after an image is captured

CB_SIZE = (7, 9)       # The size of the chessboard used in calibration
WIN_SIZE = (11, 11)    # The size of the search window used in calibration
SQUARE_SIZE = 1.0      # The unit size of the chessboard squares

CRITERIA = (TERM_CRITERIA_EPS | TERM_CRITERIA_MAX_ITER, 30, 0.001) # The criteria used in calibration

COORD_THRESH = 100     # Threshold for pointcloud distance from the origin

SHOW_PREVIEW = False  # Debug feature that displays a preview of the camera on screen
MIRROR_PREVIEW = True # Toggles whether or not the preview is mirrored




# Data from calibration 2/8/2019

# Intrinsic matrix of first camera
K1 = \
array([[506.02714246,   0.        , 327.43869217],
       [  0.        , 506.83558152, 208.42300576],
       [  0.        ,   0.        ,   1.        ]])

# Distortion coefficients of first camera
D1 = \
array([[ 0.14277543, -0.04825507,  0.00326943,  0.00599028, -0.53504333,
         0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.        ,  0.        ]])

# Intrinsic matrix of second camera
K2 = \
array([[472.29697008,   0.        , 325.2902712 ],
       [  0.        , 393.04568793, 192.66877657],
       [  0.        ,   0.        ,   1.        ]])

# Distortion coefficients of second camera
D2 = \
array([[-0.45360399,  0.33141038, -0.00127511, -0.00568173, -0.1871959 ,
         0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
         0.        ,  0.        ,  0.        ,  0.        ]])

# Rotation matrix between two cameras
R = \
array([[ 0.96130185,  0.27394812, -0.02917519],
       [-0.27518946,  0.95983298, -0.05469372],
       [ 0.01302007,  0.06060588,  0.99807685]])

# Translation vector between two cameras
T = \
array([[-1.95912708],
       [ 0.60067235],
       [-0.1080526 ]])






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
        self.cam2.set_n(5) # 5 "grabs" for every actual capture, for some reason or another.
        self.cam1.set_resolution(*CAM_SIZE)
        self.cam2.set_resolution(*CAM_SIZE)
        self.clear_frames()
        # Initialize the projector
        if not REUSE_CAPTURE_DATA:
            namedWindow('projector', WINDOW_NORMAL)
            setWindowProperty('projector', WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN)
            waitKey(1)
        # Rectify if calibration data already exists
        if K1 is not None:
            self.rectify(K1, D1, K2, D2, R, T)
        # Otherwise we need to call calibrate() first in this case.
        # Set up the preview
        self.has_preview = self.mirrored_preview = False
        if SHOW_PREVIEW:
            self.start_preview(MIRROR_PREVIEW)
        


    def quit(self):
        # Close the cameras and the projector
        self.cam1.close()
        self.cam2.close()
        self.end_preview()
        if not REUSE_CAPTURE_DATA:
            destroyWindow('projector')


    def clear_frames(self):
        # Reset the capture frames
        self.frames1 = []
        self.frames2 = []
        self.rect1 = []
        self.rect2 = []


    def rectify(self, K1, D1, K2, D2, R, T):
        # Set up the calibration data
        R1, R2, P1, P2, self.Q, (x1, y1, w1, h1), (x2, y2, w2, h2) = stereoRectify(K1, D1, K2, D2, CAM_SIZE, R, T)
        self.map1x, self.map1y = initUndistortRectifyMap(K1, D1, R1, P1, CAM_SIZE, CV_32FC1)
        self.map2x, self.map2y = initUndistortRectifyMap(K2, D2, R2, P2, CAM_SIZE, CV_32FC1)
        self.roi1 = (slice(y1, y1+h1), slice(x1, x1+w1))
        self.roi2 = (slice(y2, y2+h2), slice(x2, x2+y2))



    def capture(self):
        # Capture a single image with both cameras
        self.pause_preview()
        with Bench('PRE_DELAY'):
            waitKey(PRE_DELAY)
        with Bench('Left camera capture'):
            frame1 = self.cam1.capture()
        with Bench('Resize'):
            frame1 = resize(frame1, CAM_SIZE)
        with Bench('Convert'):
            frame1 = cvtColor(frame1, COLOR_BGR2GRAY)
        with Bench('Append'):
            self.frames1.append(frame1)
        with Bench('Right camera capture'):
            frame2 = self.cam2.capture()
        with Bench('Resize'):
            frame2 = resize(frame2, CAM_SIZE)
        with Bench('Convert'):
            frame2 = cvtColor(frame2, COLOR_BGR2GRAY)
        with Bench('Append'):
            self.frames2.append(frame2)
        with Bench('POST_DELAY'):
            waitKey(POST_DELAY)
        self.resume_preview()
            
        


    def snapshot(self):
        # Capture and process a sequence of stereo images
        with Bench('Total processing time'):
            self.clear_frames()
            if REUSE_CAPTURE_DATA:
                # Debugging ONLY: Load a sequence of previously captured images
                for fname in sorted(os.listdir(CAPTURE_PATH)):
                    im = imread(os.path.join(CAPTURE_PATH, fname))
                    if fname.startswith('left'):
                        im = cvtColor(im, COLOR_BGR2GRAY)
                        self.frames1.append(im)
                    elif fname.startswith('right'):
                        im = cvtColor(im, COLOR_BGR2GRAY)
                        self.frames2.append(im)
                if not (self.frames1 and self.frames2):
                    return None # Error signal: haven't previously captured anything
            else:
                # Capture a new sequence of images
                for pattern in self.pattern:
                    imshow('projector', pattern)
                    self.capture()
                # Save the images if necessary
                if CAPTURE_PATH:
                    for i, frame in enumerate(self.frames1):
                        path = os.path.join(CAPTURE_PATH, 'left%.2d.png' % i)
                        print('Saving %s' % path)
                        imwrite(path, frame)
                    for i, frame in enumerate(self.frames2):
                        path = os.path.join(CAPTURE_PATH, 'right%.2d.png' % i)
                        print('Saving %s' % path)
                        imwrite(path, frame)
            # Rectify the images
            for frame in self.frames1:
                rect = remap(frame, self.map1x, self.map1y, INTER_NEAREST, None, BORDER_CONSTANT)
                self.rect1.append(rect)
            for frame in self.frames2:
                rect = remap(frame, self.map2x, self.map2y, INTER_NEAREST, None, BORDER_CONSTANT)
                self.rect2.append(rect)
            # Save the rectified images if necessary
            if CAPTURE_PATH:
                for i, frame in enumerate(self.rect1):
                    path = os.path.join(CAPTURE_PATH, 'rect_left%.2d.png' % i)
                    print('Saving %s' % path)
                    imwrite(path, frame)
                for i, frame in enumerate(self.rect2):
                    path = os.path.join(CAPTURE_PATH, 'rect_right%.2d.png' % i)
                    print('Saving %s' % path)
                    imwrite(path, frame)
            patternImages = [self.rect1[:-2], self.rect2[:-2]]
            whiteImages = [self.rect1[-2], self.rect2[-2]]
            blackImages = [self.rect1[-1], self.rect2[-1]]
            patternImages = numpy.array(patternImages)
            whiteImages = numpy.array(whiteImages)
            blackImages = numpy.array(blackImages)
            # Decode and reconstruct the pointcloud
            retval, disparityMap = self.graycode.decode(patternImages, blackImages=blackImages, whiteImages=whiteImages)
            if not retval:
                return None # Error signal - decode() failed
            disparityMap = numpy.float32(disparityMap)
            # Process the disparity map
            min = disparityMap.min()
            max = disparityMap.max()
            if min == max:
                return None # Error signal - no data
            alpha = 255.0 / (max - min)
            scaledDisparityMap = convertScaleAbs(disparityMap, alpha=alpha)
            # Use a threshold to remove noise
            retval, thresh = threshold(scaledDisparityMap, 0, 255, THRESH_OTSU | THRESH_BINARY)
            # Generate the pointcloud
            pointcloud = reprojectImageTo3D(disparityMap, self.Q, handleMissingValues=True)
            pointcloud[thresh == 0] = numpy.inf
            pointcloud[(abs(pointcloud) > COORD_THRESH).any(2)] = numpy.inf
            # Save the disparity map and pointcloud, both in NumPy and standard formats, if
            # that debug flag is turned on.
            if CAPTURE_PATH:
                numpy.save(os.path.join(CAPTURE_PATH, 'disparity.npy'), disparityMap)
                colorDisparityMap = applyColorMap(scaledDisparityMap, COLORMAP_JET)
                imwrite(os.path.join(CAPTURE_PATH, 'disparity.png'), colorDisparityMap)
                numpy.save(os.path.join(CAPTURE_PATH, 'pointcloud.npy'), pointcloud)
                # Save pointcloud in plain text format for debug mode.
                save_pcd(pointcloud, os.path.join(CAPTURE_PATH, 'pointcloud.pcd'), binary=False)
            # TODO: error checking
            return pointcloud




    def calibrate(self):
        # Calibrate the cameras
        self.clear_frames()
        if not SHOW_PREVIEW:
            # Start a preview if there's not already one.
            self.start_preview(MIRROR_PREVIEW)
        # Initialize the calibration result arrays
        objpoints = []
        grid = [(j*SQUARE_SIZE, i*SQUARE_SIZE, 0) for i in range(CB_SIZE[1]) for j in range(CB_SIZE[0])]
        imgpoints1 = []
        imgpoints2 = []
        waitKey(1) # Update the windows
        # Capture a series of calibration images
        while True:
            if REUSE_CALIB_DATA:
                # Debugging ONLY: Load a sequence of previously captured images
                frame1 = imread(os.path.join(CALIB_PATH, 'left%.2d.png' % (len(self.frames1))))
                if frame1 is None:
                    break
                frame1 = cvtColor(frame1, COLOR_BGR2GRAY)
                self.frames1.append(frame1)
                frame2 = imread(os.path.join(CALIB_PATH, 'right%.2d.png' % (len(self.frames2))))
                if frame2 is None:
                    break
                frame2 = cvtColor(frame2, COLOR_BGR2GRAY)
                self.frames2.append(frame2)
            else:
                print('Press any key to capture an image. Press [ESCAPE] to finish calibrating.')
                # Camera preview loop
                while True:
                    # Show the mirrored captures, since this behavior is more intuitive.
                    retval = self.update()
                    if retval != -1:
                        break
                if retval == 27:
                    break # escape means we're done capturing
                self.capture()
            # Show the images
            imshow('Camera 1', self.frames1[-1])
            imshow('Camera 2', self.frames2[-1])
            waitKey(1) # Update the images
            # Find the corners in both images
            ret1, corners1 = findChessboardCorners(self.frames1[-1], CB_SIZE, None)
            if ret1:
                print('Found corners using camera #1.')
                ret2, corners2 = findChessboardCorners(self.frames2[-1], CB_SIZE, None)
                if ret2:
                    print('Found corners using camera #2.')
                    # Make sure the corners are in the right order
                    xdelta1 = corners1[0, 0, 0] - corners1[-1, 0, 0]
                    xdelta2 = corners2[0, 0, 0] - corners2[-1, 0, 0]
                    if (xdelta1 > 0) != (xdelta2 > 0):
                        # They're not, so switch them.
                        print('Switching order of coordinates in camera #2')
                        corners2 = corners2[::-1]
                    # Refine the corners
                    subpix1 = cornerSubPix(self.frames1[-1], corners1, WIN_SIZE, (-1, -1), CRITERIA)
                    subpix2 = cornerSubPix(self.frames2[-1], corners2, WIN_SIZE, (-1, -1), CRITERIA)
                    imgpoints1.append(corners1)
                    imgpoints2.append(corners2)
                    objpoints.append(grid[:])
                    if CALIB_PATH and not REUSE_CALIB_DATA:
                        imwrite(os.path.join(CALIB_PATH,  'left%.2d.png' % (len(objpoints)-1)), self.frames1[-1])
                        imwrite(os.path.join(CALIB_PATH, 'right%.2d.png' % (len(objpoints)-1)), self.frames2[-1])
                    frame1 = cvtColor(self.frames1[-1], COLOR_GRAY2BGR)
                    frame1 = drawChessboardCorners(frame1, CB_SIZE, subpix1, ret1)
                    frame2 = cvtColor(self.frames2[-1], COLOR_GRAY2BGR)
                    frame2 = drawChessboardCorners(frame2, CB_SIZE, subpix2, ret2)
                    imshow('Camera 1', frame1)
                    imshow('Camera 1', frame2)
                    print('Successfully found %d calibration data point%s.' % (len(objpoints), '' if len(objpoints) == 1 else 's'))
                    if REUSE_CALIB_DATA:
                        # If we're just reusing old data, don't waste the user's time by making them press keys for no reason.
                        waitKey(1000)
                    else:                        
                        print('Press any key to continue to the next capture. Press [ESCAPE] to finish calibrating.')
                        if waitKey() == 27:
                            break
                else:
                    print('Failed to find corners using camera #2.')
            else:
                print('Failed to find corners using camera #1.')
        # Clean up
        if not SHOW_PREVIEW:
            self.end_preview()
        # Obtain calibration data
        if objpoints:
            objpoints = numpy.array(objpoints, numpy.float32)
            imgpoints1 = numpy.array(imgpoints1, numpy.float32)
            imgpoints2 = numpy.array(imgpoints2, numpy.float32)
            if CALIB_PATH:
                print('Saving calibration capture results...')
                numpy.save(os.path.join(CALIB_PATH, 'objpoints.npy'), objpoints)
                numpy.save(os.path.join(CALIB_PATH, 'imgpoints1.npy'), imgpoints1)
                numpy.save(os.path.join(CALIB_PATH, 'imgpoints2.npy'), imgpoints2)
        else:
            if CALIB_PATH and os.listdir(CALIB_PATH):
                # Use previously stored capture data if possible
                objpoints = numpy.load(os.path.join(CALIB_PATH, 'objpoints.npy'))
                imgpoints1 = numpy.load(os.path.join(CALIB_PATH, 'imgpoints1.npy'))
                imgpoints2 = numpy.load(os.path.join(CALIB_PATH, 'imgpoints2.npy'))
            else:
                # Do nothing since the user didn't capture anything.
                print('No calibration information.')
                return
        # OpenCV calibration routine
        print('Calibrating...')
        print()
        retval, K1, D1, rvecs1, tvecs1 = calibrateCamera(objpoints, imgpoints1, CAM_SIZE, None, None)
        print('Left camera calibration:')
        print('K1 =\n%r\n' % K1)
        print('D1 =\n%r\n' % D1)
        print('Reprojection error %g' % retval)
        print()
        retval, K2, D2, rvecs2, tvecs2 = calibrateCamera(objpoints, imgpoints2, CAM_SIZE, None, None)
        print('Right camera calibration:')
        print('K2 =\n%r\n' % K2)
        print('D2 =\n%r\n' % D2)
        print('Reprojection error %g' % retval)
        print()
        retval, K1, D1, K2, D2, R, T, E, F = stereoCalibrate(objpoints, imgpoints1, imgpoints2, K1, D1, K2, D2, CAM_SIZE,
                                                             flags = CALIB_FIX_INTRINSIC | CALIB_RATIONAL_MODEL | CALIB_FIX_PRINCIPAL_POINT)
        print('Stereo calibration:')
        print()
        print('# Intrinsic matrix of first camera')
        print('K1 = \\\n%r\n' % K1)
        print('# Distortion coefficients of first camera')
        print('D1 = \\\n%r\n' % D1)
        print('# Intrinsic matrix of second camera')
        print('K2 = \\\n%r\n' % K2)
        print('# Distortion coefficients of second camera')
        print('D2 = \\\n%r\n' % D2)
        print('# Rotation matrix between two cameras')
        print('R = \\\n%r\n' % R)
        print('# Translation vector between two cameras')
        print('T = \\\n%r\n' % T)
        print('# Reprojection error %g' % retval)
        print()
        # Set up remap and perspective transform data needed by snapshot().
        self.rectify(K1, D1, K2, D2, R, T)
            
        


    # Camera preview debugging tools

    def start_preview(self, mirrored=True):
        # Create OpenCV preview windows.
        if not self.has_preview:
            self.has_preview = True
            self.mirrored_preview = bool(mirrored)
            namedWindow('Camera 1')
            namedWindow('Camera 2')
            try:
                setWindowProperty('projector', WND_PROP_FULLSCREEN, WINDOW_NORMAL)
            except error:
                pass
            waitKey(1)

    def end_preview(self):
        # Close OpenCV preview windows.
        if self.has_preview:
            destroyWindow('Camera 1')
            destroyWindow('Camera 2')
            self.has_preview = False
            waitKey(1)

    def pause_preview(self):
        # Pause the preview if we're about to take a snapshot.
        if self.has_preview and not REUSE_CAPTURE_DATA:
            setWindowProperty('Camera 1', WND_PROP_VISIBLE, False)
            setWindowProperty('Camera 2', WND_PROP_VISIBLE, False)
            setWindowProperty('projector', WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN)
            waitKey(1)

    def resume_preview(self):
        # Resume the preview after we take a snapshot.
        if self.has_preview and not REUSE_CAPTURE_DATA:
            setWindowProperty('Camera 1', WND_PROP_VISIBLE, True)
            setWindowProperty('Camera 2', WND_PROP_VISIBLE, True)
            setWindowProperty('projector', WND_PROP_FULLSCREEN, WINDOW_NORMAL)
            waitKey(1)

    def update(self):
        # Update the preview if present.
        if self.has_preview:
            im1 = self.cam1.capture()
            im2 = self.cam2.capture()
            if self.mirrored_preview:
                im1 = im1[:, ::-1]
                im2 = im2[:, ::-1]
            imshow('Camera 1', im1)
            imshow('Camera 2', im2)
            return waitKey(1)
        return -1

