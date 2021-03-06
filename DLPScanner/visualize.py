#!/usr/bin/python

# Visualization script with VPython
# Matthew Kroesche
# ECEN 404

# Note the /usr/bin/python instead of /usr/bin/env python.
# This is because we specifically need the Pi's standard version of python,
# which has VPython; not the phantom version within the CV workspace.

import sys
from visual import *
from pcd import *

Z_FILTER_MAX = float('inf')
Z_FILTER_MIN = -float('inf')


def visualize(pcd):
    
    # Apply a color wedge
    pcd = pcd[(Z_FILTER_MIN <= pcd[:,2]) & (pcd[:,2] <= Z_FILTER_MAX)]
    color_scale = 1.0 / (pcd[:,2].max() - pcd[:,2].min())
    hue = 6.0 * color_scale * (pcd[:,2] - pcd[:,2].min())
    col = numpy.zeros(pcd.shape, float)
    rng = [((i <= hue) & (hue <= i+1)) for i in range(6)]
    col[:,1][rng[0]] =     hue[rng[0]]     # Red -> Yellow
    col[:,0][rng[1]] = 2 - hue[rng[1]]     # Yellow -> Green
    col[:,2][rng[2]] =     hue[rng[2]] - 2 # Green -> Cyan
    col[:,1][rng[3]] = 4 - hue[rng[3]]     # Cyan -> Blue
    col[:,0][rng[4]] =     hue[rng[4]] - 4 # Blue -> Magenta
    col[:,2][rng[5]] = 6 - hue[rng[5]]     # Magenta -> Red

    # Full color intensity in these regions
    col[:,0][rng[0]] = col[:,1][rng[1]] = col[:,1][rng[2]] = \
                       col[:,2][rng[3]] = col[:,2][rng[4]] = col[:,0][rng[5]] = 1

    # Shift RGB -> GBR (just for aesthetic reasons)
    col = numpy.roll(col, 1, axis=1)

    # Create pointcloud
    scene.center = pcd.mean(0) # Center at the mass center of the pointcloud
    scene.fullscreen = True
    obj = points(pos=pcd, size=1, color=col)

    # Press ESCAPE to quit.



# Read pointcloud file from command line
if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = '/home/pi/Desktop/DLPScanner/socketsfile/data/upload.pcd'
    visualize(load_pcd(filename))


