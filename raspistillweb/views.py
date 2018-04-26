# raspistillWeb - web interface for raspistill
# Copyright (C) 2013 Tim Jungnickel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response, FileResponse
from httplib2 import ServerNotFoundError
from httplib import ResponseNotReady

import os
import shutil
import signal
import threading
import tarfile
import zipfile
import fileinput
import gdrive_helper as G
import multisensors as ms

from subprocess import call, Popen, PIPE 
from time import gmtime, strftime, localtime, asctime, mktime, sleep
from stat import *
from datetime import *
from glob import glob
from sys import stderr

import re



#import Image
from PIL import Image
##from bqapi.bqclass import fromXml
#import bqapi as zzz
from bqapi.comm import BQSession#, BQCommError
from bqapi.util import save_blob
from lxml import etree
#from time import time
from socket import gethostname

from sqlalchemy.exc import DBAPIError
import transaction
from .models import (
    DBSession,
    Picture,
    Settings,
    Timelapse,
    CameraParams
    )

# Modify these lines to change the directory where the pictures and thumbnails
# are stored. Make sure that the directories exist and the user who runs this
# program has write access to the directories. 
RASPISTILL_ROOT = 'raspistillweb'
RASPISTILL_DIRECTORY = 'raspistillweb/pictures/' # Example: /home/pi/pics/
THUMBNAIL_DIRECTORY = 'raspistillweb/thumbnails/' # Example: /home/pi/thumbs/
TIMELAPSE_DIRECTORY = 'raspistillweb/time-lapse/' # Example: /home/pi/timelapse/
CAMERA_CALIBR_DIRECTORY = 'raspistillweb/camera-calibr'
TIMESTAMP = '%Y-%m-%d_%H-%M'

IMAGE_EFFECTS = [
    'none', 'negative', 'solarise', 'sketch', 'denoise', 'emboss', 'oilpaint', 
    'hatch', 'gpen', 'pastel', 'watercolour', 'film', 'blur', 'saturation', 
    'colourswap', 'washedout', 'posterise', 'colourpoint', 'colourbalance', 
    'cartoon'
    ]

EXPOSURE_MODES = [
    'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports',
    'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'
    ]

AWB_MODES = [
    'off', 'auto', 'sun', 'cloud', 'shade', 'tungsten', 'fluorescent',
    'incandescent', 'flash', 'horizon'
    ]

ISO_OPTIONS = [
    'auto', '100', '150', '200', '250', '300', '400', '500', 
    '600', '700', '800'
    ]

IMAGE_RESOLUTIONS = [
    '800x600', '1024x768', '1280x720', '1920x1080', '2592x1944', '3280x2464'
    ]

ENCODING_MODES = [
    'jpg', 'png', 'bmp', 'gif'
    ]

MIME_TYPES={ 'jpg':'image/jpeg', 'png':'image/png', 'bmp':'image/bmp', 'gif':'image/gif'}


CALIBR_DEF_NUMBER_IMAGES = 12
CALIBR_DEF_INTERVAL = 3
CALIBR_DEF_CHECKER_VERTICAL = 13
CALIBR_DEF_CHECKER_HORIZONTAL = 9
CALIBR_DEF_RESIZE = (1024,768)


#TODO: check version of camera (v1 or v2)
IMAGE_HEIGHT_ALERT = 'Please enter an image height value between 0 and 2464 (or 1944 for the v1 camera).'
IMAGE_WIDTH_ALERT = 'Please enter an image width value between 0 and 3280 (or 2592 for the v1 camera).'
IMAGE_EFFECT_ALERT = 'Please enter a valid image effect.'
EXPOSURE_MODE_ALERT = 'Please enter a valid exposure mode.'
ENCODING_MODE_ALERT = 'Please enter a valid encoding mode.'
AWB_MODE_ALERT = 'Please enter a valid AWB mode.'
ISO_OPTION_ALERT = 'Please enter a valid ISO option.'
IMAGE_ROTATION_ALERT = 'Please enter a valid image rotation option.'
BISQUE_USER_ALERT = 'Please enter a valid BisQue username.'
BISQUE_PSWD_ALERT = 'Please enter a valid BisQue password.'
BISQUE_ROOT_URL_ALERT = 'Please enter a valid BisQue root URL.'
GDRIVE_ALERT = 'Something went wrong uploading to Google Drive'
GDRIVE_FOLDER_ALERT = 'Something went wrong uploading to your Google Drive folder. Make sure there are no special characters in the folder name.'
GDRIVE_USER_ALERT = 'Please enter a valid Google Drive client ID'
GDRIVE_SECRET_ALERT = 'Please enter a valid Google Drive Secret token'

#THUMBNAIL_SIZE = '240:160:80'
THUMBNAIL_SIZE = 240, 160
THUMBNAIL_JPEG_QUALITY = 80

timelapse = False


timelapse_database = None
p_timelapse = None

preferences_fail_alert = []
preferences_success_alert = False

# not implemented yet
image_quality = '100'
image_sharpness = '0'
image_contrast = '0'
image_brightness = '50'
image_saturation = '0'


###############################################################################
################################### Views #####################################
###############################################################################


