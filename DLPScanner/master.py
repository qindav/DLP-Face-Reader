# Master object, responsible for driving all other objects
# Matthew Kroesche
# ECEN 403-404

from .gpio import IO
from .wifi import WiFi
from .usb import USB
from .cvstereo import OpenCV # May also use opencv or pyimage, but these currently do not work properly.




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
        self.io.start_busy() # Error light is lit while device is booting
        self.wifi.init()
        self.usb.init()
        self.opencv.init()
        self.io.end_busy()
        self.on = True

    def quit(self):
        self.io.quit()
        self.wifi.quit()
        self.usb.quit()
        self.opencv.quit()
        self.on = False

    def run(self):
        self.io.run()
