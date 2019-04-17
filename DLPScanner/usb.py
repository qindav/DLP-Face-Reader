# USB connection functions
# Matthew Kroesche
# ECEN 403-404

import os
from .pcd import *


# USB locations
USB_PATH = '/media/pi'




class USB(object):

    def __init__(self, master):
        self.master = master
        self.n = 1

    # init(), quit() are just for modularity.
    # They don't do anything.
    def init(self): pass
    def quit(self): pass

    def connected(self):
        # Return True if the USB drive exists.
        return bool(os.listdir(USB_PATH))

    def send(self, pointcloud):
        # Locate the USB drive
        dir = os.listdir(USB_PATH)
        if not dir:
            return # Does not exist, so do nothing
        path = dir[0]
        # Find a filename that has not been used yet.
        while self.n < 1024:
            filename = os.path.join(USB_PATH, path, 'pointcloud_%d.pcd' % self.n)
            self.n += 1
            if not os.path.isfile(filename):
                break
        else:
            return
        # Save the pointcloud to the file
        save_pcd(pointcloud, filename)

    def eject(self):
        # Eject the USB device
        dir = os.listdir(USB_PATH)
        if not dir:
            return # Does not exist, so do nothing
        path = dir[0]
        os.system('sudo umount %s' % os.path.join(USB_PATH, path))
        
        





