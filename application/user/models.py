"""Definition of database tables using ORM of user"""
import os
from sqlalchemy import Column
# from sqlalchemy.orm import backref
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, login_manager, images


class User(db.Model, UserMixin):
    """ORM for User"""
    # pylint: disable=too-many-instance-attributes, too-many-public-methods

    __tablename__ = 'users'

    ##########################################
    # Columns typical for every application  #
    ##########################################
    id = Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String(128))  # We store it hashed
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    confirmed = db.Column(db.Boolean, nullable=True, default=False)
    password_set = db.Column(db.Boolean, nullable=True, default=False)
    registered_with_google = db.Column(db.Boolean, nullable=True,
                                       default=False)
    failed_logins = db.Column(db.Integer, default=0)
    blocked = db.Column(db.Boolean, nullable=True, default=False)
    profile_pic_filename = db.Column(db.String, default=None, nullable=True)
    profile_pic_url = db.Column(db.String, default=None, nullable=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    ################################
    # Application specific columns #
    ################################

    #########################################
    # Methds typical for every application  #
    #########################################
    def __init__(self, **kwargs):
        """Initialize a user and set its default Role"""
        super(User, self).__init__(**kwargs)

        # Set default role for a regular new User
        self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def create_user(email, password, first_name, last_name,
                    confirmed=False,
                    role=None,
                    with_google=False,
                    profile_pic_url=None):
        """Creates a user from provided arguments"""

        # pylint: disable=too-many-arguments

        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name)
        if password:
            user.password = password
        if confirmed:
            user.confirmed = True
        if role:
            user.role = Role.query.filter_by(name=role).first()
        if with_google:
            user.registered_with_google = True
        if profile_pic_url:
            user.profile_pic_url = profile_pic_url

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def delete_account(user):
        """Deletes user and all it's owned Categories and Items"""

        # first delete all owned categories and all the items in those
        # categories, including items that other users added to the category.
        for category in user.categories:
            for item in category.items:
                db.session.delete(item)
            db.session.delete(category)
        db.session.commit()

        # then delete all remaining owned items
        for item in user.items:
            db.session.delete(item)
        db.session.commit()

        # finally, delete the user
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def insert_default_users():
        """Inserts a default admin, usermanager and user into the database"""
        user1 = User(email=current_app.config['ADMIN_EMAIL'],
                     password=current_app.config['ADMIN_PW'],
                     first_name=current_app.config['ADMIN_FIRST_NAME'],
                     last_name=current_app.config['ADMIN_LAST_NAME'],
                     confirmed=True)
        user1.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(user1)

        user2 = User(email=current_app.config['USERMANAGER_EMAIL'],
                     password=current_app.config['USERMANAGER_PW'],
                     first_name=current_app.config['USERMANAGER_FIRST_NAME'],
                     last_name=current_app.config['USERMANAGER_LAST_NAME'],
                     confirmed=True)
        user2.role = Role.query.filter_by(name='Usermanager').first()
        db.session.add(user2)

        user3 = User(email=current_app.config['USER_EMAIL'],
                     password=current_app.config['USER_PW'],
                     first_name=current_app.config['USER_FIRST_NAME'],
                     last_name=current_app.config['USER_LAST_NAME'],
                     confirmed=True)
        user3.role = Role.query.filter_by(name='User').first()
        db.session.add(user3)

        db.session.commit()

    @property
    def password(self):
        """By using a descriptor the 'getter' of password is deactivated
        and will now raise an AttributeError.
        """
        raise AttributeError('password is not a readable attribute')

    # Customize 'setter' of password to store password in hashed format
    @password.setter
    def password(self, password):
        """Hash the password before storing"""
        self.password_hash = generate_password_hash(password)
        self.password_set = True

    def verify_password(self, password):
        """Check the hashed password"""
        if (self.password_set and
                check_password_hash(self.password_hash, password)):
            self.failed_logins = 0
            return True
        else:
            self.failed_logins += 1
            if self.failed_logins > 2:
                self.blocked = True
            db.session.commit()
            return False

    def unblock(self):
        """Unblock the account by resetting the values"""
        self.failed_logins = 0
        self.blocked = False

    def generate_confirmation_token(self, expiration=3600):
        """Returns an email confirmation token"""
        ser = Serializer(current_app.config['SECRET_KEY'], expiration)
        return ser.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        """Corfirm user and return True if email confirmation token is OK"""
        ser = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = ser.loads(token.encode('utf-8'))
        except (BadSignature, SignatureExpired):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_password_token(self, expiration=3600):
        """Returns a reset password token"""
        ser = Serializer(current_app.config['SECRET_KEY'], expiration)
        return ser.dumps({'reset_password': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        """Verifies that reset_password token is OK, and returns user"""
        ser = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = ser.loads(token.encode('utf-8'))
            user_id = data.get('reset_password')
            return User.query.get(user_id)
        except (BadSignature, SignatureExpired):
            return None

        return None

    def generate_email_change_token(self, new_email, expiration=3600):
        """Returns an email change token"""
        ser = Serializer(current_app.config['SECRET_KEY'], expiration)
        return ser.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        """Change email and return True if email change token is OK"""
        ser = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = ser.loads(token.encode('utf-8'))
        except (BadSignature, SignatureExpired):
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
        """Returns an invitation token"""
        ser = Serializer(current_app.config['SECRET_KEY'], expiration)
        return ser.dumps(
            {'user_email': user_email}).decode('utf-8')

    @staticmethod
    def email_from_invitation_token(token):
        """Return user email if invitation token is OK"""
        ser = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = ser.loads(token.encode('utf-8'))
        except (BadSignature, SignatureExpired):
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
        """Returns True if user has admin privileges"""
        return self.can(Permission.ADMIN)

    def is_usermanager(self):
        """Returns True if user has usermanager privileges"""
        return self.can(Permission.CRUD_USERS)

    @property
    def profile_pic(self):
        """By using a descriptor 'getter' of profile_pic is deactivated and
        attempt to retrieve it will raise AttributeError"""
        raise AttributeError('profile_pic is not a readable attribute')

    # Customize 'setter' of profile_pic
    @profile_pic.setter
    def profile_pic(self, client_file_storage):
        """Upload the profile picture to the server and set the url"""

        # If we already have a profile picture, remove it
        if self.profile_pic_filename:
            filepath = os.path.join(
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
        """Serialize user object to json format"""
        json_user = {'url': url_for('api.user_detail', id=self.id)}
        return json_user

    def generate_auth_token(self, expiration):
        """Returns an authentication token"""
        ser = Serializer(current_app.config['SECRET_KEY'],
                         expires_in=expiration)
        return ser.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        """Return user id if authentication token is OK"""
        ser = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = ser.loads(token)
        except (BadSignature, SignatureExpired):
            return None
        return User.query.get(data['id'])

    ################################
    # Application specific methods #
    ################################


# For consistency, create a custom AnonymousUser class that implements the
# can() and is_administrator() methods. This object inherits from Flask-Login’s
# AnonymousUserMixin class and is registered as the class of the object that is
# assigned to current_user when the user is not logged in.
# This will enable the application to freely call current_user.can() and
# current_user.is_administrator() without having to check whether the user is
# logged in first.
class AnonymousUser(AnonymousUserMixin):
    """Dummy functionality for Anonymous user so calls to same methods can
    be made without additional checks.
    """
    # So, just disable the error R0201: Method could be a function
    # pylint: disable=no-self-use
    def can(self, unused_perm):
        """Anonymous user has no CUD permissions, so always return False"""
        return False

    def is_administrator(self):
        """Anonymous user is not admin, so return False"""
        return False

    def is_usermanager(self):
        """Anonymous user is not usermanager, so return False"""
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """Callback for flask_login to return user id"""
    return User.query.get(int(user_id))


class Permission:  # pylint: disable=too-few-public-methods
    """Defines the list of permissions"""
    # implementation based on "Flask Web Development - Chapter 9. User Roles"
    CRUD_OWNED = 1
    CRUD_USERS = 2
    ADMIN = 4


class Role(db.Model):
    """Defines the list of roles with their permissions:

    User role      | Permission value  | Description
    ---------------|-------------------|--------------------------------------
    Anonymous      | 0                 | User who is not logged in.
                   |                   | Can only register or login.
                   |                   |
    User           | 1                 | Basic permissions to CRUD owned data.
                   |                   | This is the default for new users.
                   |                   |
    Usermanager    | 2                 | Adds permission to CRUD other users
                   |                   |
                   |                   |
    Administrator  | 4                 | Full access, which includes permission
                   |                   | to change the roles of other users.

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
        """Populate the roles & permissions tables in the database."""
        roles = {
            'User': [Permission.CRUD_OWNED],
            'Usermanager': [Permission.CRUD_OWNED, Permission.CRUD_USERS],
            'Administrator': [Permission.CRUD_OWNED, Permission.CRUD_USERS,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for rol in roles:
            role = Role.query.filter_by(name=rol).first()
            if role is None:
                role = Role(name=rol)
            role.reset_permissions()
            for perm in roles[rol]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        """Helper function to add a permission"""
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """Helper function to remove a permission"""
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """Helper function to delete all permissions"""
        self.permissions = 0

    def has_permission(self, perm):
        """Helper function to check on a permission"""
        return self.permissions & perm == perm

    def __repr__(self):
        """Returns output of print"""
        return '<Role %r>' % self.name
