# Gregory Mueth
# 2635999
# EEL 4660 Robotics Systems
# Fall 2017

# line-follower.py

# A line following robot for Robotics Systems final project
# Coded using Python 2.7.13 and OpenCV 3.3 for a Raspberry Pi 3B running Raspbian
# Uses Raspberry Pi camera module v2

from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
import time
import cv2
import picamera
import numpy as np

# Initialize camera
camera = picamera.PiCamera()
camera.resolution = (192,108)
camera.framerate = 20
rawCapture = PiRGBArray(camera,size=(192,108))
time.sleep(0.1)

# setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

# Loop over all frames captured by camera indefinitely
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	# Display camera input
	image = frame.array
	cv2.imshow('img',image)

	# Create key to break for loop
	key = cv2.waitKey(1) & 0xFF

	# convert to grayscale, gaussian blur, and threshold
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray,(5,5),0)
	ret,thresh1 = cv2.threshold(blur,100,255,cv2.THRESH_BINARY_INV)

	# Erode to eliminate noise, Dilate to restore eroded parts of image
	mask = cv2.erode(thresh1, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# Find all contours in frame
	something, contours, hierarchy = cv2.findContours(mask.copy(),1,cv2.CHAIN_APPROX_NONE)

	# Find x-axis centroid of largest contour and cut power to appropriate motor
	# to recenter camera on centroid.
	# This control algorithm was written referencing guide:
		# Author: Einsteinium Studios
		# Availability: http://einsteiniumstudios.com/beaglebone-opencv-line-following-robot.html
	if len(contours) > 0:
		# Find largest contour area and image moments
		c = max(contours, key = cv2.contourArea)
		M = cv2.moments(c)

		# Find x-axis centroid using image moments
		cx = int(M['m10']/M['m00'])

		if cx >= 150:
			GPIO.output(12, GPIO.LOW)
			GPIO.output(21, GPIO.HIGH)

		if cx < 150 and cx > 40:
			GPIO.output(12, GPIO.HIGH)
			GPIO.output(21, GPIO.HIGH)

		if cx <= 40:
			GPIO.output(12, GPIO.HIGH)
			GPIO.output(21, GPIO.LOW)

	if key == ord("q"):
            break

	rawCapture.truncate(0)

GPIO.output(12, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(20, GPIO.LOW)
GPIO.output(21, GPIO.LOW)

GPIO.cleanup()
