# Initialize SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Add Flask-Migrate extension, for migrating databases
from flask_migrate import Migrate
migrate = Migrate()

# Add Flask-Login extension, for keeping track of login status during session
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'

# Add Flask-Bcrypt extension, for password hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# Add Flask-REST-JSONAPI extenstion, for JSON API 1.0 support
from flask_rest_jsonapi import Api
api = Api()

# Add flask-uploads, to easily upload files
from flask_uploads import UploadSet, IMAGES
# Configure the image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)

# Add flask-mail
from flask_mail import Mail
mail = Mail()
