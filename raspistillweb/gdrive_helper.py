from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from os import path

def get_folder_id(drive,folder_name):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for upload_folder in file_list:
        if upload_folder['title'] == folder_name:
            return upload_folder['id']
    
    return None
    

def get_all_uploaded_images(folder_name,drive=None):
    if (drive is None):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
    
    fid = get_folder_id(drive,folder_name)
    
    print fid
    
    if (fid is not None):
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"% (fid)}).GetList()
    
        return file_list
    else:
        return []
        
        
def delete_file(folder_name,file_name):
    file_list = get_all_uploaded_images(folder_name)
    
    _,file_name = path.split(file_name)
    
    title,_ = path.splitext(file_name)
    
    for f in file_list:
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'+ f['title'] 
        if f['title'] == title:
            f.Delete()

    

def upload_file(fullpath,mimetype,app_settings):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    
    upload_folder_id = get_folder_id(drive,app_settings.gdrive_folder)

    _,fname = path.split(fullpath)
    fname,ext = path.splitext(fname)

    upfile = drive.CreateFile({'title': fname, 'mimeType':mimetype,
    "parents": [{"kind": "drive#fileLink", "id": upload_folder_id}]})
    upfile.SetContentFile(fullpath)
    upfile.Upload()

def gdrive_init(folder_name,user,secret,yaml_filename):
    with open(yaml_filename, 'r') as gdrive_setting_file:
        gdrive_settings_data = gdrive_setting_file.read()

    gdrive_settings_data = gdrive_settings_data.replace('clienttext', user)
    gdrive_settings_data = gdrive_settings_data.replace('secrettext', secret)
                    
    with open(yaml_filename, 'w') as gdrive_setting_file:
        gdrive_setting_file.write(gdrive_settings_data)
        
    print "Google Authorization in progress"
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    folder_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    new_folder_data = {'title' : folder_name, 'mimeType' : 'application/vnd.google-apps.folder'}
    upload_folder_exists = False
    for upload_folder in folder_list:
        if upload_folder['title'] == folder_name:
            upload_folder_id = upload_folder['id']
            upload_folder_exists = True
    if not upload_folder_exists:
        #new_folder_data = {'title' : app_settings.gdrive_folder, 'mimeType' : 'application/vnd.google-apps.folder'}
        new_folder = drive.CreateFile(new_folder_data)
        new_folder.Upload()
        upload_folder_id = new_folder['id']
