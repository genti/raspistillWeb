import warnings
import time
import views as v
from glob import glob
import os

try:
	from pydrive.auth import GoogleAuth, AuthenticationError
	from pydrive.drive import GoogleDrive
except:
	warnings.warn('The module pydrive is not installed. Google Drive uploads will not work.')

from os import path

GDRIVE_POOLING=60 #every hour
GDRIVE_OBJECT = None

try:
	from apscheduler.schedulers.background import BackgroundScheduler as Scheduler
	
	GDRIVE_SCHEDULER=None#Scheduler()
			
except ImportError:
	GDRIVE_SCHEDULER=None
	warnings.warn('The module APScheduler is not installed. Google Drive uploads will not work.')


def gdrive_uploader_job(app_settings):
    if (is_gdrive_operative(app_settings)):
		lst = glob(os.path.join(v.RASPISTILL_DIRECTORY,'IMG*.'+app_settings.encoding_mode))
		
		file_list = get_all_uploaded_images(app_settings.gdrive_folder,app_settings.gdrive_authentication_token)
		file_list = [f['title'] for f in file_list]
		
		i=0
		for f in lst:
			_,fname = os.path.split(f)
			title,_ = os.path.splitext(fname)
			
			if (title not in file_list):
				print "Uploading "+title+" on GDrive"
				upload_file(f,v.MIME_TYPES[app_settings.encoding_mode],app_settings)
				i=i+1
		
		print "Uploaded " + str(i) + " file(s)"

def init_scheduler(app_settings):
    if (GDRIVE_SCHEDULER is not None) and (app_settings.gdrive_enabled.lower() == 'yes') :

		GDRIVE_SCHEDULER.add_job(gdrive_uploader_job,'interval',minutes=GDRIVE_POOLING,args=[app_settings])
		GDRIVE_SCHEDULER.start()

		print "GDrive scheduler started"

def get_folder_id(folder_name):
    drive = gdrive_authentication()
    
    if (drive is not None):
		file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
		for upload_folder in file_list:
			if upload_folder['title'] == folder_name:
				return upload_folder['id']
    
    return None
    

def get_all_uploaded_images(folder_name,auth_token):    
    fid = get_folder_id(folder_name)
    
    print fid
    
    if (fid is not None):
		drive = gdrive_authentication(auth_token)
		if (drive is not None):
			file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"% (fid)}).GetList()
    
			return file_list
		else:
			return None
    else:
        return []
        
        
def delete_file(folder_name,file_name,authcode):
    file_list = get_all_uploaded_images(folder_name,auth_code)
    
    _,file_name = path.split(file_name)
    
    title,_ = path.splitext(file_name)
    
    for f in file_list:
        if f['title'] == title:
            f.Delete()

    

def upload_file(fullpath,mimetype,app_settings):
    drive = gdrive_authentication();
    
    upload_folder_id = get_folder_id(app_settings.gdrive_folder)

    _,fname = path.split(fullpath)
    fname,ext = path.splitext(fname)

    upfile = drive.CreateFile({'title': fname, 'mimeType':mimetype,
    "parents": [{"kind": "drive#fileLink", "id": upload_folder_id}]})
    upfile.SetContentFile(fullpath)
    upfile.Upload()
    
    
def gdrive_authentication(auth_code=None , force=False):
	global GDRIVE_OBJECT
	if (force or (GDRIVE_OBJECT is None)):
		if (auth_code is not None):
			print "Google Authorization in progress..."
			gauth = GoogleAuth(http_timeout=20)
			try:
				gauth.Auth(auth_code)
				GDRIVE_OBJECT = GoogleDrive(gauth)
			except AuthenticationError, ae:
				return None
		else:
			return None
	return GDRIVE_OBJECT

def is_gdrive_operative(app_settings):
	return (app_settings.gdrive_enabled.lower() == 'yes') and (app_settings.gdrive_authentication_token is not None) and (len(app_settings.gdrive_authentication_token)>0)
	
def gdrive_auth_url():
	gauth = GoogleAuth()
	return gauth.GetAuthUrl()

def gdrive_init(folder_name,auth_code,yaml_filename):
    #with open(yaml_filename, 'r') as gdrive_setting_file:
    #    gdrive_settings_data = gdrive_setting_file.read()

    #gdrive_settings_data = gdrive_settings_data.replace('clienttext', user)
    #gdrive_settings_data = gdrive_settings_data.replace('secrettext', secret)
                    
    #with open(yaml_filename, 'w') as gdrive_setting_file:
    #    gdrive_setting_file.write(gdrive_settings_data)
        
    drive = gdrive_authentication(auth_code,True)
    
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