# View for the /settings site
@view_config(route_name='settings', renderer='settings.mako')
def settings_view(request):
    app_settings = DBSession.query(Settings).first()
    global preferences_fail_alert, preferences_success_alert
        
    preferences_fail_alert_temp = []    
    if preferences_fail_alert is not []:
        preferences_fail_alert_temp = preferences_fail_alert
        preferences_fail_alert = []
     
    preferences_success_alert_temp = False  
    if preferences_success_alert:
        preferences_success_alert_temp = True
        preferences_success_alert = False
    
    host_name = gethostname()
    
    ips,macs = ms.get_clients()
    clients = []
    
    for ip,mac in zip (ips,macs):
        clients.append({'ip':ip,'mac':mac})
    
    return {'project' : 'raspistillWeb',
            'hostName' : host_name,
            'image_effects' : IMAGE_EFFECTS,
            'image_effect' : app_settings.image_effect,
            'exposure_modes' : EXPOSURE_MODES,
            'exposure_mode' : app_settings.exposure_mode,
            'awb_modes' : AWB_MODES,
            'awb_mode' : app_settings.awb_mode,
            'encoding_modes' : ENCODING_MODES,
            'encoding_mode' : app_settings.encoding_mode,
            'iso_options' : ISO_OPTIONS, 
            'image_iso' : app_settings.image_ISO,
            'image_resolutions' : IMAGE_RESOLUTIONS,
            'image_width' : str(app_settings.image_width),
            'image_height' : str(app_settings.image_height),
            'image_rotation' : app_settings.image_rotation,
            'timelapse_interval' : str(app_settings.timelapse_interval),
            'timelapse_time' : str(app_settings.timelapse_time),
            'bisque_enabled' : str(app_settings.bisque_enabled),
            'bisque_user' : str(app_settings.bisque_user),
            'bisque_pswd' : str(app_settings.bisque_pswd),
            'bisque_root_url' : str(app_settings.bisque_root_url),
            'bisque_local_copy' : str(app_settings.bisque_local_copy),
            'gdrive_enabled' : str(app_settings.gdrive_enabled),
            'gdrive_folder' : str(app_settings.gdrive_folder),
            'gdrive_user' : str(app_settings.gdrive_user),
            'gdrive_secret' : str(app_settings.gdrive_secret),
            'gdrive_file_delete' : str(app_settings.gdrive_delete_files),
            'preferences_fail_alert' : preferences_fail_alert_temp,
            'preferences_success_alert' : preferences_success_alert_temp,
            'number_images' :  str(app_settings.number_images),
            'command_before_shot': str(app_settings.command_before_shot),
            'command_after_shot': str(app_settings.command_after_shot),
            'command_before_sequence': str(app_settings.command_before_sequence),
            'command_after_sequence': str(app_settings.command_after_sequence),
            'multisensor_enabled': str(app_settings.multisensor_enabled) if (app_settings.multisensor_enabled is not None) else 'No',
            'async_download' : str(app_settings.multisensor_download_asynch) if (app_settings.multisensor_download_asynch is not None) else 'No',
            'sensors_name': app_settings.sensors_name if (app_settings.sensors_name is not None) or (app_settings.sensors_name=='') else ms.get_default_clients_name() ,
            'clients':clients,
            'hdr_enabled': str(app_settings.hdr_enabled) if (app_settings.hdr_enabled is not None) else 'No',
            'hdr_exposure_times': app_settings.hdr_exposure_times if app_settings.hdr_exposure_times is not None else '',
            'downloadInProgress': check_new_images_on_devices(app_settings)
            } 


def check_new_images_on_devices(app_settings):
    
    if ((app_settings.multisensor_enabled.lower() == 'yes') and (app_settings.multisensor_download_asynch.lower() == 'yes')):
        clients = ms.get_registered_clients(app_settings.sensors_name)
        hosts = [(ip,clients[ip]) for ip in clients]
        return ms.check_for_new_images(hosts, app_settings.encoding_mode)
    else:
        return False

# View for the /archive site
@view_config(route_name='archive', renderer='archive.mako')
def archive_view(request):

    pictures = DBSession.query(Picture).all()
    picturedb = []
    
    app_settings = DBSession.query(Settings).first()
    
    try:
        if (app_settings.gdrive_enabled == 'Yes'):
            file_list = G.get_all_uploaded_images(app_settings.gdrive_folder)
            file_list = [f['title'] for f in file_list]
        else:
            file_list = []
    except :
        file_list = None
            
    for picture in pictures:
        imagedata = get_picture_data(picture,file_list)
        picturedb.insert(0,imagedata)
    return {'project' : 'raspistillWeb',
            'database' : picturedb,
            'downloadInProgress': check_new_images_on_devices(app_settings)
            }
            

# View for the / site
@view_config(route_name='home', renderer='home.mako')
def home_view(request):
    pictures = DBSession.query(Picture).all()
    app_settings = DBSession.query(Settings).first()
    
    if len(pictures) == 0:
        return HTTPFound(location='/photo')
    else:
        picture_data = get_picture_data(pictures[-1])
        if timelapse:            
            return {'project': 'raspistillWeb',
                    'imagedata' : picture_data,
                    'timelapse' : timelapse,
                    'downloadInProgress': check_new_images_on_devices(app_settings)
                    }
        #elif (mktime(localtime()) - mktime(picture_data['timestamp'])) > 1800: 
        #    return HTTPFound(location='/photo') 
        else:
            return {'project': 'raspistillWeb',
                    'imagedata' : picture_data,
                    'timelapse' : timelapse,
                    'downloadInProgress': check_new_images_on_devices(app_settings)
                    }

# View for the /timelapse site
@view_config(route_name='timelapse', renderer='timelapse.mako')
def timelapse_view(request):
    global timelapse_database

    #if timelapse_database is not None:
    #    DBSession.add(timelapse_database)
    #    timelapse_database = None

    app_settings = DBSession.query(Settings).first()
    timelapse_collection = DBSession.query(Timelapse).all()
    timelapsedb = []
    for timelapse_rec in timelapse_collection:
        timelapse_data = get_timelapse_data(timelapse_rec)
        timelapsedb.insert(0,timelapse_data)
    
    return {'project': 'raspistillWeb',
            'timelapse' : timelapse,
            'timelapseInterval' : str(app_settings.timelapse_interval),
            'timelapseTime' : str(app_settings.timelapse_time),
            'timelapseDatabase' : timelapsedb
            }

# View for the timelapse start - no site will be generated
@view_config(route_name='timelapse_start')
def timelapse_start_view(request):
    global timelapse
    timelapse = True
    filename = strftime(TIMESTAMP, localtime())
    t = threading.Thread(target=take_timelapse, args=(filename, ))
    t.start()
    return HTTPFound(location='/timelapse') 

# View for the timelapse stop - no site will be generated
@view_config(route_name='timelapse_stop')
def timelapse_stop_view(request):
    global timelapse, p_timelapse
    if p_timelapse.poll() is None:
        os.killpg(p_timelapse.pid, signal.SIGTERM)
    timelapse = False
    return HTTPFound(location='/timelapse')

@view_config(route_name='timelapse_upload_gdrive')
def timelapse_upload_gdrive_view(request):
    app_settings = DBSession.query(Settings).first()
    t_id = request.params['id']
    tl = DBSession.query(Timelapse).filter_by(id=int(t_id)).first()
    
    G.upload_file(TIMELAPSE_DIRECTORY + tl.filename + '.zip','application/zip',app_settings)

    return HTTPFound(location='/timelapse')


