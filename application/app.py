from flask import Flask

from config import Config
from .user import User, Role
from .catalog import Item

from .extensions import db, migrate, login_manager, api, images, mail
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
    configure_cli(app)

    return app


def configure_app(app, config):
    """Different ways of configurations."""

    # Load the configuration from ./config.py
    # http://flask.pocoo.org/docs/api/#configuration
    # Note: Potentially overwritten by TestConfig class during unit testing
    app.config.from_object(config)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-migrate
    migrate.init_app(app, db)

    # flask-login
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    login_manager.init_app(app)

    # Flask-REST-JSONAPI
    #  Add blueprint as 2nd argument, to get the api prefix (/api/v1) added to
    #  all the routes that are generated by the Flask-REST-JSONAPI
    #
    #  Note that adding the blueprint here already registers the blueprint with
    #  the app, so it is not needed to do this again in configure_blueprints.
    from .api import api as api_blueprint
    api.init_app(app, blueprint=api_blueprint)

    # flask-uploads
    from flask_uploads import configure_uploads
    configure_uploads(app, images)

    # flask-mail
    mail.init_app(app)


def configure_blueprints(app):
    """Configure blueprints in views."""

    from .user import user
    from .auth import auth
    from .email import email
    from .catalog import catalog
    # Note: api blueprint already initialzed above in api.init_app(---)
    # from .api import api

    # Register all blueprints with the application
    for blueprint in [user, auth, email, catalog]:
        app.register_blueprint(blueprint)


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
    # from logging.handlers import SMTPHandler

    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        info_file_handler = logging.handlers.RotatingFileHandler(
            'logs/info.log', maxBytes=10240, backupCount=10)
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')
                                      )
        app.logger.addHandler(info_file_handler)

    # Set info level on logger, which might be overwritten by handlers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')


def configure_hook(app):

    @app.before_request
    def before_request():
        pass


def configure_cli(app):

    @app.cli.command()
    def initdb():
        """This resets the database to default content"""
        app.logger.info("Dropping all tables in database...")
        db.drop_all()

        app.logger.info("Creating tables in database...")
        db.create_all()

        app.logger.info("Inserting roles...")
        Role.insert_roles()

        app.logger.info("Inserting default users...")
        User.insert_default_users()

        app.logger.info("Inserting default items...")
        Item.insert_default_items()
