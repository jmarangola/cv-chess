from realsense_utils import RealSenseCamera
import cv2
import preprocessing as pre
import numpy as np
from math import pi

TMP_DEST = "/home/spark/cv-chess/core/vision/tmp/"

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

realsense = RealSenseCamera()
img = realsense.capture_rgb_image()
img = img[105:690, 348:940, :]
img = rotate_image(img, 1.5)

pre.delete_board2_64_output()
pre.board_to_64_files(img, base_directory=TMP_DEST)

cv2.imwrite("hardcode.jpg", img)

