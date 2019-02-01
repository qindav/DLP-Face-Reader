# Utility to save a numpy array (HxWx3 floating point values)
# as a PCD format file
# Matthew Kroesche
# ECEN 404


def save_pcd(pointcloud, filename, binary=True):
    with open(filename, 'wb') as o:
        h, w = pointcloud.shape[:2]
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
''' % (w, h, w*h, b'binary' if binary else b'ascii'))
        if binary:
            # Binary data
            pointcloud.tofile(filename)
        else:
            # ASCII data
            for point in pointcloud.reshape(w*h, 3):
                filename.write(b'%g %g %g\n' % tuple(point))
