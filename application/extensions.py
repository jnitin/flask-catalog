# -*- coding: utf-8 -*-

# Initialize SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Add Flask-Bcrypt extension, for password hashing
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
#from mega: login_manager.login_view = 'auth.login' # TODO?? # We only have an api...

# Add Flask-Bcrypt extension, for password hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# https://docs.getsentry.com/hosted/clients/python/integrations/flask/
#AB from raven.contrib.flask import Sentry
#AB sentry = Sentry()
