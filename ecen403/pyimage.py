# Camera/projector communication
# Matthew Kroesche
# ECEN 403

import pygame
import numpy
import picamera
import os


# Operation parameters

PROJ = (608, 328)
RESOLUTION = (640, 368)
PRE_DELAY = 50 # milliseconds
POST_DELAY = 20 # milliseconds
SHUTTER_SPEED = 1000 # microseconds

# Converting to grayscale
RED_SCALE = .299
GREEN_SCALE = .587
BLUE_SCALE = .114

B = .3 # parameter for direct light estimation
THRESH = 5 # parameter for robust estimation
MM_THRESHOLD = 25 # Min/max threshold
MAX_DIST = 100.0
MIN_ACCEPTABLE_POINTS = 100

# For debugging, set IMAGE_SAVE_PATH to some non-empty string
# and all the images captured should be saved to that path.
IMAGE_SAVE_PATH = '/home/pi/Desktop/Pictures'
IMAGE_SAVE_FILETYPE = 'png'
BENCHMARK = False



# Calibration parameters

matrix = numpy.mat

K1 = matrix([[2.80650169e+03, 0.00000000e+00, 7.45108475e+02],
        [0.00000000e+00, 2.84352345e+03, 6.09849175e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

K2 = matrix([[9.68530149e+03, 0.00000000e+00, 3.36178522e+02],
        [0.00000000e+00, 1.48493075e+04, 1.34518347e+02],
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

R = matrix([[ 0.98237387,  0.00285983,  0.18690477],
        [-0.09839445,  0.85806115,  0.50403332],
        [-0.15893427, -0.51353956,  0.84321825]])

T = matrix([[-0.02758365],
        [-0.61067318],
        [ 5.07215759]])


Rt = R.T




class PyImage(object):

    def __init__(self, master):
        self.master = master



    def init(self):
        # Set up the camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = RESOLUTION
        self.camera.framerate = int(round(1000.0 / (PRE_DELAY + POST_DELAY)))
        self.camera.shutter_speed = SHUTTER_SPEED
        # Set up pygame
        pygame.init()
        self.screen = None
        # Generate the projector patterns
        vertical = []
        horizontal = []
        n = 1
        x, y, z = numpy.indices(PROJ+(3,))
        while n <= max(PROJ):
            pattern = numpy.where(((x // n) % 2) == 0, 255, 0)
            vertical.extend([pattern, 255-pattern])
            pattern = numpy.where(((y // n) % 2) == 0, 255, 0)
            horizontal.extend([pattern, 255-pattern])
            n *= 2
        self.pattern = [pygame.surfarray.make_surface(p) for p in vertical[::-1] + horizontal[::-1]]
        self.pattern = [pygame.transform.scale(i, (3*PROJ[0], 3*PROJ[1])) for i in self.pattern]
        # Create storage area for captured images
        w, h = RESOLUTION
        self.color = numpy.empty((h, w, 3), dtype=numpy.uint8)
        self.flat_color = self.color.ravel()
        self.images = numpy.empty((len(self.pattern), h, w), dtype=numpy.uint8)


        
    def quit(self):
        # Close the camera now that we're done with it
        self.camera.close()




    def generate(self):
        # Generator function used by capture_sequence() to speed up camera
        for pattern, im in zip(self.pattern, self.images):
            # Update the projector
            self.screen.blit(pattern, (0, 0))
            pygame.display.flip()
            pygame.time.delay(PRE_DELAY)
            # Capture the image
            yield self.flat_color
            pygame.time.delay(POST_DELAY)
            # Store the image
            im[...] = (self.color[...,2]*RED_SCALE + self.color[...,1]*GREEN_SCALE + self.color[...,0]*BLUE_SCALE).round()




    # A lot of this code is based on code found here:
    # https://github.com/kshi219/3dScan
    

    def decode(self):
        N = len(self.images) // 2
        nbits = N // 2
        nan_thresh = 1 << (nbits + 1)
        # First, estimate direct and ambient sources of light
        images = self.images[N-8:N-4] + self.images[-8:-4] # Use images near (but not at) the dense end of the spectrum.
        images = numpy.stack(images, axis=2)
        min = numpy.amin(images, axis=2)
        max = numpy.amax(images, axis=2)
        direct = ((max - min) / (1.0-B)).astype(numpy.uint8)
        ambient = (2.0 * (min - B*max) / (1.0-B**2)).astype(numpy.uint8)
        # Next, iterate through the captured images
        shape = (RESOLUTION[1], RESOLUTION[0])
        decoded = numpy.zeros(shape+(2,), int) # 2 channels, one for vertical and one for horizontal.
        for i in range(N):
            im1 = self.images[2*i]
            im2 = self.images[2*i+1]
            # Performing robust bit estimation
            out = numpy.full(shape, nan_thresh)
            needs_correct = (direct > ambient) & (direct >= THRESH)
            diff = (im1 > im2)
            out[needs_correct & diff] = 1 << (nbits - 1 - (i % (N//2)))
            out[needs_correct & ~diff] = 0
            # Combine with decoded data, choosing the channel based on whether 2*i >= N.
            decoded[...,((2*i)//N)] |= out
        # Convert the pattern to projector coordinates
        resx, resy = PROJ
        offx, offy = ((1 << nbits) - resx)//2, ((1 << nbits) - resy)//2
        below_thresh = (decoded < THRESH)
        decoded[~below_thresh] = -1
        shift = 1
        while shift < 64:
            decoded[below_thresh] ^= (decoded[below_thresh] >> shift)
            shift <<= 1
        decoded[...,0][below_thresh[...,0]] = (decoded[...,0][below_thresh[...,0]] - offy).clip(0, resy-1)
        decoded[...,1][below_thresh[...,1]] = (decoded[...,1][below_thresh[...,1]] - offx).clip(0, resx-1)
        return decoded



    def reconstruct(self, pattern):
        # Calculate min/max
        stack = numpy.stack(self.images, axis=2)
        amin = numpy.amin(stack, axis=2)
        amax = numpy.amax(stack, axis=2)
        # Determine invalid area
        invalid = (pattern[...,0] < 0) | (pattern[...,0] >= PROJ[1]) | \
                  (pattern[...,1] < 0) | (pattern[...,1] >= PROJ[0]) | \
                  (amax - amin < MM_THRESHOLD)
        # Map projector coordinates to camera coordinates
        uniq = numpy.unique( pattern[...,1][~invalid] * PROJ[1] + pattern[...,0][~invalid] )
        pointcloud = []
        y, x = numpy.indices(pattern.shape[:2])
        for proj_point in uniq:
            matching = (pattern[...,1]*PROJ[1] + pattern[...,0] == proj_point) & ~invalid
            x1 = x[matching].mean()
            y1 = y[matching].mean()
            x2 = proj_point // PROJ[1]
            y2 = proj_point % PROJ[1]
            # Triangulation (pretty much direct from kshi's code)
            u1 = numpy.mat([
                [ (x1 - K1[0, 2]) / K1[0, 0] ],
                [ (y1 - K1[1, 2]) / K1[1, 1] ],
                [             1.0            ],
                ])
            u2 = numpy.mat([
                [ (x2 - K2[0, 2]) / K2[0, 0] ],
                [ (y2 - K2[1, 2]) / K2[1, 1] ],
                [             1.0            ],
                ])
            v1 = u1
            v2 = Rt * (u2 - T)
            q1 = v1
            q2 = Rt * u2
            v1tv1 = float(v1.transpose() * v1)
            v1tv2 = float(v1.transpose() * v2)
            v2tv1 = float(v2.transpose() * v1)
            v2tv2 = float(v2.transpose() * v2)
            detV = v1tv1*v2tv2 - v1tv2*v2tv1
            q2q1 = q2 - q1
            Q1 = float(v1.transpose() * q2q1)
            Q2 = -float(v2.transpose() * q2q1)
            lam1 = (v2tv2*Q1 + v1tv2*Q2) / detV
            lam2 = (v2tv1*Q1 + v1tv1*Q2) / detV
            p1 = lam1*v1 + q1
            p2 = lam2*v2 + q2
            p = (p1+p2)/2.0
            # Add to the pointcloud if applicable
            dist = numpy.linalg.norm(p2-p1)
            if dist < MAX_DIST:
                pointcloud.append(p)
        # Return the pointcloud
        return pointcloud



    def save(self):
        # This will save every one of the ~40 grayscale images that were just captured to some folder so you can look at them.
        # Obviously, this will waste some time, so just use it when debugging, but hopefully it will be useful. :-)
        for i, im in enumerate(self.images):
            surf = pygame.surfarray.make_surface(numpy.repeat((im.T)[..., numpy.newaxis], 3, axis=2))
            print 'Saving image #%d' % (i+1)
            pygame.image.save(surf, os.path.join(IMAGE_SAVE_PATH, 'image_%.2d.%s' % (i+1, IMAGE_SAVE_FILETYPE)))



    def snapshot(self):
        # Pygame window setup
        if BENCHMARK:
            start = pygame.time.get_ticks()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        # Capture a sequence of images using the camera and the projector
        self.camera.capture_sequence(self.generate(), 'bgr', use_video_port=True)
        pygame.display.quit()
        if IMAGE_SAVE_PATH:
            self.save()
        # Processing
        pattern = self.decode()
        pointcloud = self.reconstruct(pattern)
        if BENCHMARK:
            end = pygame.time.get_ticks()
            print 'Time elapsed: %d ms' % (end-start)
        return pointcloud if len(pointcloud) >= MIN_ACCEPTABLE_POINTS else None
            
            