# View to take a photo - no site will be generated
@view_config(route_name='photo')
def photo_view(request,ret=False):
    if timelapse:
        return HTTPFound(location='/') 
    else:
        app_settings = DBSession.query(Settings).first()
        basename = strftime("IMG_"+TIMESTAMP, localtime())
        filename = basename + '.' + app_settings.encoding_mode
        take_photo(filename)
        
        #f = open(RASPISTILL_DIRECTORY + filename,'rb')
        #exif = extract_exif(exifread.process_file(f))    
        filedata = extract_filedata(os.stat(RASPISTILL_DIRECTORY + filename))
        #filedata.update(exif)
        filedata['filename'] = filename
        filedata['image_effect'] = app_settings.image_effect
        filedata['exposure_mode'] = app_settings.exposure_mode
        filedata['awb_mode'] = app_settings.awb_mode
        filedata['encoding_mode'] = app_settings.encoding_mode
        filedata['ISO'] = str(app_settings.image_ISO)
        #filedata['exposure_time'] = app_settings.exposure_time
        im = Image.open(RASPISTILL_DIRECTORY + filename)
        width, height = im.size
        filedata['resolution'] = str(width) + ' x ' + str(height)
        im.thumbnail(THUMBNAIL_SIZE);
        im.mode='RGB'
        
        im.save(THUMBNAIL_DIRECTORY + basename + '.' + app_settings.encoding_mode, quality=THUMBNAIL_JPEG_QUALITY, optimize=True, progressive=True)
        '''
        imagedata = dict()
        imagedata['filename'] = filename
        imagedata['image_effect'] = 'test'
        imagedata['exposure_mode'] = 'test'
        imagedata['awb_mode'] = 'test'
        imagedata['resolution'] = '800x600'
        imagedata['ISO'] = '300'
        imagedata['exposure_time'] = '100'
        imagedata['date'] = 'test'
        imagedata['timestamp'] = localtime()
        imagedata['filesize'] = 100
        '''
        picture = Picture(filename=filedata['filename'],
                        image_effect=filedata['image_effect'],
                        exposure_mode=filedata['exposure_mode'],
                        awb_mode=filedata['awb_mode'],
                        encoding_mode=filedata['encoding_mode'],
                        resolution=filedata['resolution'],
                        ISO=filedata['ISO'],
                        #exposure_time=filedata['exposure_time'],
                        date=filedata['date'],
                        timestamp='test',
                        filesize=filedata['filesize'])
        DBSession.add(picture)
        #TODO: remove feature of local copy
        #if bisque_enabled == "Yes" and bisque_local_copy == "No":
        #    print 'Deleting local copy of \'' + filename + '\''
        #    os.remove(RASPISTILL_DIRECTORY + filename)
        
        if (not ret):
            return HTTPFound(location='/')
        else:
            return filename;
                

# View for the archive delete - no site will be generated
@view_config(route_name='delete_picture')
def pic_delete_view(request):    
    p_id = request.params['id']
    pic = DBSession.query(Picture).filter_by(id=int(p_id)).first()
    print('Deleting picture and thumbnail...')
    
    app_settings = DBSession.query(Settings).first()
    
    delete_gdrive = app_settings.gdrive_enabled.lower() == app_settings.gdrive_delete_files.lower() == 'yes'
    
    if os.path.isfile(RASPISTILL_DIRECTORY + pic.filename):
        lst = glob(RASPISTILL_DIRECTORY + pic.filename.replace('.png','.*.png'));
        lst.append(RASPISTILL_DIRECTORY + pic.filename)
        
        for l in lst:
            if (delete_gdrive):
                try:
                    G.delete_file(app_settings.gdrive_folder,l)    
                except:
                    pass
                    
            os.remove(l)
    
    if os.path.isfile(THUMBNAIL_DIRECTORY + pic.filename):
        os.remove(THUMBNAIL_DIRECTORY + pic.filename)
        
    DBSession.delete(pic)
    return HTTPFound(location='/archive')

# View for the timelapse delete - no site will be generated
@view_config(route_name='delete_timelapse')
def tl_delete_view(request):
    tt_id = request.params['id']
    tl = DBSession.query(Timelapse).filter_by(id=int(t_id)).first()
    print 'Deleting time-lapse directory and archive...'
    try:
        shutil.rmtree(TIMELAPSE_DIRECTORY + tl.filename)
    except:
        print "Folder "+tl.filename+" not found"
    
    try:    
        os.remove(TIMELAPSE_DIRECTORY + tl.filename + '.zip')
    except:
        print "File "+tl.filename + ".zip not found"
        
    #os.remove(TIMELAPSE_DIRECTORY + timelapse_database[int(request.params['id'])]['filename'] + '.tar.gz')
    #shutil.rmtree(TIMELAPSE_DIRECTORY + timelapse_database[int(request.params['id'])]['filename'])
    DBSession.delete(tl)
    return HTTPFound(location='/timelapse')

