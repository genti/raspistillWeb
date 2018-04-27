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

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import multisensors as ms

from .models import (
    DBSession,
    Base,
    Settings,
    )

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    
    config = Configurator(settings=settings)
    #config.include('pyramid_chameleon')
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('pictures', 'pictures', cache_max_age=3600)
    config.add_static_view('thumbnails', 'thumbnails', cache_max_age=3600)
    config.add_static_view('time-lapse', 'time-lapse', cache_max_age=3600)
    config.add_route('home','/')
    config.add_route('settings','/settings')
    config.add_route('save','/save')
    config.add_route('action_picture','/action_picture')
    config.add_route('delete_timelapse','/delete_timelapse')
    config.add_route('archive','/archive')
    config.add_route('timelapse','/timelapse')
    config.add_route('photo','/photo')
    config.add_route('timelapse_start','/timelapse_start')
    config.add_route('timelapse_stop','/timelapse_stop')
    config.add_route('timelapse_upload_gdrive','/timelapse_upload_gdrive')
    config.add_route('reboot','/reboot')
    config.add_route('shutdown','/shutdown')
    config.add_route('external_photo','/external_photo')
    config.add_route('upload_gdrive','/upload_gdrive')
    config.add_route('camera_calibr','/camera_calibr')
    config.add_route('camera_calibr_do_pic','/camera_calibr_do_pic')
    config.add_route('camera_calibr_do_calibr','/camera_calibr_do_calibr')
    config.add_route('camera_calibrated_action','/camera_calibrated_action')
    config.scan()
    
    app_settings = DBSession.query(Settings).first()
    ms.init_thread(app_settings)
    
    return config.make_wsgi_app()
