# Wireless connection functions
# Matthew Kroesche
# ECEN 403-404

import os
import subprocess
from .pcd import *


SOCKETS_DIR = '/home/pi/Desktop/DLPScanner/socketsfile'


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
        self.popen = None

    def connected(self):
        return False # TODO

    def send(self, pointcloud):
        filename = os.path.join(SOCKETS_DIR, 'data', 'upload.pcd')
        save_pcd(pointcloud, filename)
            
        
