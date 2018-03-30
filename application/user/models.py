from sqlalchemy import Column, desc
from sqlalchemy.orm import backref
from flask import current_app, g, url_for, render_template
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ..extensions import db, login_manager, bcrypt, images
import os
import base64
from datetime import datetime, date, timedelta


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    ############################################
    ## Columns typical for every application  ##
    ############################################
    id = Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String(128))  # We store it hashed
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    confirmed = db.Column(db.Boolean, nullable=True, default=False)
    failed_logins = db.Column(db.Integer, default=0)
    blocked = db.Column(db.Boolean, nullable=True, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    profile_pic_filename = db.Column(db.String, default=None, nullable=True)
    profile_pic_url = db.Column(db.String, default=None, nullable=True)

    ##################################
    ## Application specific columns ##
    ##################################


    ###########################################
    ## Methds typical for every application  ##
    ###########################################
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # Set default role for a regular new User
        self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def insert_default_users():
        """Inserts a default admin, usermanager and user into the database"""
        u1 = User(email=current_app.config['ADMIN_EMAIL'],
                  password=current_app.config['ADMIN_PW'],
                  first_name=current_app.config['ADMIN_FIRST_NAME'],
                  last_name=current_app.config['ADMIN_LAST_NAME'],
                  confirmed=True)
        u1.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(u1)

        u2 = User(email=current_app.config['USERMANAGER_EMAIL'],
                  password=current_app.config['USERMANAGER_PW'],
                  first_name=current_app.config['USERMANAGER_FIRST_NAME'],
                  last_name=current_app.config['USERMANAGER_LAST_NAME'],
                  confirmed=True)
        u2.role = Role.query.filter_by(name='Usermanager').first()
        db.session.add(u2)

        u3 = User(email=current_app.config['USER_EMAIL'],
                  password=current_app.config['USER_PW'],
                  first_name=current_app.config['USER_FIRST_NAME'],
                  last_name=current_app.config['USER_LAST_NAME'],
                  confirmed=True)
        u3.role = Role.query.filter_by(name='User').first()
        db.session.add(u3)

        db.session.commit()

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
        if bcrypt.check_password_hash(self.password_hash, password):
            self.failed_logins = 0
            return True
        else:
            self.failed_logins += 1
            if self.failed_logins > 2:
                self.blocked = True
            db.session.commit()
            return False


    def unblock(self):
        self.failed_logins = 0
        self.blocked = False


    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    @staticmethod
    def generate_invitation_token(user_email, expiration=7*3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'user_email': user_email}).decode('utf-8')

    @staticmethod
    def get_user_email_from_invitation_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user_email = data.get('user_email')
        if user_email is None:
            return False
        if User.query.filter_by(email=user_email).first() is not None:
            return False
        return user_email

    def can(self, perm):
        """Returns True if User has all the permissions.

        Usage:
            u = User.query....
            u.can(Permission.CRUD_OWNED_ITEMS)
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def is_usermanager(self):
        return self.can(Permission.CRUD_USERS)

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

    # Use descriptor to deactivate 'getter' of profile_pic
    @property
    def profile_pic(self):
        raise AttributeError('profile_pic is not a readable attribute')

    # Customize 'setter' of profile_pic
    @profile_pic.setter
    def profile_pic(self, client_file_storage):
        """Upload the profile picture to the server and set the url"""

        # If we already have a profile picture, remove it
        if self.profile_pic_filename:
            filepath=os.path.join(
                current_app.config['UPLOADED_IMAGES_DEST'],
                self.profile_pic_filename)
            os.remove(filepath)
            self.profile_pic_filename = None
            self.profile_pic_url = None

        # This uploads & saves the file on the server
        # NOTE: It uses the secure_filename function...
        server_filename = images.save(client_file_storage)

        # Generate the URL to this file
        url = images.url(server_filename)

        # Store information with the user
        self.profile_pic_filename = server_filename
        self.profile_pic_url = url

    def to_json(self):
        json_user = {
                'url': url_for('api.user_detail', id=self.id)
            }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    ##################################
    ## Application specific methods ##
    ##################################


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

    def is_usermanager(self):
        return False

login_manager.anonymous_user = AnonymousUser

class Permission:
    """Defines the list of permissions"""
    # implementation based on "Flask Web Development - Chapter 9. User Roles"
    CRUD_OWNED = 1
    CRUD_USERS = 2
    ADMIN = 4

class Role(db.Model):
    """Defines the list of roles with their permissions:

    User role      | Permission value  | Description
    ---------------|-------------------|---------------------------------------------
    Anonymous      | 0                 | User who is not logged in.
                   |                   | Can only register or login.
                   |                   |
    User           | 1                 | Basic permissions to CRUD owned entries.
                   |                   | This is the default for new users.
                   |                   |
    Usermanager    | 2                 | Adds permission to CRUD other users
                   |                   |
                   |                   |
    Administrator  | 4                 | Full access, which includes permission to
                   |                   | change the roles of other users.

    """
    # implementation based on "Flask Web Development - Chapter 9. User Roles"

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.CRUD_OWNED],
            'Usermanager': [Permission.CRUD_OWNED, Permission.CRUD_USERS],
            'Administrator': [Permission.CRUD_OWNED, Permission.CRUD_USERS,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name
