# Raspberry Pi I/O functions
# Matthew Kroesche
# ECEN 403-404

import RPi.GPIO as GPIO
import os
import time



# Channel constants
POWER_BUTTON = 14
SNAPSHOT_BUTTON = 15
POWER_LED = 18
WIFI_LED = 27
USB_LED = 22
BUSY_LED = 23
ERROR_LED = 24


# Auto capture timer flag (for debugging)
# If set to a nonzero integer, then at the beginning the processor
# sleeps for that many seconds, and then automatically captures a pointcloud.
# After that the application runs normally.
AUTO_TIMER = 0






class IO(object):

    def __init__(self, master):
        self.master = master
        self.snapshot_reset = False # Flag to make sure only one button press is detected per "click"

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(POWER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(SNAPSHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup([POWER_LED, WIFI_LED, USB_LED, BUSY_LED, ERROR_LED], GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(POWER_LED, GPIO.HIGH) # Power LED should always be lit

    def quit(self):
        GPIO.cleanup()

    def start_busy(self):
        GPIO.output(BUSY_LED, GPIO.HIGH)

    def end_busy(self):
        GPIO.output(BUSY_LED, GPIO.LOW)


    def snapshot(self):
        # Call .master.opencv.snapshot(), make appropriate GPIO calls,
        # and save image to USB/transmit via WiFi if applicable.
        self.start_busy()
        GPIO.output(ERROR_LED, GPIO.LOW)
        # This function blocks. No LEDs will update while the image data is being
        # captured and processed.
        data = self.master.opencv.snapshot()
        self.end_busy()
        GPIO.output(ERROR_LED, GPIO.HIGH if data is None else GPIO.LOW)
        if data is not None:
            self.master.wifi.send(data)
            self.master.usb.send(data)


    def shutdown(self):
        # Shut the Raspberry Pi down
        self.start_busy()
        os.system('sudo shutdown -r now')
        # Don't call end_busy(); wait for the Pi to completely turn off.


    def auto_timer(self, n):
        # DEBUG function that performs an automatic capture.
        for i in range(n):
            # Flash the busy light every second.
            self.start_busy()
            time.sleep(.2)
            self.end_busy()
            time.sleep(.8)
        # Do the capture
        self.snapshot()


    def run(self):
        # Main I/O event loop
        if AUTO_TIMER:
            self.auto_timer(AUTO_TIMER)
        while True:
            # Check for the presence of WiFi connections and USB drives.
            GPIO.output(WIFI_LED, GPIO.HIGH if self.master.wifi.connected() else GPIO.LOW)
            GPIO.output(USB_LED, GPIO.HIGH if self.master.usb.connected() else GPIO.LOW)
            if GPIO.input(SNAPSHOT_BUTTON) == GPIO.HIGH:
                if not self.snapshot_reset:
                    self.snapshot_reset = True
                    self.snapshot()
            else:
                self.snapshot_reset = False
            if GPIO.input(POWER_BUTTON) == GPIO.HIGH:
                self.shutdown()
            time.sleep(.05) # Keep the processor from using up too much CPU time
        

