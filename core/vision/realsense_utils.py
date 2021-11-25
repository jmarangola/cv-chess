"""
Realsense utils for capturing data and configuring the realsense for our constrained environment
"""
import pyrealsense2 as rs
import numpy as np
import json
import time
import cv2

class RealSenseCamera:
    """
    Class for setting up realsense camera with correct default settings and performing common operations
    """
    def __init__(self):
        """
        Initialize the camera with exposure settings
        """
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # Start the pipline
        profile = self.pipeline.start(self.config)
        # Enable depth and color streams
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        # Set the exposure settings
        self.sensor = self.pipeline.get_active_profile().get_device().query_sensors()[1]
        self.sensor.set_option(rs.option.exposure, 1000.000)
        self.device = self.find_device_that_supports_advanced_mode()

    def stop_pipeline(self):
        """
        Stop the pipeline
        """
        self.pipeline.stop()

    def capture_rgb_image(self, dest):
        """
        Capture an rgb image on the realsense, returning it as an ndarray

        Args:
            dest (str): relative path and filename (wihout .jpg extension)

        Returns:
            ndarray: RGB image ndarray
        """
        align_to = rs.stream.color
        align = rs.align(align_to)
        frames = self.pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        self.pipeline.stop()
        # Saving the image
        try:
            imageName1 = '.jpg'
            cv2.imwrite(dest + imageName1, color_image)
        except:
            print(f"realsense_utils could not save as {dest}.")
        return color_image

    def find_device_that_supports_advanced_mode():
        """
        Find a connected camera that is supports advanced mode

        Raises:
            Exception: No D400 product line device that supports advanced mode was found

        Returns:
            rs.device: realsense device object  
        """
        DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07", "0B3A", "0B5C"]
        ctx = rs.context()
        ds5_dev = rs.device()
        devices = ctx.query_devices()
        for dev in devices:
            if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
                if dev.supports(rs.camera_info.name):
                    print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
                return dev
        raise Exception("No D400 product line device that supports advanced mode was found")
