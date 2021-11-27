from oauth2client.client import GoogleCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.client import GoogleCredentials

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

if __name__ == "__main__":
    gauth = GoogleAuth()
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

    drive = GoogleDrive(gauth)

    textfile = drive.CreateFile()
    textfile.SetContentFile('eng.txt')
    textfile.Upload()
    print(textfile)
