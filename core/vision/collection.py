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
import numpy as np
import uuid
from PIL import Image
from PIL.ExifTags import TAGS

RUN_CALIBRATION = False # Run calibration sequence or use preexisting board four corners data from config/setup.txt
BOARD_SAVE_DEST= r"board_metadata.jpeg" # Where the debug metadata board visualization image is saved (to ensure we properly setup the metadata)
TMP_DEST = "/home/spark/cv-chess/core/vision/tmp/" # Where images are temporarily saved before being uploaded to drive in a batch
LOCAL_MD_FILENAME = "local_meta.json"
LOCAL_METADATA_JSON_PATH = TMP_DEST + LOCAL_MD_FILENAME
TL = [250, 115]
BL = [250, 687]
TR = [825, 115]
BR = [825, 687]

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

def fen_to_dict(string):

  name_to_num = {
      'p' : 1,
      'b' : 2,
      'n' : 3,
      'r' : 4,
      'q' : 5,
      'k' : 6,
  }

  out = {}
  letters = "ABCDEFGH"
  for i in range(8):
    for j in range(1,9):
      out[letters[i] + str(j)] = 0
  string = string.split('/')
  new_string = []
  for s in string:
    for d in s:
      if d.isnumeric():
        ix = s.index(d)
        for i in range(int(d)-1):
          s = s[0:ix] + '1' + s[ix:]
    new_string.append(s)
  for i in range(8, 0, -1):
    for j in range(8):
      if new_string[8-i][j].isnumeric():
        out[letters[j] + str(i)] = 0
      else:
        out[letters[j] + str(i)] = name_to_num[new_string[8-i][j].lower()]

  return out

def get_sorted_time_saved(images):
    """
    Given a list of image filenames, return a dictionary of image filename : time written to disk pairs.
    Purpose: for debugging dataset

    Args:
        images (list): List of image filenames

    Returns:
        dict: dict of image filenames
    """
    image_dat = []
    for image in images:
        imtmp = Image.open(image)
        tmp = imtmp.getexif()
        image_dat.append(tmp)
    dt = {}
    for exifdata in image_dat:
        idx = image_dat.index(exifdata)
        # iterating over all EXIF data fields
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode()
            # Add datetime field
            if tag == "DateTime":
                dt[images[idx]] = data
                print(f"{tag:25}: {data}")
    
    output = sorted(dt.items(), key=lambda eta: eta[1], reverse=False)
    print(output)
    dt = {}
    for item in output:
        dt[item[0]] = item[1]
        
    with open(TMP_DEST + "datetimes.json", "w") as wr: # dump to json
        json.dump(output, wr)
    return output

def del_batch_from_text_file(file):
    filenames = []
    with open(file, "r") as rd:
        for line in rd.readlines():
            # parse each line for file to delete:
            commaIndex = line.index(",")
            filename = line[:commaIndex]
            os.remove(TMP_DEST + filename)
            
    
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
        
        img = img[105:690, 348:940, :]
        img = rotate_image(img, 1.5)
        
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
    
    """
    

    #pr.delete_board2_64_output(base_directory=TMP_DEST)
    FEN = "5P1R/1Q1RP1P1/3R1P2/QQPPK1R1/1B1K1N2/B1R2N1B/1N2B3R/2B1BN2".upper()
    last_input = None
    df = pd.DataFrame()
    
    
    while input() != "end":
        resp = input("[n] for new fen, [anything key to take an image] >")
        if resp == "new":
          fen = input("Enter a FEN:").upper()
          
        img = realsense.capture_rgb_image() # Capture the image 
        print("Captured image")
        img = img[105:690, 348:940, :]
        img = rotate_image(img, 1.5)
        cv2.imwrite("original.jpg", img)
        
        # Get dict of positions
        temp_dict = fen_to_dict(FEN)
        tiles = pr.board_to_64_files(img, temp_dict, base_directory=TMP_DEST) # Break image up into 64 files
        
        data_frame = pd.DataFrame(tiles)
        data_frame = data_frame.transpose()
        
        frames = [df, data_frame]
        df = pd.concat(frames) # Concatenate dataframe

        
    csv_file = df.to_csv(TMP_DEST + 'my_csv.csv', header=False, index=False)
    # Close streams and end pipeline
    realsense.stop_pipeline()

