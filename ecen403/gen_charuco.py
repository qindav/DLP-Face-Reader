#!/usr/bin/env python

# Simple script to generate and save a charuco image
# Matthew Kroesche
# ECEN 403

import cv2
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
cb = cv2.aruco.CharucoBoard_create(6, 8, 0.04, 0.02, dictionary)
image = cb.draw((600, 500), marginSize=10)
cv2.imwrite('/home/pi/Desktop/charuco.png', image)
