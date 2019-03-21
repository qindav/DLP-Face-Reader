# GUI for Raspberry Pi Virtual I/O
# Matthew Kroesche
# ECEN 404

from tkinter import *
import cv2

# Channel constants
POWER_BUTTON = 14
SNAPSHOT_BUTTON = 15
POWER_LED = 18
WIFI_LED = 27
USB_LED = 22
BUSY_LED = 23
ERROR_LED = 24




# Helper class for LEDs

class LED(Frame):

    def __init__(self, gpio, id, text, col_off, col_on):
        Frame.__init__(self, gpio.root)
        self.id = id
        self.col_off = col_off
        self.col_on = col_on
        self.indicator = Frame(self, relief=SUNKEN, width=10, height=10, bg=col_off)
        self.indicator.pack(side=LEFT, padx=10, pady=10)
        self.label = Label(self, text=text)
        self.label.pack(side=LEFT, padx=10, pady=10)

    def activate(self):
        self.indicator['bg'] = self.col_on

    def deactivate(self):
        self.indicator['bg'] = self.col_off






# Class to emulate the behavior of the Pi GPIO module

class VGPIO(object):

    def __init__(self):
        self.root = None
        self.inputs = set()



    def setmode(self, *args):
        if self.root:
            self.cleanup()
        self.root = Tk()
        self.root.withdraw()
        self.root.title('Virtual I/O')
        self.root.minsize(300, 0)
        self.root.attributes('-topmost', True)
        self.power_button = Button(self.root, text='Power', command = lambda: self.inputs.add(POWER_BUTTON))
        self.power_button.pack(side=TOP, fill=X, padx=10, pady=10)
        self.snapshot_button = Button(self.root, text='Snapshot', command = lambda: self.inputs.add(SNAPSHOT_BUTTON))
        self.snapshot_button.pack(side=TOP, fill=X, padx=10, pady=10)
        self.power_led = LED(self, POWER_LED, 'Power', '#070', '#0f0')
        self.power_led.pack(side=TOP, fill=X, padx=10, pady=10)
        self.wifi_led = LED(self, WIFI_LED, 'Wifi', '#007', '#7af')
        self.wifi_led.pack(side=TOP, fill=X, padx=10, pady=10)
        self.usb_led = LED(self, USB_LED, 'USB', '#777', '#fff')
        self.usb_led.pack(side=TOP, fill=X, padx=10, pady=10)
        self.busy_led = LED(self, BUSY_LED, 'Busy', '#770', '#ff0')
        self.busy_led.pack(side=TOP, fill=X, padx=10, pady=10)
        self.error_led = LED(self, ERROR_LED, 'Error', '#700', '#f00')
        self.error_led.pack(side=TOP, fill=X, padx=10, pady=10)
        self.root.deiconify()



    def cleanup(self):
        if self.root:
            self.root.destroy()
            self.root = None
        self.inputs.clear()


    # Compatibility
    def setwarnings(self, *args): pass
    def setup(self, *args, **kw): pass


    def output(self, id, status):
        if id == BUSY_LED:
            # Show or hide the projector depending on whether the device is busy
            try:
                cv2.setWindowProperty('projector', cv2.WND_PROP_FULLSCREEN, int(bool(status)))
                cv2.waitKey(1)
            except cv2.error:
                pass
        for led in (self.power_led, self.wifi_led, self.usb_led, self.busy_led, self.error_led):
            if led.id == id:
                if status:
                    led.activate()
                else:
                    led.deactivate()
                break
        self.update()


    def input(self, id):
        if id in self.inputs:
            self.inputs.remove(id)
            return True
        return False


    def update(self):
        self.root.update()


    # Constants
    BCM = IN = OUT = PUD_DOWN = None # Compatibility
    HIGH = True
    LOW = False
        




# GPIO module emulator object
GPIO = VGPIO()

