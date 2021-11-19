"""
Autonomously collect data on jetson nano

"""

import pyrealsense2 as rs
import numpy as np
import cv2


pipeline = rs.pipeline()
config = rs.config()


config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

profile = pipeline.start(config)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1.5 
clipping_distance = clipping_distance_in_meters / depth_scale


align_to = rs.stream.color
align = rs.align(align_to)

frames = pipeline.wait_for_frames()

aligned_frames = align.process(frames)
aligned_depth_frame = aligned_frames.get_depth_frame()
color_frame = aligned_frames.get_color_frame()

depth_image = np.asanyarray(aligned_depth_frame.get_data())
color_image = np.asanyarray(color_frame.get_data())


# Remove background - Set pixels further than clipping_distance to grey
grey_color = 153
depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

# Render images
depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
images = np.hstack((bg_removed, depth_colormap))
cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)

# Filename 
# path = ''
imageName1 = str(time.strftime("%Y_%m_%d_%H_%M_%S")) +  '_Color.jpg'
imageName2 = str(time.strftime("%Y_%m_%d_%H_%M_%S")) +  '_Depth.jpg'
imageName3 = str(time.strftime("%Y_%m_%d_%H_%M_%S")) +  '_bg_removed.jpg'
imageName4 = str(time.strftime("%Y_%m_%d_%H_%M_%S")) +  '_ColorDepth.jpg'
imageName5 = str(time.strftime("%Y_%m_%d_%H_%M_%S")) +  '_DepthColormap.jpg'

# Saving the image 
cv2.imwrite(imageName1, color_image) 
cv2.imwrite(imageName2, depth_image) 
cv2.imwrite(imageName3, images) 
cv2.imwrite(imageName4, bg_removed )
cv2.imwrite(imageName5, depth_colormap )

key = cv2.waitKey(1)
# Press esc or 'q' to close the image window
cv2.destroyAllWindows()