# View for settings form data - no site will be generated      
@view_config(route_name='save')
def save_view(request):
    global preferences_success_alert, preferences_fail_alert
    trigger_reboot=False

    image_width_temp = request.params['imageWidth']
    image_height_temp = request.params['imageHeight']
    timelapse_interval_temp = request.params['timelapseInterval']
    timelapse_time_temp = request.params['timelapseTime']
    exposure_mode_temp = request.params['exposureMode']
    image_effect_temp = request.params['imageEffect']
    awb_mode_temp = request.params['awbMode']
    image_ISO_temp = request.params['isoOption']
    image_rotation_temp = request.params['imageRotation']
    image_resolution = request.params['imageResolution']
    encoding_mode_temp = request.params['encodingMode']
    bisque_enabled_temp = request.params['bisqueEnabled']
    bisque_user_temp = request.params['bisqueUser']
    bisque_pswd_temp = request.params['bisquePswd']
    bisque_root_url_temp = request.params['bisqueRootUrl']
    bisque_local_copy_temp = request.params['bisqueLocalCopy']
    gdrive_enabled_temp = request.params['gdriveEnabled']
    gdrive_folder_temp = request.params['gdriveFolder']
    gdrive_user_temp = request.params['gdriveUser']
    gdrive_secret_temp = request.params['gdriveSecret']
    gdrive_delete_files_temp = request.params['gdriveDelete']
    number_shots_temp = request.params['numberImages']
    command_before_sequence_temp = request.params['commandBeforeAcquisition']
    command_after_sequence_temp = request.params['commandAfterAcquisition']
    command_before_shot_temp = request.params['commandBeforeShot']
    command_after_shot_temp = request.params['commandAfterShot']
    multisensors_enabled_temp = request.params['multisensorEnabled']
    multisensor_download_asynch = request.params['asyncDownload']
    hdr_enabled = request.params['hdrEnabled']
    hdr_exposure_times = request.params['exposureTimes']
    sensors_name = request.params['sensors_name'] if request.params['sensors_name'] !='None' else ''


    app_settings = DBSession.query(Settings).first()
    
    if image_width_temp:
        if 0 < int(image_width_temp) < 2592:
            app_settings.image_width = image_width_temp
        else:
            preferences_fail_alert.append(IMAGE_WIDTH_ALERT)
    
    if image_height_temp:
        if 0 < int(image_height_temp) < 1945:
            app_settings.image_height = image_height_temp
        else:
            preferences_fail_alert.append(IMAGE_HEIGHT_ALERT)
            
    if not image_width_temp and not image_height_temp:
        app_settings.image_width = image_resolution.split('x')[0]
        app_settings.image_height = image_resolution.split('x')[1]
        
    if number_shots_temp:
        app_settings.number_images = int(number_shots_temp)
    
    #if command_before_sequence_temp:
    app_settings.command_before_sequence = command_before_sequence_temp
        
    #if command_after_sequence_temp:
    app_settings.command_after_sequence = command_after_sequence_temp
        
    #if command_before_shot_temp:
    app_settings.command_before_shot = command_before_shot_temp
        
    #if command_after_shot_temp:
    app_settings.command_after_shot = command_after_shot_temp
            
    if timelapse_interval_temp:
        app_settings.timelapse_interval = int(timelapse_interval_temp)
        
    if timelapse_time_temp:
        app_settings.timelapse_time = int(timelapse_time_temp)
    
    if exposure_mode_temp and exposure_mode_temp in EXPOSURE_MODES:
        app_settings.exposure_mode = exposure_mode_temp
    else:
        preferences_fail_alert.append(EXPOSURE_MODE_ALERT)
        
    if image_effect_temp and image_effect_temp in IMAGE_EFFECTS:
        app_settings.image_effect = image_effect_temp
    else:
        preferences_fail_alert.append(IMAGE_EFFECT_ALERT)
        
    if awb_mode_temp and awb_mode_temp in AWB_MODES:
        app_settings.awb_mode = awb_mode_temp
    else:
        preferences_fail_alert.append(AWB_MODE_ALERT)
        
    if image_ISO_temp and image_ISO_temp in ISO_OPTIONS:
        app_settings.image_ISO = image_ISO_temp
    else:
        preferences_fail_alert.append(ISO_OPTION_ALERT)
        
    if image_rotation_temp and image_rotation_temp in ['0','90','180','270']:
        app_settings.image_rotation = image_rotation_temp
    else:
        preferences_fail_alert.append(IMAGE_ROTATION_ALERT)  
    
    if encoding_mode_temp and encoding_mode_temp in ENCODING_MODES:
        app_settings.encoding_mode = encoding_mode_temp
    else:
        preferences_fail_alert.append(ENCODING_MODE_ALERT)
    
    if bisque_enabled_temp:
        app_settings.bisque_enabled = bisque_enabled_temp
        if app_settings.bisque_enabled == "Yes":
            if bisque_user_temp:
                app_settings.bisque_user = bisque_user_temp
            else:
                preferences_fail_alert.append(BISQUE_USER_ALERT)
            if bisque_pswd_temp:
                app_settings.bisque_pswd = bisque_pswd_temp
            else:
                preferences_fail_alert.append(BISQUE_PSWD_ALERT)
            if bisque_root_url_temp:
                app_settings.bisque_root_url = bisque_root_url_temp
            else:
                preferences_fail_alert.append(BISQUE_ROOT_URL_ALERT)
        if bisque_local_copy_temp and bisque_local_copy_temp in ['Yes','No']:
            app_settings.bisque_local_copy = bisque_local_copy_temp

    if gdrive_enabled_temp:
        app_settings.gdrive_enabled = gdrive_enabled_temp
        gmail_enabled = app_settings.gdrive_enabled == "Yes"
        
        
        if gdrive_folder_temp:
            app_settings.gdrive_folder = gdrive_folder_temp
        elif gmail_enabled:
            preferences_fail_alert.append(GDRIVE_FOLDER_ALERT)
            
        if gdrive_user_temp:
            app_settings.gdrive_user = gdrive_user_temp
        elif gmail_enabled:
            preferences_fail_alert.append(GDRIVE_USER_ALERT)
        
        if gdrive_secret_temp:
            app_settings.gdrive_secret = gdrive_secret_temp
        elif gmail_enabled:
            preferences_fail_alert.append(GDRIVE_SECRET_ALERT)
                
        if gmail_enabled:
            try:
                G.gdrive_init(app_settings.gdrive_folder,gdrive_user_temp,gdrive_secret_temp,RASPISTILL_ROOT+'/settings.template.yaml')
            except ServerNotFoundError:
                preferences_fail_alert.append('Unable to authenticate G-Drive account. Check your internet connection')
    
    app_settings.gdrive_delete_files = gdrive_delete_files_temp
    
    app_settings.hdr_enabled = hdr_enabled
    app_settings.hdr_exposure_times = hdr_exposure_times
    
    
    if multisensors_enabled_temp:
        app_settings.multisensor_enabled = multisensors_enabled_temp
        
    if ( (multisensor_download_asynch=='Yes') and (app_settings.multisensor_download_asynch!=multisensor_download_asynch)):
        trigger_reboot=True
    
    app_settings.multisensor_download_asynch = multisensor_download_asynch
        
    app_settings.sensors_name = sensors_name
                
    if preferences_fail_alert == []:
        preferences_success_alert = True 
    
    DBSession.flush()      

    
    return HTTPFound(location='/settings')  

@view_config(route_name='upload_gdrive')
def upload_gdrive_view(request):
    tt_id = request.params['id']
    picture = DBSession.query(Picture).filter_by(id=int(tt_id)).first()
    imagedata = get_picture_data(picture)
    
    app_settings = DBSession.query(Settings).first()
    
    for client in imagedata['slaves']:
        if client['gdrive'].lower() == 'no':
            fullpath = os.path.join(RASPISTILL_DIRECTORY,client['filename'])
            G.upload_file(fullpath,MIME_TYPES[app_settings.encoding_mode],app_settings)
            
    print request
    return HTTPFound(location='/') 
    

@view_config(route_name='camera_calibr_do_pic')
def camera_calibr_do_pic(request):
    app_settings = DBSession.query(Settings).first()
    
    if not os.path.isdir(CAMERA_CALIBR_DIRECTORY):
        os.mkdir(CAMERA_CALIBR_DIRECTORY)
    
    
    if (not request.params['device']):
        fname = 'calibr_master_{id}.'.format(id=request.params['count']) + app_settings.encoding_mode
        filename = os.path.join(CAMERA_CALIBR_DIRECTORY,fname)
        raspistill_command = raspistill_commandline(None,app_settings)
        raspistill_command[0]+=' -o '+filename
        
        call (raspistill_command,stdout=PIPE, shell=True)
    else:
        ip = request.params['device']
        fname = 'calibr_'+ip+'_{id}.'.format(id=request.params['count']) + app_settings.encoding_mode
        raspistill_command = raspistill_commandline(None,app_settings)[0]
        
        ips,macs = ms.get_clients()
        
        idx = ips.index(ip)
        
        fname = os.path.join(CAMERA_CALIBR_DIRECTORY,fname)
        
        ms.get_picture_from_using_ssh([(ip,macs[idx])],raspistill_command,fname,False)
        
    response = Response()
    
    return response

