from flask import Flask, render_template

from config import Config
from .user import User

from .extensions import db, login_manager
from .filters import format_date, pretty_date, nl2br


# For import *
__all__ = ['create_app']


def create_app(config=Config, app_name=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = config.APP_NAME

    app = Flask(app_name, instance_relative_config=True)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_cli(app)

    return app


def configure_app(app, config):
    """Different ways of configurations."""

    # Load the configuration from ./config.py
    # http://flask.pocoo.org/docs/api/#configuration
    # Note: Potentially overwritten by TestConfig class during unit testing
    app.config.from_object(config)

    # Load the configuration from ./instance/config.py (secret information)
    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('config.py')


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-login
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    login_manager.init_app(app)


def configure_blueprints(app):
    """Configure blueprints in views."""

    from .user import user
    from .auth import auth
    from .api import api

    for bp in [user, auth, api]:
        app.register_blueprint(bp)


def configure_template_filters(app):
    """Configure filters."""

    app.jinja_env.filters["pretty_date"] = pretty_date
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["nl2br"] = nl2br


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging
    import os
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    if not os.path.exists('logs'):
        os.mkdir('logs')

    info_file_handler = logging.handlers.RotatingFileHandler('logs/info.log',
                                                             maxBytes=10240,
                                                             backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)


def configure_hook(app):

    @app.before_request
    def before_request():
        pass


# http://flask.pocoo.org/docs/latest/errorhandling/
def configure_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404


def configure_cli(app):

    @app.cli.command()
    def initdb():
        db.drop_all()
        db.create_all()