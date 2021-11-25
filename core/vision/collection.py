"""
Autonomously collection of data for jetson nano
"""
import cv2
from realsense_utils import RealSenseCamera
import preprocessing as pr

RUN_CALIBRATION = False

if __name__ == "__main__":
    realsense = RealSenseCamera()
    
    # Check if calibration sequence must be run
    if RUN_CALIBRATION:
        realsense.calibrate_board_pos()
    
    # Loop through input 
    while input() != "exit":
        img = realsense.capture_rgb_image()
        img = pr.warp(img, realsense.corner_positions)
        cv2.imwrite("tmp/test.jpg", img)
        #fl = pr.board_to_64_files(img)
        
    # Close streams and end pipeline
    realsense.stop_pipeline()