def get_calibration_patterns():
    lst = glob(os.path.join(CAMERA_CALIBR_DIRECTORY,'calibr*.*'));
    data = {}
    
    if (lst != []):
        for f in lst:
            path,fname = os.path.split(f)
            _,client,_ = fname.split('_')
            
            
            
            client = client.replace('-','.')

            if (client not in data.keys()):
                data[client] = []
                
            data[client].append(f)
                
        data[client].sort()
        
    return data
    


@view_config(route_name="camera_calibrated_action",renderer='view_parameters.mako')
def camera_calibration_params_actions(request):
    action = request.params['action']
    pid = int(request.params['id'])
    
    camera_params = DBSession.query(CameraParams).filter_by(id=int(pid)).first()
    
    if (action=='delete'):
        DBSession.delete(camera_params)
        
        
        return HTTPFound(location='/camera_calibr') 
    elif(action=='view'):
        import pickle
        
        params = pickle.loads(camera_params.params)
        
        
        return {
            'project': 'raspistillWeb',
            'device': camera_params.device,
            'timestamp': camera_params.timestamp,
            'mtx' : params['matrix'],
            'dist' : params['dist'],
            'rvecs' : params['rvecs'],
            'tvecs' : params['tvecs'] 
        }
    elif (action=="apply"):
        import cv2
        import pickle
        
        params = pickle.loads(camera_params.params)
        
        filename = request.params['pic_filename']
        
        I = cv2.imread(os.path.join( RASPISTILL_DIRECTORY,filename));
        I = cv2.resize(I, CALIBR_DEF_RESIZE )
        
        h,w = I.shape[:2]
        
        newcameramtx,roi = cv2.getOptimalNewCameraMatrix(params['matrix'],params['dist'], (w,h), 1, (w,h))
        
        mapx,mapy = cv2.initUndistortRectifyMap(params['matrix'],params['dist'],None,newcameramtx,(w,h),5)
        
        dst = cv2.remap(I,mapx,mapy,cv2.INTER_LINEAR)
        
        dst_fname = os.path.join('/tmp',filename)
        cv2.imwrite(dst_fname, dst)
        
        r = FileResponse(dst_fname)
        return r
        #r.headers.add('Content-disposition','attachment; filename="'+str(filename)+'"')
        

@view_config(route_name="camera_calibr_do_calibr",renderer='camera_calibr.mako')
def do_camera_calibration(request):
    import cv2
    import numpy as np
    import pickle
    
    app_settings = DBSession.query(Settings).first()
    
    action = request.params['action']
    client = request.params['client']
    
    h = int(request.params['checkerHoriz'])
    v = int(request.params['checkerVert'])
    
    checkerboardPattern = (v,h)
    
    patterns = get_calibration_patterns()
    
    alerts = []
    slaves = []
    
    checkerboard_detected = {}
    
    if (app_settings.multisensor_enabled.lower() == 'yes'):
        clients = ms.get_registered_clients(app_settings.sensors_name)
        
        
        for k in clients:
            slaves.append({'ip':k,'name':clients[k]})

    if (action=='detect'):
        
        img = patterns[client]
        
        
        
        for i in range(len(img)):
            f = img[i]
                        
            I = cv2.imread(f)
            I = cv2.resize(I,CALIBR_DEF_RESIZE)
            gs = cv2.cvtColor(I,cv2.COLOR_BGR2GRAY)
            ret,_ = cv2.findChessboardCorners(gs,checkerboardPattern)
            
            checkerboard_detected[f] = ret  

    elif (action=='calibr'):
        
        img = patterns[client]
        
        image_points = []
        
        for i in range(len(img)):
            f = img[i]
                        
            I = cv2.imread(f)
            I = cv2.resize(I,CALIBR_DEF_RESIZE)
            gs = cv2.cvtColor(I,cv2.COLOR_BGR2GRAY)
            ret,corners = cv2.findChessboardCorners(gs,checkerboardPattern)
            
            if (ret):
                cv2.cornerSubPix(gs,corners,(3,3),(-1,-1), (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,30,0.001) )
                image_points.append(corners)
                
        objp = np.zeros((checkerboardPattern[0]*checkerboardPattern[1],3),np.float32)
        objp[:,:2] = np.mgrid[0:checkerboardPattern[0],0:checkerboardPattern[1]].T.reshape(-1,2)
        real_points = [objp]*len(image_points)
        
        try:
            
            _,mtx,dist,rvecs,tvecs = cv2.calibrateCamera(real_points,image_points,gs.shape[::-1],None,None)
            camera_calibr_data = {'matrix':mtx,'dist':dist,'rvecs':rvecs,'tvecs':tvecs}
            
            params = CameraParams(device=client,timestamp=strftime(TIMESTAMP, localtime()),params=pickle.dumps(camera_calibr_data))
            DBSession.add(params)
        except _ as exp:
            print exp
            alerts.append('An error occured during the camera calibration process')
        
    elif (action=='delete'):
        
        for f in patterns[client]:
            os.remove(f)
        
        del patterns[client]
        
    parameters = DBSession.query(CameraParams).all()
    
    return {
        'project': 'raspistillWeb',
        'slaves':slaves,
        'number_images': CALIBR_DEF_NUMBER_IMAGES,
        'interval' : CALIBR_DEF_INTERVAL,
        'checker_horizontal' : CALIBR_DEF_CHECKER_HORIZONTAL,
        'checker_vertical' : CALIBR_DEF_CHECKER_VERTICAL,
        'preferences_fail_alert': alerts,
        'calibration_images': patterns,
        'detected_checkerboards' : checkerboard_detected,
        'parameters': parameters,
        'pic_filenames': get_picture_quicklist()
        
    }    

def get_picture_quicklist():
    pictures = DBSession.query(Picture).all()
    
    filenames={'Master':[]}
    
    for pic in pictures:
        imagedata = get_picture_data(pic,None)
        slaves = imagedata['slaves']
        
        for slave in slaves:
            k=slave['sensor_name']
            if (k in filenames.keys()):
                filenames[k].append(slave['filename'])
            else:
                filenames[k] = [slave['filename']]
                
    return filenames        
   
