#!/usr/bin/env python

# Raspberry Pi I/O test
# Matthew Kroesche
# ECEN 404

from DLPScanner.gpio import *

io = IO(None)
io.init()

while True:
    s = input()
    if s.startswith('P'):
        GPIO.output(POWER_LED, GPIO.HIGH)
    elif s.startswith('p'):
        GPIO.output(POWER_LED, GPIO.LOW)
    elif s.startswith('W'):
        GPIO.output(WIFI_LED, GPIO.HIGH)
    elif s.startswith('w'):
        GPIO.output(WIFI_LED, GPIO.LOW)
    elif s.startswith('U'):
        GPIO.output(USB_LED, GPIO.HIGH)
    elif s.startswith('u'):
        GPIO.output(USB_LED, GPIO.LOW)
    elif s.startswith('B'):
        GPIO.output(BUSY_LED, GPIO.HIGH)
    elif s.startswith('b'):
        GPIO.output(BUSY_LED, GPIO.LOW)
    elif s.startswith('E'):
        GPIO.output(ERROR_LED, GPIO.HIGH)
    elif s.startswith('e'):
        GPIO.output(ERROR_LED, GPIO.LOW)
    elif s.startswith('1'):
        print('Power/eject button state: %d' % GPIO.input(EJECT_BUTTON))
    elif s.startswith('2'):
        print('Snapshot button state: %d' % GPIO.input(SNAPSHOT_BUTTON))
    elif not s:
        io.quit()
        break
