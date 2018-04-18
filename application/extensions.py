from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_rest_jsonapi import Api
from flask_uploads import UploadSet, IMAGES
from flask_mail import Mail

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