@view_config(route_name='camera_calibr',renderer='camera_calibr.mako')
def camera_calibr(request):
    app_settings = DBSession.query(Settings).first()
    slaves = []
    alerts = []
    
    try:
        import cv2
    except:
        alerts.append('OpenCV2 not installed. Calibration cannot be performed. Please <a href="https://www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/" target="_blank">read this guide</a> on how to do it')
        
    
    if (app_settings.multisensor_enabled.lower() == 'yes'):
        clients = ms.get_registered_clients(app_settings.sensors_name)
        
        
        for k in clients:
            slaves.append({'ip':k,'name':clients[k]})
            
    calibration_images = get_calibration_patterns()
    
    parameters = DBSession.query(CameraParams).all()
       
    return {
        'project': 'raspistillWeb',
        'slaves':slaves,
        'number_images': CALIBR_DEF_NUMBER_IMAGES,
        'interval' : CALIBR_DEF_INTERVAL,
        'checker_horizontal' : CALIBR_DEF_CHECKER_HORIZONTAL,
        'checker_vertical' : CALIBR_DEF_CHECKER_VERTICAL,
        'preferences_fail_alert': alerts,
        'calibration_images': calibration_images,
        'parameters': parameters,
        'pic_filenames': get_picture_quicklist()
    }
    

# View for the reboot
@view_config(route_name='reboot', renderer='shutdown.mako')
def reboot_view(request):
    host_name = gethostname()
    
    app_settings = DBSession.query(Settings).first()
    if (app_settings.multisensor_enabled == "Yes"):
        ips,macs = ms.get_clients()
        hosts = zip(ips,macs)
        ms.reboot_clients(hosts)
        
    os.system("sudo shutdown -r now")
    return {'project': 'raspistillWeb',
            'hostName' : host_name,
            }

# View for the shutdown
@view_config(route_name='shutdown', renderer='shutdown.mako')
def shutdown_view(request):
    host_name = gethostname()
    
    app_settings = DBSession.query(Settings).first()
    if (app_settings.multisensor_enabled == "Yes"):
        ips,macs = ms.get_clients()
        hosts = zip(ips,macs)
        ms.shutdown_clients(hosts)
    
    os.system("sudo shutdown -hP now")
    return {'project': 'raspistillWeb',
            'hostName' : host_name,
            }
            
@view_config(route_name='external_photo')
def external_photo_view(request):
    filename = photo_view(request,True)
    r = FileResponse(RASPISTILL_DIRECTORY+filename)
    r.headers.add('Content-disposition','attachment; filename="'+str(filename)+'"')
    return r


###############################################################################
############ Helper functions to keep the code clean ##########################
###############################################################################

def raspistill_commandline(filename=None,exp=None,awb=None,iso=None,shutter_speed=0,app_settings=None):
    if (app_settings is None):
        app_settings = DBSession.query(Settings).first()
        
    awb_call = app_settings.awb_mode if awb is None else awb
    exp_call = app_settings.exposure_mode if exp is None else exp
    
    if iso is None:
        if app_settings.image_ISO == 'auto':
            iso_call = ''
        else:
            iso_call = ' -ISO ' + str(app_settings.image_ISO)
    else:
        iso_call = ' -ISO '+ str(iso)
        
    shutter_speed_call = ''
    
    if (shutter_speed is not None) and (shutter_speed > 0):
		shutter_speed_call = ' -ss '+ str(shutter_speed)

        
    if (filename is None):
        out = ''
    else:
        out = ' -o ' + RASPISTILL_DIRECTORY + filename
        
    command = ['raspistill -t 500'
                + ' -n '
                + ' -w ' + str(app_settings.image_width)
                + ' -h ' + str(app_settings.image_height)
                + ' -e ' + app_settings.encoding_mode
                + ' -ex ' + exp_call
                + ' -awb ' + awb_call
                + ' -rot ' + str(app_settings.image_rotation)
                + ' -ifx ' + app_settings.image_effect
                + iso_call
                + shutter_speed_call
                + out ]
        
    return command
    
 
def perform_hdr(filename):
	import cv2
	import numpy as np
	
	fname,ext = os.path.splitext(filename)
	lst = glob(os.path.join(RASPISTILL_DIRECTORY,fname+"*"))
	
	files = {}
	
	for f in lst:
		m = re.search("IMG_(.+)\.([0-9a-fA-F]{4})\.(.*)",f)
		key = 'master' if m is None else m.group(2)
		
		#finding exposure on name
		
		m = re.search("IMG_(.+)\.SS\=1f([0-9]+)\.(.*)",f)
		
		if (m is not None):
			exposure_speed = m.group(2)
			if (key not in files.keys()):
				files[key]={exposure_speed:f}
			else:
				files[key][exposure_speed] = f
				
	
	for device in files.keys():
		exposures = files[device]
		times = np.array([ 1./float(t) for t in exposures.keys() ],dtype=np.float32)
		imgs = [cv2.imread(os.path.join(exposures[f])) for f in exposures]
		
		calibration = cv2.createCalibrateDebevec()
		responseDebevec = calibration.process(imgs,times)
		
		mergeDebevec = cv2.createMergeDebevec()
		hdrDebevec = mergeDebevec.process(imgs,times,responseDebevec)
		
		dragoTonemap = cv2.createTonemapDrago(1.0,0.7)
		ldrDrago = dragoTonemap.process(hdrDebevec)
		ldrDrago = 3 * ldrDrago
		
		if (device == 'master'):
			save_as = fname + ext
		else:
			save_as = fname + '.'+device + ext
		
		cv2.imwrite( os.path.join(RASPISTILL_DIRECTORY,save_as) ,ldrDrago*255)
		
		for f in lst:
			os.remove(os.path.join(f))
		

