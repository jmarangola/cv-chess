from oauth2client.client import GoogleCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.client import GoogleCredentials
import json
import os 
import pandas as pd

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
    Download a file from google drive

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
            return False
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

def upload_new_dataset(drive, dataset_name):
    pass

def add_to_existing_dataset(drive, dataset_name):
    pass

if __name__ == "__main__":
    # Run authentication:
    gauth = GoogleAuth()
    os.chdir("core/vision/")
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    # Create drive object
    drive = GoogleDrive(gauth)

    # Change to path of tmp dir! 
    BASE_PATH = "/Users/johnmarangola/Desktop/repos/cv-chess/core/vision/tmp/"
    
    # Load pandas dataframe from local:
    local_meta = pd.read_csv(r"tmp/local_meta.json")
    im_upload = []
    for file in os.listdir(BASE_PATH):
        if file.endswith(".jpg") and file[0] == "f":
            im_upload.append(file)
    for filename in im_upload: # upload the images to drive
        file = drive.CreateFile()   
        file.SetContentFile(BASE_PATH + filename)
        file.Upload()
        id = file["id"]
        temp = local_meta.index[local_meta["File"]==filename].tolist()
        print(local_meta)
        print(local_meta["File"].tolist())
        # Add drive file id to meta_data csv
        if len(temp) != 1:
            print("Exiting, input .csv not properly formatted")
            break
        row = temp[0]
        local_meta.at[row, "ID"] = id
        print(f"uploading {filename} to {id}...")
    # Upload metadata to google drive
    metadata = drive.CreateFile()
    metadata.SetContentFile(BASE_PATH + "local_meta.json")
    metadata.Upload()
    


    #drive.CreateFile({'id':textfile['id']}).GetContentFile('eng-dl.txt')
    
