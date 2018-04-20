"""Contains non-sensitive configurations for application"""

import os
import os.path
import json
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # path to this file

# load content of .env as environment variables for our application
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config(object):
    """Configuration of the flask application."""
    # Accepted pattern in Flask to use a class for configuration
    # See: http://flask.pocoo.org/docs/0.12/config/
    # pylint: disable=too-few-public-methods

    APP_NAME = "application"  # must be same as folder name
    COPYRIGHT = "Arjaan Buijk 2018"

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'not-so-secret-key'
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS') or 2)

    # Option to log directly to stdout
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # We use gmail as our mail server
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = (os.environ.get('MAIL_USE_TLS') == 'True')
    MAIL_USE_SSL = (os.environ.get('MAIL_USE_SSL') == 'True')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # In a new database, we initialize one ADMIN, one USERMANAGER and one USER
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    ADMIN_PW = os.environ.get('ADMIN_PW') or 'not-so-good-password'
    ADMIN_FIRST_NAME = os.environ.get('ADMIN_FIRST_NAME') or 'Example'
    ADMIN_LAST_NAME = os.environ.get('ADMIN_LAST_NAME') or 'Admin'

    USERMANAGER_EMAIL = os.environ.get('USERMANAGER_EMAIL') or \
        'manager@example.com'
    USERMANAGER_PW = os.environ.get('USERMANAGER_PW') or \
        'not-so-good-password'
    USERMANAGER_FIRST_NAME = os.environ.get('USERMANAGER_FIRST_NAME') or \
        'Example'
    USERMANAGER_LAST_NAME = os.environ.get('USERMANAGER_LAST_NAME') or \
        'Manager'

    USER_EMAIL = os.environ.get('USER_EMAIL') or 'user@example.com'
    USER_PW = os.environ.get('USER_PW') or 'not-so-good-password'
    USER_FIRST_NAME = os.environ.get('USER_FIRST_NAME') or 'Example'
    USER_LAST_NAME = os.environ.get('USER_LAST_NAME') or 'User'

    # During development, use sqlite database on disk
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Avoid DeprecationWarning: Request.is_xhr is deprecated.
    JSONIFY_PRETTYPRINT_REGULAR = False

    ##################################
    # Uploads (eg. profile pictures) #
    ##################################

    IMAGE_DEST = os.environ.get('IMAGE_DEST')
    DEFAULT_DEST = os.environ.get('DEFAULT_DEST')

    # see description at https://pythonhosted.org/Flask-Uploads/
    UPLOADED_IMAGES_DEST = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        IMAGE_DEST)
    # UPLOADED_IMAGES_URL = TODO when uploading a lot!

    UPLOADS_DEFAULT_DEST = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        DEFAULT_DEST)
    # UPLOADS_DEFAULT_URL = TODO!

    #################
    # Google OAUTH2 #
    #################
    GOOGLE_OAUTH2 = json.loads(os.environ.get('GOOGLE_OAUTH2_ENV'))
    GOOGLE_OAUTH2_FILE_PATH = os.environ.get('GOOGLE_OAUTH2_FILE_PATH')
    #
    # google auth also requires the json inside an actual file on disk
    #
    GOOGLE_OAUTH2_FILE = os.path.join(
        os.path.dirname(__file__), GOOGLE_OAUTH2_FILE_PATH)

    # print('dumping google oauth2 json to disk')
    with open(GOOGLE_OAUTH2_FILE, 'w') as f:
        json.dump(GOOGLE_OAUTH2, f, indent=4)


class TestConfig(Config):
    """Configuration for unit tests"""
    # Accepted pattern in Flask to use a class for configuration
    # See: http://flask.pocoo.org/docs/0.12/config/
    # pylint: disable=too-few-public-methods

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In memory database

    # turn CSRF off to enable unittesting of frontend without CSRF tokens
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
