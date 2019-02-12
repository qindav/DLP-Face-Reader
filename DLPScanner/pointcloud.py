# VPython hack for visualizing pointclouds
# Matthew Kroesche
# ECEN 404

from visual import *
#from PIL import Image, ImageGrab, GifImagePlugin
import numpy
#import sys
#
#sys.path.append('C:/Users/Matthew/Desktop')
#import images2gif

pcd = numpy.load('C:/Users/Matthew/Desktop/pointcloud.npy')
pcd = pcd.reshape(pcd.shape[0]*pcd.shape[1], 3)
pcd = pcd[(abs(pcd) <= 1000).all(1)]

#pcd = pcd[(-16 <= pcd[:,2]) & (pcd[:,2] <= -7)]

color_scale = 1.0 / (pcd[:,2].max() - pcd[:,2].min())
hue = 6.0 * color_scale * (pcd[:,2] - pcd[:,2].min())
col = numpy.zeros(pcd.shape, float)
rng = [((i <= hue) & (hue <= i+1)) for i in range(6)]
col[:,0][rng[0]] = hue[rng[0]]
col[:,1][rng[1]] = hue[rng[1]]-1
col[:,0][rng[2]] = 3-hue[rng[2]]
col[:,2][rng[3]] = hue[rng[3]]-3
col[:,1][rng[4]] = 5-hue[rng[4]]
col[:,2][rng[5]] = hue[rng[5]]-5
col[:,0][rng[1]] = col[:,1][rng[2]] = col[:,1][rng[3]] = col[:,2][rng[4]] = 1


scene.center = pcd.mean(0)
scene.visible = False
scene.fullscreen = True
##scene.cursor.visible = False
##scene.range = 15
scene.x = scene.y = 0
scene.width = 1920
scene.height = 1080
scene.visible = True
graphic = points(pos=pcd, size=1, color=col)

##images = []
##n = 0
##
##while True:
##    if n < 420:
##        n += 1
##        if (n > 60) and (n % 6 == 0):
##            im = ImageGrab.grab()
##            images.append(im.crop((10, 40, 1910, 1000)).resize((950, 480)))
##    rate(60)
##    scene.forward = scene.forward.rotate(radians(1), (0, 1, 0))
##    if scene.kb.keys:
##        scene.visible = False
##        break
##
##images2gif.writeGif('C:/Users/Matthew/Desktop/with_threshold.gif', images, loops=65535)
