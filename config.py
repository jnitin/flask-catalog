"""Contains non-sensitive configurations for application"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # do NOT define secret information here.
    # Define those in ./instance/config.py
    APP_NAME = "application"
    COPYRIGHT = "Arjaan Buijk 2018"

    # During development, use sqlite database
    DATABASE_PATH = os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Avoid DeprecationWarning: Request.is_xhr is deprecated.
    JSONIFY_PRETTYPRINT_REGULAR = False