def take_photo(picture_name,bypassUploads=False):
    app_settings = DBSession.query(Settings).first()

    # ----- TEST CODE -----#
    #print PiCamera.AWB_MODES
    #with picamera.PiCamera() as camera:
    #    camera.resolution = (app_settings.image_width,app_settings.image_height)
    #    # Camera warm-up time
    #    time.sleep(2)
    #    camera.shutter_speed = camera.exposure_speed
    #    camera.exposure_mode = app_settings.exposure_mode
    #    camera.awb_mode = app_settings.awb_mode
    #    camera.image_rotation = app_settings.image_rotation
    #    camera.image_effect = app_settings.image_effect
    #    camera.iso = 0 if app_settings.image_ISO == 'auto' else app_settings.image_ISO
    #    camera.capture(RASPISTILL_DIRECTORY + filename + '_test', format=app_settings.encoding_mode)
    # ----- TEST CODE -----#

    hdr_speeds = [0]
    hdr = False

    if (app_settings.hdr_enabled.lower() == 'yes'):
	    hdr_speeds = app_settings.hdr_exposure_times.split(';')
	    hdr = True

    for speed in hdr_speeds:
		
		if (speed>0):
			[name,ext] = os.path.splitext(picture_name)
			filename = name + ".SS=1f{}".format(speed) +ext
			
			speed = long(round(1/float(speed) * 1000000))
		else:
		    filename = picture_name
    
		raspistill_command = raspistill_commandline(filename,shutter_speed=speed,app_settings=app_settings)
		raspistill_command_no_out = raspistill_commandline(None,shutter_speed=speed,app_settings=app_settings)
		
		r = app_settings.command_before_sequence
		r = r.replace('$f',filename)
		r = r.replace('$c',raspistill_command_no_out[0])
		run_shell_command(r)


		print raspistill_command
		
		
		threads = []

		if (app_settings.multisensor_enabled == "Yes"):
			fullpath = os.path.join(RASPISTILL_DIRECTORY,filename)   
			
			download = True if app_settings.multisensor_download_asynch.lower() =='no' else False 
			
			clients_conf = app_settings.sensors_name
			clients = ms.get_registered_clients(clients_conf,ip_keys=False)
			clients_params = ms.get_clients_parameters(clients_conf)
			
			if (len(clients)>0):
				commands = {}
				for mac in clients.keys():
					params = clients_params[mac] if mac in clients_params else {}
					c = raspistill_commandline(None,shutter_speed=speed,app_settings=app_settings,**params)
					commands[mac] = c[0]
					
				threads = ms.trigger_pictures_from_clients(commands,fullpath,download=download,join=False)
		
		call (raspistill_command,stdout=PIPE, shell=True)

		for t in threads:
			t.join()
			
		r = app_settings.command_after_sequence
		r = r.replace('$f',filename)
		r = r.replace('$c',raspistill_command_no_out[0])
		run_shell_command(r)
		
    if (hdr):
        perform_hdr(picture_name)
    

    if (app_settings.bisque_enabled == 'Yes') and not bypassUploads:
        resource = etree.Element('image', name=filename)
        etree.SubElement(resource, 'tag', name="experiment", value="Phenotiki")
        etree.SubElement(resource, 'tag', name="timestamp", value=os.path.splitext(filename)[0])
        bqsession = setbasicauth(bisque_root_url, bisque_user, bisque_pswd)
        print 'Uploading \'' + filename + '\' to Bisque...'
        start_time = time()
        r = save_blob(bqsession, localfile=RASPISTILL_DIRECTORY+filename, resource=resource)
        elapsed_time = time() - start_time
        if r is None:
            print 'Error uploading!'
            preferences_fail_alert.append('Error uploading \'' + filename + '\' to Bisque!')
        else:
            print 'Image uploaded in %.2f seconds' % elapsed_time
            print r.items()
            print 'Image URI:', r.get('uri')

    if (app_settings.gdrive_enabled == 'Yes') and not bypassUploads:
        print ">>>> GDrive Upload <<<<"
        lst = get_clients_file_list(RASPISTILL_DIRECTORY + filename,app_settings.encoding_mode);
        lst.append(RASPISTILL_DIRECTORY + filename)
        
        for p in lst:
            try:
                G.upload_file(p,MIME_TYPES[app_settings.encoding_mode],app_settings)
            except ResponseNotReady:
                pass
            except ServerNotFoundError:
                pass
        

    return

