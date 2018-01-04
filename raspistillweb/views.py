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
#import exifread
import os
import os.path
import shutil
import signal
import threading
import tarfile
import zipfile
from subprocess import call, Popen, PIPE 
from time import gmtime, strftime, localtime, asctime, mktime, sleep
from stat import *
from datetime import *

#import Image
from PIL import Image
##from bqapi.bqclass import fromXml
#import bqapi as zzz
from bqapi.comm import BQSession#, BQCommError
from bqapi.util import save_blob
from lxml import etree
from time import time
from socket import gethostname
import picamera

from sqlalchemy.exc import DBAPIError
import transaction
from .models import (
    DBSession,
    Picture,
    Settings,
    Timelapse,
    )


# Modify these lines to change the directory where the pictures and thumbnails
# are stored. Make sure that the directories exist and the user who runs this
# program has write access to the directories. 
RASPISTILL_DIRECTORY = 'raspistillweb/pictures/' # Example: /home/pi/pics/
THUMBNAIL_DIRECTORY = 'raspistillweb/thumbnails/' # Example: /home/pi/thumbs/
TIMELAPSE_DIRECTORY = 'raspistillweb/time-lapse/' # Example: /home/pi/timelapse/

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

#THUMBNAIL_SIZE = '240:160:80'
THUMBNAIL_SIZE = 240, 160
THUMBNAIL_JPEG_QUALITY = 80

timelapse = False
timelapse_database = None
p_timelapse = None
percentage_completed = 0
starttime = 0

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
            'preferences_fail_alert' : preferences_fail_alert_temp,
            'preferences_success_alert' : preferences_success_alert_temp
            } 

# View for the /archive site
@view_config(route_name='archive', renderer='archive.mako')
def archive_view(request):

    pictures = DBSession.query(Picture).all()
    picturedb = []
    for picture in pictures:
        imagedata = get_picture_data(picture)
        picturedb.insert(0,imagedata)
    return {'project' : 'raspistillWeb',
            'database' : picturedb
            }

# View for the / site
@view_config(route_name='home', renderer='home.mako')
def home_view(request):
    pictures = DBSession.query(Picture).all()
    if len(pictures) == 0:
        return HTTPFound(location='/photo')
    else:
        picture_data = get_picture_data(pictures[-1])
        if timelapse:            
            return {'project': 'raspistillWeb',
                    'imagedata' : picture_data,
                    'timelapse' : timelapse,
                    }
        #elif (mktime(localtime()) - mktime(picture_data['timestamp'])) > 1800: 
        #    return HTTPFound(location='/photo') 
        else:
            return {'project': 'raspistillWeb',
                    'imagedata' : picture_data,
                    'timelapse' : timelapse,
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
            'timelapseDatabase' : timelapsedb,
            'percentage_completed' : percentage_completed
            }

# View for the timelapse start - no site will be generated
@view_config(route_name='timelapse_start')
def timelapse_start_view(request):
    global timelapse
    app_settings = DBSession.query(Settings).first()
    timelapse = True
    filename = strftime("%Y-%m-%d_%H-%M-%S", localtime())
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

# View to take a photo - no site will be generated
@view_config(route_name='photo')
def photo_view(request):
    # Make sure the directories exist
    make_sure_path_exists(RASPISTILL_DIRECTORY)
    make_sure_path_exists(THUMBNAIL_DIRECTORY)
    
    if timelapse:
        return HTTPFound(location='/') 
    else:
        app_settings = DBSession.query(Settings).first()
        basename = strftime("IMG_%Y-%m-%d_%H-%M-%S", localtime())
        filename = basename + '.' + app_settings.encoding_mode
        #filename = picture.jpg
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
        #300, 168 = im.size
        #filedata['resolution'] = '300 x 168'
        
        #### Test: convert the format to RGB if we have jpg or gif format fromat ####
        #if (app_settings.encoding_mode == 'gif' ):
            #im = im.convert("RGB")
        im.thumbnail(THUMBNAIL_SIZE)
        #im.save(THUMBNAIL_DIRECTORY + basename + '.' + app_settings.encoding_mode)
        #### Try to to fill the transparent bit if the format doesn't do this ####
        #if im.mode in ('RGBA', 'LA'):
            #background = Image.new(im.mode[:-1], im.size)
            #background.paste(im, im.split()[-1])
            #im = background
        im.save(THUMBNAIL_DIRECTORY + basename + '.' + app_settings.encoding_mode, quality=THUMBNAIL_JPEG_QUALITY, optimize=True, progressive=True)
        #im.convert('RGB').save(THUMBNAIL_DIRECTORY + basename + '.jpg', 'JPEG', quality=THUMBNAIL_JPEG_QUALITY, optimize=True, progressive=True)
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
        return HTTPFound(location='/')  

