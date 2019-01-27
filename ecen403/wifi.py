# Wireless connection functions
# Matthew Kroesche
# ECEN 403

import subprocess
import pypcd




class WiFi(object):

    def __init__(self, master):
        self.master = master
        self.popen = None

    def init(self):
        self.popen = subprocess.Popen(('node', 'server'))

    def quit(self):
        self.popen.kill()

    def connected(self):
        return False # TODO

    def send(self, pointcloud):
        # TODO: reformat array
        pcd = pypcd.make_xyz_pointcloud(pointcloud)
        pcd.save('/home/pi/Desktop/ecen403/socketsfile/data/upload.pcd')
            
        
