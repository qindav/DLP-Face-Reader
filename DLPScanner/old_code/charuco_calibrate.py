#!/usr/bin/env python

# Script to calibrate the camera and projector from
# a list of previously captured images
# Matthew Kroesche
# ECEN 403

# This script uses Aruco to calibrate a single camera to a projector,
# and is intended to be used in tandem with charuco_capture.py.
# See stereo_calibrate.py and cvstereo.py for code to calibrate two
# cameras to each other

import cv2
import numpy
import os


# Constants
CHARUCO_DICT = cv2.aruco.DICT_6X6_1000
BOARD = (6, 8)
CIRCLE_GRID = (7, 6)
BOARD_SPACING = (0.04, 0.02)
CIRCLE_SPACING = 0.04
PROJ_RESOLUTION = (608, 328)
CALIBRATION_DIR = '/home/pi/Desktop/charuco_calibration'
DISPLAY = True


# Set up the chessboard
dictionary = cv2.aruco.getPredefinedDictionary(CHARUCO_DICT)
board = cv2.aruco.CharucoBoard_create(BOARD[0], BOARD[1], BOARD_SPACING[0], BOARD_SPACING[1], dictionary)

# Initial data
list_corners = []
list_ids = []
images = []
draw_images = []
camera_circles = []
projector_circles = []

circle_array = numpy.array([(CIRCLE_SPACING*i, CIRCLE_SPACING*j, 0) for j in range(CIRCLE_GRID[1]) for i in range(CIRCLE_GRID[0])])
circle_points = []

# Blob detector
params = cv2.SimpleBlobDetector_Params()
params.maxArea = 1e5
params.blobColor = 255
params.filterByCircularity = True
blobDetector = cv2.SimpleBlobDetector_create(params)



# Iterate through the captured images once for corner detection
for filename in os.listdir(CALIBRATION_DIR):
    print 'Finding charuco board in %s' % filename
    # Load the image
    path = os.path.join(CALIBRATION_DIR, filename)
    image = cv2.imread(path)
    images.append(image)
    # Find the charuco board corners
    corners, ids, rejected = \
             cv2.aruco.detectMarkers(image, dictionary)
    corners, ids, rejected, recovered = \
             cv2.aruco.refineDetectedMarkers(image, board, corners, ids, rejected)
    retval, corners, ids = \
            cv2.aruco.interpolateCornersCharuco(corners, ids, image, board)
    list_corners.append(corners)
    list_ids.append(ids)
    # Draw the corners onto the image
    if DISPLAY:
        draw_image = image.copy()
        draw_image = cv2.aruco.drawDetectedCornersCharuco(draw_image, corners, ids) # Draw the corners
        draw_images.append(draw_image)
    else:
        draw_images.append(None)


        

# Obtain the camera matrix
retval1, K1, dist1, rvecs1, tvecs1 = \
        cv2.aruco.calibrateCameraCharuco(list_corners, list_ids, board, image.shape[:2], None, None)

print
print 'Camera matrix:'
print K1
print
print 'Camera distortion coefficients:'
print dist1
print




# Now, iterate again to detect the circles
for image, rvec, tvec, draw_image in zip(images, rvecs1, tvecs1, draw_images):
    # Find the circle grid
    retval, centers = cv2.findCirclesGrid(image, CIRCLE_GRID, blobDetector=blobDetector,
                                          flags=cv2.CALIB_CB_SYMMETRIC_GRID)
    if not retval:
        continue
    if DISPLAY:
        draw_image = cv2.drawChessboardCorners(draw_image, CIRCLE_GRID, centers, retval) # Draw the circle grid
    # Do the ray-plane intersection
    centers_norm = cv2.convertPointsToHomogeneous(cv2.undistortPoints(centers, K1, dist1))
    R = cv2.Rodrigues(rvec)[0] # Convert the rotation vector to a matrix
    normal = R[2] # Obtain normal vector to plane
    point = tvec.T # Obtain point in plane
    circles3d = []
    for p in centers_norm:
        direction = p / numpy.linalg.norm(p)
        dot_product = normal.dot(direction.T)
        if abs(dot_product) >= 1e-6:
            si = -normal.dot((p-point).T) / dot_product # Project this vector onto the normal
            circles3d.append(p + si*direction)
    # Reproject onto the camera
    if circles3d:
        circles_reproj = cv2.projectPoints(numpy.array(circles3d), (0,0,0), (0,0,0), K1, dist1)[0]
        camera_circles.append(centers)
        circle_points.append(circle_array)
        projector_circles.append(circles_reproj)
        if DISPLAY:
            for c in circles_reproj:
                cv2.circle(draw_image, tuple(c.astype(numpy.int32)[0]), 3, (255,255,0), cv2.FILLED)
        # Display the image with gridlines drawn onto it
        if DISPLAY:
            cv2.imshow('charuco', draw_image)
            cv2.waitKey()
            cv2.destroyWindow('charuco')



# Obtain the projector matrix
circle_points = numpy.array(circle_points, numpy.float32)
camera_circles = numpy.array(camera_circles, numpy.float32)
projector_circles = numpy.array(projector_circles, numpy.float32)
retval2, K2, dist2, rvecs2, tvecs2 = cv2.calibrateCamera(circle_points, projector_circles, PROJ_RESOLUTION, None, None)

print
print 'Projector matrix:'
print K2
print
print 'Projector distortion coefficients:'
print dist2
print



# Obtain the final data
retval, K1, dist1, K2, dist2, R, T, E, F = cv2.stereoCalibrate(
    circle_points, camera_circles, projector_circles, K1, dist1, K2, dist2, image.shape[:2], flags=cv2.CALIB_USE_INTRINSIC_GUESS)

print
print
print 'K1 =', repr(numpy.mat(K1))
print 'K2 =', repr(numpy.mat(K2))
print 'R =', repr(numpy.mat(R))
print 'T =', repr(numpy.mat(T))












