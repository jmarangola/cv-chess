"""
Automatic dataset upload to google drive

John Marangola - marangol@bc.edu
"""

from logging import root
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tqdm import tqdm
import pandas as pd
import queue
import sys
import os
from os.path import isfile, join
from time import perf_counter
import collection
import cv2

LOCAL_PATH_TO_TMP = "/Users/johnmarangola/Desktop/repos/cv-chess/core/vision/tmp/"
DATASET_METADATA_FILENAME = "my_csv.csv"

METADATA_FIELDS = ["File", "Piece Color", "Piece Type", "Position", "ID", "Batch ID"]

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
import preprocessing as pre

def get_id(drive, name):
    """
    Get the ID of a file in Google Drive

    Args:
        name (str): Filename

    Returns:
        str: Google drive file ID 
    """
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    ids = []
    for file1 in file_list: 
        if file1["title"] == name: 
            ids.append(file1["id"])
    if len(ids) == 1: return ids[0]
    return None

def download(drive, filename):
    """
    Download a file from root directory of google drive

    Args:
        GoogleDrive object: Access to google drive 
        filename (str): Filename to download

    Returns:
        [type]: [description]
    """
    _id = get_id(filename)
    if _id is None: 
        return False
    temp = drive.CreateFile({'id':_id})
    temp.GetContentFile(filename)
    return True

def upload_as_child(drive, filename, folder_id):
    """
    Upload a file to a parent folder

    Args:
        drive (GoogleDrive object): Access to Google Drive
        filename (str): Name of file to be uploaded
        folder_id (str): Parent folder drive ID

    Returns:
        GoogleDriveFile: Uploaded file
    """
    image_file = drive.CreateFile({'parents': [{'id': folder_id}]})
    image_file.SetContentFile(filename)
    image_file.Upload()
    return image_file

def create_root_folder(drive, name):
    """
    Create a root folder in Google Drive

    Args:
        drive (GoogleDrive object): Access to google drive
        name (str): Folder name

    Returns:
        str: Folder ID 
    """
    for file in drive.ListFile({'q': f"'root' in parents and trashed=false"}).GetList():
        if file['title'] == name:
            return None
    root_folder = drive.CreateFile({'title':name, 'mimeType':"application/vnd.google-apps.folder"})
    root_folder.Upload()
    return root_folder['id']

def add_sub_directory(drive, parent_id, sub_dir):
    """
    Add subfolder to parent directory

    Args:
        drive (GoogleDrive object): Access to google drive
        parent_id (str): ID of parent directory
        sub_dir (str): Name of subfolder

    Returns:
        str: ID of subfolder
    """
    # check to make sure sub-directory does not exist yet:
    for file in drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList():
        if file['title'] == sub_dir:
            return False
    sub_dir = drive.CreateFile({'title':sub_dir,"parents":[{'id':parent_id}],'mimeType':"application/vnd.google-apps.folder"})
    sub_dir.Upload()
    return sub_dir['id']

def upload_local_dataset(dataset_name, folder_id, local_path=LOCAL_PATH_TO_TMP, metadata_filename=DATASET_METADATA_FILENAME):
    """
    Upload a local dataset to a Google Drive that named dataset_name.

    Args:
        dataset_name (str): Name of dataset to be uploaded to Google Drive.
        folder_id (str): Google drive ID of folder that the dataset is uploaded within.
        local_path (str, optional): Local absolute path of cv-chess/core/vision/tmp/. Defaults to LOCAL_PATH_TO_TMP.
        metadata_filename (str optional): Name of metadata file (includes .csv). Defaults to DATASET_METADATA_FILENAME.

    Returns:
        [type]: [description]
    """
    # Read in local metadata
    os.chdir(local_path)
    try:
        local_meta = pd.read_csv(metadata_filename)
    except:
        print(f"Unable to load {metadata_filename} from {LOCAL_PATH_TO_TMP}. Exiting...")
        return False
    # Walk through directory, finding valid files to upload
    im_upload = []
    for file in os.listdir(local_path):
        if file.endswith(".jpg") and file[0] == "f":
            im_upload.append(file)
    # initialize empty queue
    #q = queue.Queue()
    t1 = perf_counter() # Start runtime clock 
    # Concurrently execute file uploads using 100 workers for the thread pool
    with ThreadPoolExecutor(max_workers=50) as executor:
        for file in tqdm (im_upload, desc="Threading upload", ascii=False, ncols=100):
            executor.submit(push_to_drive_as_child, drive, local_meta, file, folder_id)
    # Dequeue drive ids, adding each to metadata as it is popped from the queue
    #while not q.empty():
    #    _row, _id = q.get()
    #    local_meta.at[_row, "ID"] = _id
    t1 -= perf_counter()
    # Clean up dataframe from auto-add during copying and writing operations
    #for col in local_meta.columns.tolist():
        # Remove any column that is not an essential metadata field
    #   if col not in METADATA_FIELDS:
    #       del local_meta[col]
    local_meta.to_csv(path_or_buf=local_path + metadata_filename)
    # Upload metadata to google drive
    upload_as_child(drive, metadata_filename, folder_id)
    print(f"Total upload time: {abs(t1)}s")
    
