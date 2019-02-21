# Operations on pointclouds (HxWx3 NumPy arrays of floating point values)
# Matthew Kroesche
# ECEN 404

import numpy



def save_pcd(pointcloud, filename, binary=True):
    # Save a pointcloud in .pcd format
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
            points.tofile(o)
        else:
            # ASCII data
            for point in points:
                o.write(b'%g %g %g\n' % tuple(point))



def load_pcd(filename):
    # Load a pointcloud from .pcd format. Return the Nx3 NumPy array.
    with open(filename, 'rb') as o:
        n = 0
        while True:
            line = o.readline().split()
            if line[0] == b'POINTS':
                n = int(line[1])
            if line[0] == b'DATA':
                format = line[1]
                assert format in (b'ascii', b'binary')
                pointcloud = numpy.fromfile(o, numpy.float32, n*3, ('' if format == b'binary' else ' '))
                return pointcloud.reshape((n, 3))
                
        

def filter_pcd(pointcloud, d=2):
    # Try to remove the noise from a pointcloud. (Operates in place.)
    # First, calculate the mean Z distance from each point to its neighbors
    z = pointcloud[:, :, 2]
    isinf = numpy.isinf(pointcloud).any(2)
    counts = numpy.zeros(z.shape, z.dtype)
    zsum = numpy.zeros(z.shape, z.dtype)
    # Horizontal distances
    ok = ~isinf[:, :-1] & ~isinf[:, 1:]
    zsum[:, :-1][ok] += abs(z[:, :-1][ok] - z[:, 1:][ok])
    counts[:, :-1][ok] += 1
    zsum[:, 1:][ok] += abs(z[:, :-1][ok] - z[:, 1:][ok])
    counts[:, 1:][ok] += 1
    # Vertical distances
    ok = ~isinf[:-1, :] & ~isinf[1:, :]
    zsum[:-1, :][ok] += abs(z[:-1, :][ok] - z[1:, :][ok])
    counts[:-1, :][ok] += 1
    zsum[1:, :][ok] += abs(z[:-1, :][ok] - z[1:, :][ok])
    counts[1:, :][ok] += 1
    isinf |= (counts == 0)
    if isinf.all():
        # Bogus pointcloud
        pointcloud.fill(numpy.inf)
        return
    # Mean distances
    means = numpy.empty(z.shape, z.dtype)
    means[~isinf] = zsum[~isinf] / counts[~isinf]
    # Global mean and standard deviation of means
    mean = means[~isinf].mean()
    std = means[~isinf].std()
    norm = (means - mean) / std
    # Kick out any points whose "mean" distance is not within d standard deviations
    # of the global mean. d defaults to 2, which means that on average, roughly 5%
    # of the data points will be evicted.
    isinf |= (abs(norm) > d)
    pointcloud[isinf] = numpy.inf


