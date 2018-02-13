import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Picture,
    Settings,
    Timelapse,
    CameraParams,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        picture = Picture(
                        filename = '-',
                        image_effect = '-',
                        exposure_mode = '-',
                        awb_mode = '-',
                        resolution = '-',
                        ISO = 1,
                        date = '-',
                        timestamp = '-',
                        filesize = 1,
                        encoding_mode = '-'
                        )
        DBSession.add(picture)

        app_settings = Settings(
                        image_width = 1024,
                        image_height = 768,
                        timelapse_interval = 5,
                        timelapse_time = 20,
                        exposure_mode = 'auto',
                        image_effect = 'none',
                        awb_mode = 'auto',
                        image_ISO = 'auto',
                        image_rotation = '180',
                        encoding_mode = 'png',
                        bisque_enabled = 'No',
                        bisque_user = '',
                        bisque_pswd = '',
                        bisque_root_url = 'http://bisque.iplantcollaborative.org',
                        bisque_local_copy = 'Yes',
                        gdrive_enabled = 'No',
                        gdrive_folder = '',
                        gdrive_user = '',
                        gdrive_secret= '',
                        number_images = 1,
                        command_before_sequence = '',
                        command_after_sequence = '',
                        command_before_shot = '',
                        command_after_shot = '',
                        multisensor_enabled = 'No'
                        )
        DBSession.add(app_settings)

        timelapse = Timelapse(
                        filename = '-',
                        timeStart = '-',
                        image_effect = '-',
                        exposure_mode = '-',
                        awb_mode = '-',
                        timeEnd = '-',
                        n_images = 1,
                        resolution = '-',
                        encoding_mode = '-',
                        )

        DBSession.add(timelapse)
        
        camara_params = CameraParams(timestamp='-',params='')
        DBSession.add(camera_params)