# View for the archive delete - no site will be generated
@view_config(route_name='delete_picture')
def pic_delete_view(request):    
    p_id = request.params['id']
    pic = DBSession.query(Picture).filter_by(id=int(p_id)).first()
    print('Deleting picture and thumbnail...')
    # Delete on server in case if the image exists there
    if os.path.exists(RASPISTILL_DIRECTORY + '/' + pic.filename) and os.path.exists(THUMBNAIL_DIRECTORY + '/' + pic.filename):
        os.remove(RASPISTILL_DIRECTORY + '/' + pic.filename)
        os.remove(THUMBNAIL_DIRECTORY + '/' + pic.filename)
    DBSession.delete(pic)
    return HTTPFound(location='/archive')

# View for the timelapse delete - no site will be generated
@view_config(route_name='delete_timelapse')
def tl_delete_view(request):
    t_id = request.params['id']
    tl = DBSession.query(Timelapse).filter_by(id=int(t_id)).first()
    print 'Deleting time-lapse directory and archive...'
    # Delete on server in case if the directory and the archive exist there
    if os.path.exists(TIMELAPSE_DIRECTORY + tl.filename) and os.path.exists(TIMELAPSE_DIRECTORY + tl.filename + '.zip'):
        shutil.rmtree(TIMELAPSE_DIRECTORY + tl.filename)
        os.remove(TIMELAPSE_DIRECTORY + tl.filename + '.zip')
    #os.remove(TIMELAPSE_DIRECTORY + timelapse_database[int(request.params['id'])]['filename'] + '.tar.gz')
    #shutil.rmtree(TIMELAPSE_DIRECTORY + timelapse_database[int(request.params['id'])]['filename'])
    DBSession.delete(tl)
    return HTTPFound(location='/timelapse')

# View for settings form data - no site will be generated      
@view_config(route_name='save')
def save_view(request):
    global preferences_success_alert, preferences_fail_alert

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
    
    if preferences_fail_alert == []:
        preferences_success_alert = True 
    
    DBSession.flush()      
    return HTTPFound(location='/settings')  

# View for the reboot
@view_config(route_name='reboot', renderer='shutdown.mako')
def reboot_view(request):
    host_name = gethostname()
    os.system("sudo shutdown -r now")
    #os.system("sudo shutdown -k now")
    return {'project': 'raspistillWeb',
            'hostName' : host_name,
            }

# View for the shutdown
@view_config(route_name='shutdown', renderer='shutdown.mako')
def shutdown_view(request):
    host_name = gethostname()
    os.system("sudo shutdown -hP now")
    #os.system("sudo shutdown -k now")
    return {'project': 'raspistillWeb',
            'hostName' : host_name,
            }


###############################################################################
############ Helper functions to keep the code clean ##########################
###############################################################################


def take_photo(filename):
    app_settings = DBSession.query(Settings).first()
    
    if app_settings.image_ISO == 'auto':
        iso_call = ''
    else:
        iso_call = ' -ISO ' + str(app_settings.image_ISO)
    
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
    
    call (
        ['raspistill -t 500'
        + ' -n '
        + ' -w ' + str(app_settings.image_width)
        + ' -h ' + str(app_settings.image_height)
        + ' -e ' + app_settings.encoding_mode
        + ' -ex ' + app_settings.exposure_mode
        + ' -awb ' + app_settings.awb_mode
        + ' -rot ' + str(app_settings.image_rotation)
        + ' -ifx ' + app_settings.image_effect
        + iso_call
        + ' -o ' + RASPISTILL_DIRECTORY + filename],
        stdout=PIPE, shell=True
        )
#    if not (RASPISTILL_DIRECTORY == 'raspistillweb/pictures/'):
#        call (
#            ['ln -s ' + RASPISTILL_DIRECTORY + filename
#            + ' raspistillweb/pictures/' + filename], shell=True
#            )
    #generate_thumbnail(filename)
    
    if app_settings.bisque_enabled == 'Yes':
        resource = etree.Element('image', name=filename)
        etree.SubElement(resource, 'tag', name="experiment", value="Phenotiki")
        etree.SubElement(resource, 'tag', name="timestamp", value=os.path.splitext(filename)[0])
        bqsession = setbasicauth(app_settings.bisque_root_url, app_settings.bisque_user, app_settings.bisque_pswd)
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
    

    #call(['cp raspistillweb/pictures/preview.jpg raspistillweb/pictures/'+filename],shell=True)
    #generate_thumbnail(filename)
    return

def take_timelapse(filename):
    global timelapse, timelapse_database, p_timelapse, starttime, percentage_completed

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
        
        # For 'time lapse in progress' bar
        starttime = time()
        d = threading.Thread(target=percentage)
        d.start()
        
        #TODO: rename images with timestamp
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
    percentage_completed = 0   
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

def get_picture_data(picture):
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
    return imagedata

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

def make_sure_path_exists(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
        
# For 'time lapse in progress' bar
def percentage():
    global timelapse, starttime, percentage_completed
    app_settings = DBSession.query(Settings).first()
    while(timelapse and percentage_completed < 100):
        currenttime=time()
        percentage_completed = int((currenttime - starttime) * 100 // app_settings.timelapse_time)
        if (percentage_completed > 100):
            percentage_completed = 100
        sleep(1)
    return percentage_completed
