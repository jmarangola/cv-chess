"""
Autonomously collect data on jetson nano

"""
import pyrealsense2 as rs
import numpy as np
import time
import cv2


pipeline = rs.pipeline()
config = rs.config()
#profile = pipeline.start(config)
#config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
# config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
profile = pipeline.start()


#sensor = pipeline.get_active_profile().get_device().query_sensors()[1]
#sensor.set_option(rs.option.exposure, 156.000)


align_to = rs.stream.color
align = rs.align(align_to)

frames = pipeline.wait_for_frames()


#aligned_depth_frame = aligned_frames.get_depth_frame()
aligned_frames = align.process(frames)
color_frame = aligned_frames.get_color_frame()
color_image = np.asanyarray(color_frame.get_data())
color_image = np.uint8(color_image / 256.0)
# color_image = cv2.cvtColor(color_image, cv2.COLOR_R)

# Filename 
# path = ''
#imageName1 = str(time.strftime("%Y_%m_%d_%H_%M_%S")) +  '_Color.jpg'

# Saving the image 
cv2.imwrite("test.jpg", color_image) 
pipeline.stop()