def upload_new_dataset(dataset_name, local_path=LOCAL_PATH_TO_TMP, metadata_filename=DATASET_METADATA_FILENAME):
    """
    Upload a new dataset to folder in Google Drive 

    Args:
        dataset_name (str): Name of new dataset folder
        local_path (str, optional): Path to cv-chess/core/vision/. Defaults to "/Users/johnmarangola/Desktop/repos/cv-chess/core/vision/".

    Returns:
        boolean: True if dataset successfully uploaded, False otherwise.
    """
    drive = authenticate()
    if get_id(drive, dataset_name) is not None:
        print(f"Dataset {dataset_name} already exists. Exiting...")
        return False
    root_id = create_root_folder(drive, dataset_name)
    if root_id is None:
        print("Error.")
        return False
    # Upload the dataset from local to Drive
    return upload_local_dataset(dataset_name, root_id, local_path=LOCAL_PATH_TO_TMP, metadata_filename=DATASET_METADATA_FILENAME)

def add_to_existing_dataset(dataset_name,  local_path=LOCAL_PATH_TO_TMP, cloud_metadata_filename=DATASET_METADATA_FILENAME):
    drive = authenticate()
    folder_id = get_id(drive, dataset_name)
    # Check to ensure that the dataset folder exists in Google Drive
    if folder_id is None:
        print(f"Dataset {dataset_name} not found")
        return False
    folder_id_string = "\'" + folder_id + "\'" + " in parents and trashed=false"  
    file_list = drive.ListFile({'q': folder_id_string}).GetList()
    metadata_id = None
    # Iterate through dataset directory, searching for metadata filename
    for file in file_list:
        if file['title'] == cloud_metadata_filename:
            metadata_id = file['id']
            metadata_file = drive.CreateFile({'id':metadata_id})
            metadata_file.GetContentFile(cloud_metadata_filename)
            break
    # Exit if could not find metadata .csv
    if metadata_id is None:
        print("Metadata .csv not found. Exiting...")
        sys.exit()
    cloud_metadata_df = pd.read_csv(cloud_metadata_filename)

    os.chdir(local_path)
    try:
        local_meta = pd.read_csv(cloud_metadata_filename)
    except:
        print(f"Unable to load metadata file {cloud_metadata_filename} from {LOCAL_PATH_TO_TMP}. Exiting...")
        return False
    # Walk through directory, finding valid files to upload
    im_upload = []
    for file in os.listdir(local_path):
        if file.endswith(".jpg") and file[0] == "f":
            im_upload.append(file)
    # initialize empty queue
    q = queue.Queue()
    t1 = perf_counter() # Start runtime clock 
    # Concurrently execute file uploads using 100 workers for the thread pool
    with ThreadPoolExecutor(max_workers=25) as executor:
        for file in tqdm (im_upload, desc="Threading upload", ascii=False, ncols=100):
            executor.submit(push_to_drive_as_child, drive, local_meta, file, folder_id, q)
    # Dequeue drive ids, adding each to metadata as it is popped from the queue
    while not q.empty():
        _row, _id = q.get()
        local_meta.at[_row, "ID"] = _id
    t1 -= perf_counter()
    temp_frames = [cloud_metadata_df, local_meta]
    resulting_dataframe = pd.concat(temp_frames) 
    # Clean up dataframe from auto-add during copying and writing operations
    for col in resulting_dataframe.columns.tolist():
        # Remove any column that is not an essential metadata field
        if col not in METADATA_FIELDS:
            del resulting_dataframe[col]
    resulting_dataframe.to_csv(path_or_buf=local_path + cloud_metadata_filename)
    # Upload metadata to google drive
    upload_as_child(drive, cloud_metadata_filename, folder_id)
    print(f"Total upload time: {abs(t1)}s")
    return True
    