def take_timelapse(filename):
    global timelapse, timelapse_database, p_timelapse

    app_settings = DBSession.query(Settings).first()
    timelapsedata = {'filename' :  filename}
    timelapsedata['timeStart'] = str(asctime(localtime()))
    os.makedirs(TIMELAPSE_DIRECTORY + filename)
    timelapse_interval_ms = app_settings.timelapse_interval*1000
    timelapse_time_ms = app_settings.timelapse_time*1000
    if app_settings.image_ISO == 'auto':
        iso_call = ''
    else:
        iso_call = ' -ISO ' + str(app_settings.image_ISO)
    
    # ----- TEST CODE -----#
    #with picamera.PiCamera() as camera:
    #    camera.resolution = (app_settings.image_width,app_settings.image_height)
    #    # Camera warm-up time
    #    time.sleep(2)
    #    camera.shutter_speed = camera.exposure_speed
    #    camera.exposure_mode = app_settings.exposure_mode
    #    camera.awb_mode = app_settings.awb_mode
    #    camera.image_rotation = app_settings.image_rotation
    #    camera.image_effect = app_settings.image_effect
    #    camera.iso = 0 if app_settings.image_ISO == 'auto' else app_settings.image_ISO
    #    for filename in camera.capture_continuous(TIMELAPSE_DIRECTORY + filename + '/' + 'IMG_{timestamp:%Y-%m-%d_%H-%M-%S}.' + app_settings.encoding_mode, format=app_settings.encoding_mode):
    #        print('Captured %s' % filename)
    #        time.sleep(app_settings.timelapse_interval)
    #    #camera.capture(RASPISTILL_DIRECTORY + filename + '_test', format=app_settings.encoding_mode)
    # ----- TEST CODE -----#
    
    try:
        print 'Starting time-lapse acquisition...'
        #TODO: rename images with timestamp
        #run_shell_command(app_settings.command_before_sequence)
        p_timelapse = Popen(
            ['raspistill '
            + ' -n '
            + ' -w ' + str(app_settings.image_width)
            + ' -h ' + str(app_settings.image_height)
            + ' -e ' + app_settings.encoding_mode
            + ' -ex ' + app_settings.exposure_mode
            + ' -awb ' + app_settings.awb_mode
            + ' -rot ' + str(app_settings.image_rotation)
            + ' -ifx ' + app_settings.image_effect
            + iso_call
            + ' -t ' + str(timelapse_time_ms) 
            + ' -tl ' + str(timelapse_interval_ms)
            + ' -o ' + TIMELAPSE_DIRECTORY + filename + '/'
            + 'IMG_' + filename + '_%04d.' + app_settings.encoding_mode],
            stdout=PIPE, shell=True, preexec_fn=os.setsid
            )
        p_timelapse.wait()
        #run_shell_command(app_settings.command_after_sequence)
        print 'Finished time-lapse acquisition.'
    except:
        #p_timelapse.kill()
        os.killpg(p_timelapse.pid, signal.SIGTERM)
        p_timelapse.wait()
        raise
    timelapsedata['n_images'] = str(len([name for name in os.listdir(TIMELAPSE_DIRECTORY + filename) if os.path.isfile(os.path.join(TIMELAPSE_DIRECTORY + filename, name))]))
    timelapsedata['resolution'] = str(app_settings.image_width) + ' x ' + str(app_settings.image_height)
    timelapsedata['image_effect'] = app_settings.image_effect
    timelapsedata['exposure_mode'] = app_settings.exposure_mode
    timelapsedata['encoding_mode'] = app_settings.encoding_mode
    timelapsedata['awb_mode'] = app_settings.awb_mode
    timelapsedata['timeEnd'] = str(asctime(localtime()))

    timelapse_data = Timelapse(
                        filename = timelapsedata['filename'],
                        timeStart = timelapsedata['timeStart'],
                        n_images = timelapsedata['n_images'],
                        resolution = timelapsedata['resolution'],
                        image_effect = timelapsedata['image_effect'],
                        exposure_mode = timelapsedata['exposure_mode'],
                        encoding_mode = timelapsedata['encoding_mode'],
                        awb_mode = timelapsedata['awb_mode'],
                        timeEnd = timelapsedata['timeEnd'],
                    )

    print('Adding timelapse to DB')
    DBSession.add(timelapse_data)
    #DBSession.flush() 
    transaction.commit()
    print('Added timelapse to DB')
    #TODO: create zip instead of tar.gz
    #with tarfile.open(TIMELAPSE_DIRECTORY + filename + '.tar.gz', "w:gz") as tar:
    #    tar.add(TIMELAPSE_DIRECTORY + filename, arcname=os.path.basename(TIMELAPSE_DIRECTORY + filename))
    path = TIMELAPSE_DIRECTORY + filename
    print 'Creating ZIP of ' + path
    with zipfile.ZipFile(path + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for _, _, files in os.walk(path):
            for file in files:
                print file
                zipf.write(os.path.join(path,file), arcname=os.path.join(filename,file))
    print 'done'
    #timelapse_database = timelapse_data
    timelapse = False
    
    return 

#def generate_thumbnail(filename):
#    call (
#        ['exif -e ' + RASPISTILL_DIRECTORY + filename
#        + ' -o ' + THUMBNAIL_DIRECTORY + filename], shell=True
#    )
#    if not (THUMBNAIL_DIRECTORY == 'raspistillweb/thumbnails/'):
#        call (
#            ['ln -s ' + THUMBNAIL_DIRECTORY + filename 
#            + ' raspistillweb/thumbnails/' + filename], shell=True
#            )
#    return

#def extract_exif(tags):
#    return {
#        'resolution' : str(tags['Image ImageWidth']) 
#        + ' x ' + str(tags['Image ImageLength']),
#        'ISO' : str(tags['EXIF ISOSpeedRatings']),
#        'exposure_time' : str(tags['EXIF ExposureTime'])
#            }

def extract_filedata(st):
    return {
        'date' : str(asctime(localtime(st[ST_MTIME]))),
        'timestamp' : localtime(),
        'filesize': str((st[ST_SIZE])/1000) + ' kB'
            }

def setbasicauth(bisquehost, username, password):
    bqsession = BQSession()
    bqsession.init_cas(username, password, bisque_root=bisquehost, create_mex=False)
    r = bqsession.c.post(bisquehost + "/auth_service/setbasicauth", data = { 'username': username, 'passwd': password})
    print r
    return bqsession
    
    
def get_clients_file_list(filename,encoding_mode):
     return glob(filename.replace('.'+encoding_mode,'.*.'+encoding_mode));

def get_picture_data(picture,file_list=[]):
    app_settings = DBSession.query(Settings).first()
    
    if ( (file_list is not None) and (len(file_list)==0)):
        if (app_settings.gdrive_enabled == 'Yes'):
            try:
                file_list = G.get_all_uploaded_images(app_settings.gdrive_folder)
                file_list = [f['title'] for f in file_list]
            except ServerNotFoundError:
                file_list=None
        
    imagedata = dict()
    imagedata['id'] = str(picture.id)
    imagedata['filename'] = picture.filename
    imagedata['image_effect'] = picture.image_effect
    imagedata['exposure_mode'] = picture.exposure_mode
    imagedata['encoding_mode'] = picture.encoding_mode
    imagedata['awb_mode'] = picture.awb_mode
    imagedata['resolution'] = picture.resolution
    imagedata['ISO'] = str(picture.ISO)
    #imagedata['exposure_time'] = picture.exposure_time
    imagedata['date'] = str(picture.date)
    imagedata['timestamp'] = str(picture.timestamp)
    imagedata['filesize'] = str(picture.filesize)
    

    imagedata['slaves'] = None
    
    lst = get_clients_file_list(RASPISTILL_DIRECTORY + picture.filename,imagedata['encoding_mode']);
    slaves = []
    
    for l in lst:
        a = l.find('.')
        b = l.rfind('.');
        slaves.append(l[a+1:b])
        

    imagedata['slaves'] = [{'filename':picture.filename,'sensor_name':'Master','gdrive':None}] + [{'filename':picture.filename.replace('.'+picture.encoding_mode,'.'+s+'.'+picture.encoding_mode),'sensor_name':ms.map_client_name(s,app_settings.sensors_name),'gdrive':None} for s in slaves]
    
    show_upload_button = False
    
    if (app_settings.gdrive_enabled == 'Yes'):
        
        for j in range(len(imagedata['slaves'])):
            title,_ = os.path.splitext(imagedata['slaves'][j]['filename'])
            if (file_list is not None):
                imagedata['slaves'][j]['gdrive'] = 'Yes' if title in file_list else 'No'
            else:
                imagedata['slaves'][j]['gdrive'] = 'Unk' #unknown due to internet connect
            
            if (imagedata['slaves'][j]['gdrive'] == 'No'):
                show_upload_button = True
    
    imagedata['gdrive_upload'] = show_upload_button
        
    return imagedata

def run_shell_command(command=""):
    if command:
        p_command = Popen(command,shell=True,stdout=PIPE)
        p_command.wait()
        print p_command.stdout.read()
        print "Command executed with exit code %d" % p_command.returncode

def get_timelapse_data(timelapse_rec):
    timelapse_data = dict()
    timelapse_data['id'] = str(timelapse_rec.id)
    timelapse_data['filename'] = timelapse_rec.filename
    timelapse_data['image_effect'] = timelapse_rec.image_effect
    timelapse_data['exposure_mode'] = timelapse_rec.exposure_mode
    timelapse_data['awb_mode'] = timelapse_rec.awb_mode
    timelapse_data['timeStart'] = str(timelapse_rec.timeStart)
    timelapse_data['timeEnd'] = str(timelapse_rec.timeEnd)
    timelapse_data['n_images'] = str(timelapse_rec.n_images)
    timelapse_data['resolution'] = timelapse_rec.resolution
    timelapse_data['encoding_mode'] = timelapse_rec.encoding_mode
    return timelapse_data
