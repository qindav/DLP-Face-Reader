# Wireless connection functions
# Matthew Kroesche
# ECEN 403-404

import os
import subprocess
import threading
import queue
from .pcd import *


SOCKETS_DIR = '/home/pi/Desktop/DLPScanner/socketsfile'


class WiFi(object):

    def __init__(self, master):
        self.master = master
        self.popen = None
        self.read_connected = False
        self.queue = queue.Queue()
        self.pmutex = threading.Lock()

    def init(self):
        cd = os.getcwd()
        os.chdir(SOCKETS_DIR)
        self.popen = subprocess.Popen(('node', 'server'), stdout=subprocess.PIPE)
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.start()
        os.chdir(cd)

    def quit(self):
        with self.pmutex:
            self.popen.kill()
            self.popen = None

    def read_loop(self):
        while True:
            with self.pmutex:
                if self.popen is None:
                    break
                self.queue.put(self.popen.stdout.readline())

    def connected(self):
        if self.read_connected:
            return True
        try:
            if self.queue.get_nowait().strip() == b'Socket connected.':
                self.read_connected = True
                return True
        except queue.Empty:
            return False
        return False

    def send(self, pointcloud):
        filename = os.path.join(SOCKETS_DIR, 'data', 'upload.pcd')
        save_pcd(pointcloud, filename)
            
        
