"""
Clear all local data

Run this file to clear all the local data acquired from recording a new dataset
"""
import preprocessing as pr
from collection import TMP_DEST, LOCAL_METADATA_JSON_PATH

pr.delete_board2_64_output(base_directory=TMP_DEST)
with open(LOCAL_METADATA_JSON_PATH, "w") as empty:
    pass
