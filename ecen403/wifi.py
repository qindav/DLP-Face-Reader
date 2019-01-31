# Wireless connection functions
# Matthew Kroesche
# ECEN 403

import os
import subprocess
import pypcd


SOCKETS_DIR = '/home/pi/Desktop/ecen403/socketsfile'


class WiFi(object):

    def __init__(self, master):
        self.master = master
        self.popen = None

    def init(self):
        cd = os.getcwd()
        os.chdir(SOCKETS_DIR)
        self.popen = subprocess.Popen(('node', 'server'))
        os.chdir(cd)

    def quit(self):
        self.popen.kill()

    def connected(self):
        return False # TODO

    def send(self, pointcloud):
        # TODO: reformat array
        pcd = pypcd.make_xyz_pointcloud(pointcloud)
        pcd.save(os.path.join(SOCKETS_DIR, 'data', 'upload.pcd'))
            
        
