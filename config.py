import os
from sqlalchemy import create_engine
import urllib

class Config(object):
    SECRET_KEY = "Clave_Nueva"
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://paulo:root@127.0.0.1/dbPrueba"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://paulo:root@127.0.0.1/bdpizza"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