def authenticate(creds_path=LOCAL_PATH_TO_TMP[:-4]):
    """
    Authenticate for upload

    Args:
        creds_path (str, optional): Path to credentials. Defaults to LOCAL_PATH_TO_TMP[:-4].

    Returns:
        GoogleDrive object: Google drive context object for authenticated user
    """
    # Run authentication:
    gauth = GoogleAuth()
    os.chdir(creds_path)
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    # Authenticate if they're not there
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    # Refresh them if expired
    elif gauth.access_token_expired:
        gauth.Refresh()
    # Initialize the saved creds
    else:
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    # Create a drive object
    drive = GoogleDrive(gauth)
    return drive

def push_to_drive_as_child(drive, local_meta, filename, parent_id):
    """
    Upload an image to Google Drive and store drive file id in queue. Concurrently executed by many threadpool workers in parallel.

    Args:
        drive (GoogleDrive object): [description]
        local_meta (pandas.DataFrame): Pandas dataframe of metadata
        filename (str): Filename of file that is being uploaded
        parent_id (str): Google drive Id of the folder that the image is being uploaded to 
        #//q (queue.Queue): Queue of [row, id] pairs of uploaded images 
    """
    file = drive.CreateFile({'parents': [{'id': parent_id}]})
    file.SetContentFile(filename)
    file.Upload()
    #id = file["id"]
    #temp = local_meta.index[local_meta["File"]==filename].tolist()
    # Add drive file id to meta_data csv iff metadata has been correctly preprocessed for upload
    #if len(temp) != 1:
    #   print("Exiting, input .csv not properly formatted")
    #    sys.exit() # Terminate all execution
    #row = temp[0]
    #q.put([row, id])
    
def upload_iphone_dataset(drive, path_to_iphone_raw_data, csv_path, FEN, local_path=LOCAL_PATH_TO_TMP):
    os.chdir(path_to_iphone_raw_data)
    files = [f for f in os.listdir(os.getcwd()) if isfile(os.path.join(os.getcwd(), f))]
    print(f"number of raw images: {len(files)}")
    # make sure FEN is all uppercase
    FEN = FEN.upper() 
    df = pd.DataFrame()
    try:
        df = pd.read_csv(csv_path, header=False, index=False)
    except:
        print("Could not find existing .csv, initializing empty .csv...")
    for file in files:
        # Get dict of positions
        temp_dict = collection.fen_to_dict(FEN)
        img = cv2.imread(file)
        tiles = pre.board_to_64_files(img, temp_dict, base_directory=local_path) # Break image up into 64 files
        data_frame = pd.DataFrame(tiles)
        data_frame = data_frame.transpose()
        frames = [df, data_frame]
        df = pd.concat(frames) # Concatenate dataframe
    df.to_csv(local_path + 'my_csv.csv', header=False, index=False)
    
def push_to_drive(drive, local_meta, filename, q):
    """
    Push a file to root directory of Drive

    Args:
        drive (GoogleDrive object): Access to Google Drive
        local_meta (pandas.DataFrame): Image metadata dataframe
        filename (str): Name of .jpg image to be uploaded (includes '.jpg')
        q (queue.Queue): Queue of [row, id] pairs uploaded
    """
    file = drive.CreateFile()  
    file.SetContentFile(filename)
    file.Upload()
    id = file["id"]
    temp = local_meta.index[local_meta["File"]==filename].tolist()
    # Add drive file id to meta_data csv
    if len(temp) != 1:
        print("Exiting, input .csv not properly formatted")
        sys.exit()
    row = temp[0]
    local_meta.at[row, "ID"] = id
    q.put([row, id])
    
if __name__ == "__main__":
    drive = authenticate()
    #upload_new_dataset("realsense_dataset1")
    upload_iphone_dataset(drive, "/Users/johnmarangola/Desktop/repos/cv-chess/core/vision/iphone",  LOCAL_PATH_TO_TMP + "my_csv.csv", "5P1R/1Q1RP1P1/3R1P2/QQPPK1R1/1B1K1N2/B1R2N1B/1N2B3R/2B1BN2".upper())
    
    