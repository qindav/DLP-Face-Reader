# Utility to save a numpy array (HxWx3 floating point values)
# as a PCD format file
# Matthew Kroesche
# ECEN 404

import numpy


def save_pcd(pointcloud, filename, binary=True):
    with open(filename, 'wb') as o:
        h, w = pointcloud.shape[:2]
        points = pointcloud.reshape(w*h, 3)
        points = points[~numpy.isinf(points).any(1)]
        # Header
        o.write(b'''VERSION 0.7
FIELDS x y z
SIZE 4 4 4
TYPE F F F
COUNT 1 1 1
WIDTH %d
HEIGHT %d
VIEWPOINT 0 0 0 1 0 0 0
POINTS %d
DATA %b
''' % (w, h, len(points), b'binary' if binary else b'ascii'))
        if binary:
            # Binary data
            points.tofile(filename)
        else:
            # ASCII data
            for point in points:
                o.write(b'%g %g %g\n' % tuple(point))



def load_pcd(filename):
    with open(filename, 'rb') as o:
        while True:
            line = o.readline().split()
            if line[0] == b'DATA':
                format = line[1]
                if format not in (b'ascii', b'binary'):
                    return
                return numpy.fromfile(o, sep=(b'' if format == b'binary' else b' '))
        
            
        
            
