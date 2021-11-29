"""
Autonomous dataset collection of data for jetson nano

John Marangola - marangol@bc.edu
"""

import datasets
import json
from datasets import Board, ChessPiece, PieceColor, PieceType
from realsense_utils import RealSenseCamera
import preprocessing as pr
import cv2
import pandas as pd
import os 
from os.path import isfile, join
import uuid

RUN_CALIBRATION = False # Run calibration sequence or use preexisting board four corners data from config/setup.txt
BOARD_SAVE_DEST= r"board_metadata.jpeg" # Where the debug metadata board visualization image is saved (to ensure we properly setup the metadata)
TMP_DEST = "/home/spark/cv-chess/core/vision/tmp/" # Where images are temporarily saved before being uploaded to drive in a batch
LOCAL_MD_FILENAME = "local_meta.json"
LOCAL_METADATA_JSON_PATH = TMP_DEST + LOCAL_MD_FILENAME


if __name__ == "__main__":
    # Initialize camera
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
    files = []
    files = [f for f in os.listdir(TMP_DEST) if isfile(os.path.join(TMP_DEST, f))]
    # Check to see if there is pre-existing .csv metadata to add to 
    if LOCAL_MD_FILENAME in files:
        try:
            total_metadata = pd.read_csv(LOCAL_METADATA_JSON_PATH)
        except:
            total_metadata = pd.DataFrame()
    else:
        total_metadata = pd.DataFrame()
    # Loop through input 
    while input() != "exit":
        img = realsense.capture_rgb_image() # Capture the image 
        #img = pr.warp(img, realsense.corner_positions) # warp
        files = pr.board_to_64_files(img, base_directory=TMP_DEST) # Break image up into 64 files 
        piece_types, piece_colors = [], []
        batch_id = uuid.uuid1()
        for tile in sorted(files.keys()):
            temp = board_meta.get_chess_piece(tile)
            if temp is None:
                piece_types.append(None)
                piece_colors.append(None)
            else:
                piece_types.append(temp.piece_type.name)
                piece_colors.append(temp.piece_color.name)
        tmp_meta = pd.DataFrame({
            "File" : [files[file] for file in files.keys()],
            "Position" : [file for file in files.keys()],
            "Piece Type" : piece_types,
            "Piece Color" : piece_colors,
            "Batch ID" : [batch_id for i in range(len(files.keys()))]
        })
        frames = [total_metadata, tmp_meta]
        total_metadata = pd.concat(frames) # Concatenate dataframes
        print(total_metadata)
    total_metadata.to_csv(path_or_buf=LOCAL_METADATA_JSON_PATH)
        
    # Close streams and end pipeline
    realsense.stop_pipeline()

