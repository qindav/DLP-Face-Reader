# Master object, responsible for driving all other objects
# Matthew Kroesche
# ECEN 403

from ecen403.gpio import IO
from ecen403.wifi import WiFi
from ecen403.usb import USB
from ecen403.cvstereo import OpenCV




class Master(object):

    def __init__(self):
        self.io = IO(self)
        self.wifi = WiFi(self)
        self.usb = USB(self)
        self.opencv = OpenCV(self)
        self.on = False

    def __del__(self):
        if self.on:
            self.quit()

    def init(self):
        self.io.init()
        self.wifi.init()
        self.usb.init()
        self.opencv.init()
        self.on = True

    def quit(self):
        self.io.quit()
        self.wifi.quit()
        self.usb.quit()
        self.opencv.quit()
        self.on = False

    def run(self):
        self.io.run()
