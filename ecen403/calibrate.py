#!/usr/bin/env python

# Camera calibration (modified from OpenCV Python tutorial)
# Matthew Kroesche
# ECEN 403

import numpy as np
import cv2
import os

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:7].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


for name in sorted(os.listdir('/home/pi/Desktop/calibration')):
    fname = os.path.join('/home/pi/Desktop/calibration', name)
    print 'Reading %s...' % fname
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    print 'Locating corners...'
    ret, corners = cv2.findChessboardCorners(gray, (7,7),None)
    print 'Finished locating.'

    # If found, add object points, image points (after refining them)
    if ret:
        print 'Success!'
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,7), corners2,ret)
        cv2.imshow('img',img)
        cv2.waitKey()
        cv2.destroyWindow('img')
    else:
        print 'Failed to find corners.'

cv2.destroyAllWindows()
print objpoints

print cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
