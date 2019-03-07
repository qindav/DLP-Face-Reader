# DLP Structured Light Scanner
Texas A&M ECEN 403/404 Capstone Project

Matthew Kroesche

David Qin

This repo contains a library and interface for stereo 3D structured light scanning, processing, and calibration using a Raspberry Pi 3 together with a Pi camera, a USB camera, and a display projector. (Any display may be used; in this project we used the TI DLP4500 LightCrafter EVM.)

### Steps to set up the Raspberry Pi

1. Install OpenCV+Python on the Raspberry Pi. Version 4.0.0 or later is required. A step-by-step walkthrough for doing this can be found [here](https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi).

2. Go into your virtual workspace if you aren't already there:
```
$ source ~/.profile
$ workon cv
```

3. Check out the repository into a folder called DLPScanner inside the CV environment. Make sure the location you check it out to is one of the locations on the Python path. You can get the list by typing:
```
$ python -c "import sys; print(sys.path)"
```

4. Create a shortcut on the Pi Desktop to the folder. First, cd into the directory where you created the folder, and then type
```
$ sudo ln -s DLPScanner ~/Desktop/DLPScanner
```

5. While still inside the CV workspace, install the Pi Camera and GPIO libraries:
```
$ pip install picamera
$ pip install RPi.GPIO
```

6. (Optional) You can also install VPython, to use the visualization script that comes with the library:
```
$ pip install vpython
```
If you skip this step, you will not be able to visualize the pointclouds using the visualize.py script, although you can still generate them and view them using some other tool.

VPython is not as flexible of an interface. In particular, we had trouble getting it to run inside the virtual workspace, so we have installed it in the regular environment. Also, the visualization runs kind of slow by default; it can be sped up by changing the driver settings in raspi-config, but this may have ill effects on the structured light projection behavior. We don't recommend changing any of those settings unless you know exactly what you're doing.

7. Set up both the Pi Ribbon camera and the USB camera. You can also use two USB cameras instead of using the pi ribbon; if you do this you'll need to change a couple of lines of code in cvstereo.py. Instead of
```
self.cam1 = PiCamera()
```
do
```
self.cam1 = CVCamera(1)
self.cam1.set_n(5)
```
OpenCV may give the second USB camera some ID other than 1; trial and error may need to be used to determine what this ID is. The OpenCV camera interface is strange, and lacks many features.

8. Set up a display projector. This can be any projector that is connected to the Pi's HDMI port in lieu of a monitor. We have found it helpful to obtain an HDMI splitter to view the display and project simultaneously. Once this is done, make sure the SCREEN_SIZE macro at the top of cvstereo.py is set properly to the dimensions of the display, e.g.
```
SCREEN_SIZE = (1280, 800)
```
for a 1280 by 800 pixel display.

9. Fix the cameras in place, such that they are roughly at the same vertical level, but spaced at least a couple of inches apart from each other horizontally. They should probably be positioned a couple of inches above the projector as well. Make sure that both cameras can see the entire pattern being projected; this is more of an issue for cameras with a narrower FOV. To preview the Pi camera, you can do
```
$ python -c "import picamera; cam = picamera.PiCamera(); cam.start_preview()"
```
Very important: If you move either of the cameras or adjust their focus, you will need to calibrate again. Thus it's important to make sure they're fixed firmly in a position where they can see the entire projected pattern before you continue to step 10!

10. Calibrate the cameras. (The projector is not needed for this step.) You will need a calibration board, which is a large black-and-white chessboard. It can have any number of squares horizontally and vertically, although more is generally better. Make sure the CB_SIZE macro at the top of cvstereo.py is set properly; it should be a 2-tuple with the first element equal to the number of vertical squares, minus one, and the second equal to the number of horizontal squares, minus one. (This is because it counts inside corners, rather than actual squares.) In our tests we used a 10 by 8 chessboard, so we have it set by default to
```
CB_SIZE = (7, 9)
```
Once this is set properly, run the calibration script in the DLPScanner folder:
```
$ ~/Desktop/DLPScanner/calibrate
```
You should see two windows pop up on screen, one showing the preview for each camera. You should also be prompted to capture. You can press any key to capture an image of the calibration board; once this is done the console output will indicate whether the board was detected or not. If it was detected by *both* cameras, the corners will be overlaid onto the image, and you will be prompted to press a key again to dismiss this. Also the total number of successful calibration captures is displayed in the console. For good calibration, we recommend going up to at least 30 successful captures, holding the chessboard at a variety of different angles, distances, and orientations. Press ESCAPE when you're finished. The calibration parameters will all be printed out to the console.

11. Copy the calibration parameters (all the output starting with the line "# Intrinsic matrix of first camera") and paste it to replace the calibration data that is currently at the top of cvstereo.py.

12. Set up the GPIO. This can just be a simple breadboard with buttons and LEDs connected to the Pi. Make sure you have a resistor in series with every button and LED to keep it from being shorted! Some buttons and LEDs can be left off, but at minimum you should have a snapshot button and error/busy LEDs. The BCM port numbers for all the buttons and LEDs are at the top of gpio.py. If you want to build an actual physical device, you can also design a printed/soldered circuit board to connect to the pi without too much trouble, but for getting started a breadboard works just fine.

13. Start scanning! Run this command:
```
$ ~/Desktop/DLPScanner/init
```
to kick off the scanning routine. You should see the Power and Busy LEDs light up, followed by the display being blacked out. (If you want to quit at any time, you can do Ctrl+Alt+Delete to kill the Python task from the keyboard, or press the Power button to shut down the pi.) Wait for the Busy LED to turn off, and then press the Snapshot button to take a scan. The Busy LED will come on while the capturing and processing is going on, and then one of two things happens: either the Error LED lights up to indicate an invalid pointcloud, or a working pointcloud (.pcd) file is generated. This file is sent to the remote application, if a connection is established, and saved to the USB drive if one is present. It is also saved temporarily to the pi at the following location:
```
/home/pi/Desktop/DLPScanner/socketsfile/data/upload.pcd
```

14. Assuming you've installed VPython, the pointcloud just captured can be viewed by simply typing
```
$ ~/Desktop/DLPScanner/visualize.py
```
This script can also be given an argument, which is the filename of the pointcloud to view. It defaults to whatever pointcloud was most recently scanned.






### Remote Application

Now updated with simple socket connections and small support for it.
This was a modified project based off of [threejs' trackball example.](https://threejs.org/examples/misc_controls_trackball.html)
It also uses a socketio file sender found [here.](https://github.com/rico345100/socket.io-file-example)


zaghetto pcd file found [here.](http://groovemechanic.net/three.js/examples/models/pcd/)
bunny files found [here.](https://github.com/PointCloudLibrary/pcl/tree/master/test)

### Steps
```
$ npm install
$ node server
```
### Accessing page
Use a browser and go to:
```
localhost:3000
```

No support is provided for ip addresses so far when viewing on other devices (in this case for the pi):
```
192.168.0.26:3000
```
