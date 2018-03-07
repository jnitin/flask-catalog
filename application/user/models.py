# -*- coding: utf-8 -*-

from sqlalchemy import Column, desc
from sqlalchemy.orm import backref
from flask import current_app, g
from flask_login import UserMixin, AnonymousUserMixin
from application.extensions import db, login_manager, bcrypt
import os
import base64
from datetime import datetime, date, timedelta


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String(128))  # We store it hashed
    name = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # for token based authorization by api
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Set default role for a new User
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()


    # Use descriptors to deactivate 'getter' of password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # Customize 'setter' of password to store password in hashed format
    @password.setter
    def password(self, password):
        """Using bcrypt to hash the password"""
        self.password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        """Using bcrypt to check the hashed password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def can(self, permissions):
        """Returns True if User has all the permissions.

        Usage:
            u = User.query....
            u.can(Permission.CRUD_OWNED_ITEMS)
        """
        # perform a bitwise and to verify that all permissions are there
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def get_token(self, expires_in=3600):
        """Generates a new token for authorization"""
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        """Revokes the authorization token"""
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """Verifies that there is a user with this token, and that the
        the token has not yet expired"""
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

# For consistency, create a custom AnonymousUser class that implements the
# can() and is_administrator() methods. This object inherits from Flask-Login’s
# AnonymousUserMixin class and is registered as the class of the object that is
# assigned to current_user when the user is not logged in.
# This will enable the application to freely call current_user.can() and
# current_user.is_administrator() without having to check whether the user is
# logged in first.
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    """Defines the list of roles with their permissions:

    User role      | Bit value  | Description
    ---------------|------------|---------------------------------------------
    Anonymous      | 0b00000000 | User who is not logged in.
                   | (0x00)     | Can only register or login.
                   |            |
    User           | 0b00000001 | Basic permissions to CRUD owned items.
                   | (0x07)     | This is the default for new users.
                   |            |
    Administrator  | 0b11111111 | Full access
                   | (0xff)     |

    """

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.CRUD_OWNED_ITEMS, True),
            'Administrator': (0xff, False)
            }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()

class Permission:
    """Defines the list of permissions:

    Task Name        | Bit value  | Description
    -----------------|------------|---------------------------------------------
    CRUD owned items | 0b00000001 | CRUD owned items
                     | (0x01)     |
                     |            |
    Administer       | 0b10000000 | Administrative access to the site.
                     | (0x80)     |

    """
    CRUD_OWNED_ITEMS = 0x01
    ADMINISTER = 0x80
