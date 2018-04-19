from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_rest_jsonapi import Api
from flask_uploads import UploadSet, IMAGES
from flask_mail import Mail

##############################################################################
# Flask coding convention is to use lowercase for exensions and store them as
# module level variables. Pylint interprets module level variables as
# constants, which according to the PEP 8 Style Guide must use UPPER_CASE
# naming style.
#
# Avoid errors from pylint like this one:
# C0103: Constant name "db" doesn't conform to UPPER_CASE naming style
#
# pylint: disable=invalid-name
##############################################################################

# Initialize SQLAlchemy
db = SQLAlchemy()

# Add Flask-Migrate extension, for migrating databases
migrate = Migrate()

# Add Flask-Login extension, for keeping track of login status during session
login_manager = LoginManager()
login_manager.session_protection = 'strong'

# Add Flask-REST-JSONAPI extenstion, for JSON API 1.0 support
api = Api()

# Add flask-uploads, to easily upload files
# Configure the image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)

# Add flask-mail
mail = Mail()
