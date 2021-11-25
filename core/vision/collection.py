"""
Autonomously collection of data for jetson nano
"""

import datasets
from datasets import Board, ChessPiece, PieceColor, PieceType
from realsense_utils import RealSenseCamera
import preprocessing as pr
import cv2
import pandas as pd

RUN_CALIBRATION = False
BOARD_SAVE_DEST= r"board_metadata.jpeg"

if __name__ == "__main__":
    realsense = RealSenseCamera()
    
    """
    # Check if calibration sequence must be run
    if RUN_CALIBRATION:
        realsense.calibrate_board_pos()
    
    if realsense.get_board_corners() is None:
        print("Failed to run calibration. Exiting...")
        exit()
    """
    board_meta = Board()
    # Add pieces to metadata csv
    board_meta.add_pieces({
                            "A1":ChessPiece(PieceType.KNIGHT, PieceColor.BLUE), "A2":ChessPiece(PieceType.PAWN, PieceColor.BLUE), "A3":ChessPiece(PieceType.PAWN, PieceColor.ORANGE)
                         })
    board_meta.display_board(dest=BOARD_SAVE_DEST)
    print(f"Verify board is correct output dest={BOARD_SAVE_DEST}.\nContine [Y] or Exit [E]?")
    validate = input()
    if validate.upper() == "E" or validate.upper() == "N":
        print("Exiting...")
        realsense.stop_pipeline()
        exit()
    # Loop through input 
    while input() != "exit":
        pass
        #img = realsense.capture_rgb_image()
        #img = pr.warp(img, realsense.corner_positions)
        #cv2.imwrite("tmp/test.jpg", img)

        
    # Close streams and end pipeline
    realsense.stop_pipeline()

