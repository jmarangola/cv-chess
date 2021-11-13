"""
Test camera func 
Bryan + John 

11/8/2021
"""

import cv2 
import matplotlib.pyplot as plt
import time
import os
# Open the device at the ID 0

cap = cv2.VideoCapture(0)

#Check whether user selected camera is opened successfully.
if not (cap.isOpened()):
    print("Could not open video device")


ret, frame = cap.read()
cv2.imwrite("test22.jpg", frame)




