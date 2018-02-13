from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    BLOB
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Picture(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    image_effect = Column(Text)
    exposure_mode = Column(Text)
    awb_mode = Column(Text)
    resolution = Column(Text)
    ISO = Column(Integer)
    date = Column(Text)
    timestamp = Column(Text)
    filesize = Column(Integer)
    encoding_mode = Column(Text)

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    image_width = Column(Integer)
    image_height = Column(Integer)
    timelapse_interval = Column(Integer)
    timelapse_time = Column(Integer)
    exposure_mode = Column(Text)
    image_effect = Column(Text)
    awb_mode = Column(Text)
    image_ISO = Column(Text)
    image_rotation = Column(Text)
    encoding_mode = Column(Text)
    bisque_enabled = Column(Text)
    bisque_user = Column(Text)
    bisque_pswd = Column(Text)
    bisque_root_url = Column(Text)
    bisque_local_copy = Column(Text)
    gdrive_enabled = Column(Text)
    gdrive_folder = Column(Text)
    gdrive_user = Column(Text)
    gdrive_secret = Column(Text)
    gdrive_delete_files = Column(Text, default='Yes')
    number_images = Column(Integer)
    command_before_sequence = Column(Text)
    command_after_sequence = Column(Text)
    command_before_shot = Column(Text)
    command_after_shot = Column(Text)
    multisensor_enabled = Column(Text,default='No')
    sensors_name = Column(Text)

class Timelapse(Base):
    __tablename__ = 'timelapse'
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    timeStart = Column(Text)
    image_effect = Column(Text)
    exposure_mode = Column(Text)
    awb_mode = Column(Text)
    timeEnd = Column(Text)
    n_images = Column(Integer)
    resolution = Column(Text)
    encoding_mode = Column(Text)
    
class CameraParams(Base):
    __tablename__ = 'camera_params'
    id = Column(Integer, primary_key=True)
    device = Column(Text)
    timestamp = Column(Text)
    params = Column(BLOB)
    
    

Index('my_index', Picture.filename, unique=True, mysql_length=255)
