# Raspberry Pi I/O functions
# Matthew Kroesche
# ECEN 403

import RPi.GPIO as GPIO
import time



# Channel constants
SNAPSHOT_BUTTON = 15
POWER_LED = 18
WIFI_LED = 27
USB_LED = 22
BUSY_LED = 23
ERROR_LED = 24






class IO(object):

    def __init__(self, master):
        self.master = master
        self.snapshot_reset = False # Flag to make sure only one button press is detected per "click"

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(SNAPSHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup([POWER_LED, WIFI_LED, USB_LED, BUSY_LED, ERROR_LED], GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(POWER_LED, GPIO.HIGH) # Power LED should always be lit

    def quit(self):
        GPIO.cleanup()

    def run(self):
        # Main I/O event loop
        while True:
            # Check for the presence of WiFi connections and USB drives.
            GPIO.output(WIFI_LED, GPIO.HIGH if self.master.wifi.connected() else GPIO.LOW)
            GPIO.output(USB_LED, GPIO.HIGH if self.master.usb.connected() else GPIO.LOW)
            if GPIO.input(SNAPSHOT_BUTTON) == GPIO.HIGH:
                if not self.snapshot_reset:
                    self.snapshot_reset = True
                    GPIO.output(BUSY_LED, GPIO.HIGH)
                    GPIO.output(ERROR_LED, GPIO.LOW)
                    # This function blocks. No LEDs will update while the image data is being
                    # captured and processed.
                    data = self.master.opencv.snapshot()
                    GPIO.output(BUSY_LED, GPIO.LOW)
                    GPIO.output(ERROR_LED, GPIO.HIGH if data is None else GPIO.LOW)
                    if data is not None:
                        self.master.wifi.send(data)
                        self.master.usb.send(data)
            else:
                self.snapshot_reset = False
            time.sleep(.05) # Keep the processor from using up too much CPU time
        

