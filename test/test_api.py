"""Unit tests for api"""
import os
import sys
import unittest
import requests
import json
from base64 import b64encode
from test.utils import pprint_sequence, pprint_response, ordered
from flask import current_app, url_for, g
from flask_uploads import FileStorage
from datetime import datetime, date, time
from config import Config
from application import create_app
from application.user import User, AnonymousUser, Role, Permission
from application.catalog import Category, Item
from application.extensions import db
from application.extensions import api as rest_jsonapi


class TestConfig(Config):
    """Configuration for unit testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In memory database

    # turn CSRF off to enable unittesting of frontend without CSRF tokens
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False


class APITestCase(unittest.TestCase):
    def setUp(self):
        # This seems a bug in Flask_REST_JSONAPI
        #
        # The Flask_REST_JSONAPI does not remove the Blue Blueprint objects
        # stored internally when the application objects they are applied to
        # is destroyed.
        #
        # I found this same issue is there for Flask Restful extension as
        # discovered and described in the book Mastering Flask:
        # https://books.google.com/books?id=NdZOCwAAQBAJ&pg=PA219&lpg=PA219&dq=flask:+how+to+destroy+application+object&source=bl&ots=nx7L_UG3EM&sig=yA-DG-ZYPtM5JxKJsFiXrhSkwzQ&hl=en&sa=X&ved=0ahUKEwies8G-x-7ZAhUh_IMKHdYKDCsQ6AEIdDAG#v=onepage&q=flask%3A%20how%20to%20destroy%20application%20object&f=false
        #
        # The result is that during a 2nd test, the view routes are created
        # twice and this error will be thrown:
        # builtins.AssertionError: View function mapping is overwriting an
        # existing endpoint function: api.api.user_list
        #
        # Workaround is to reset them manually
        rest_jsonapi.resources = []

        self.app = create_app(TestConfig)
        # initialize the test client
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        User.insert_default_users()
        Item.insert_default_items()

        #####################################################################
        # list of users we will use during testing
        # The first user in the list is admin, because email is ADMIN_EMAIL
        # Rest will become default users.
        self.user_url = '/api/v1/users/'
        self.user_headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
            }
        self.user_data_list = []
        for i in range(10):
            self.user_data_list.append({
                "data": {
                    "type": "user",
                    "attributes": {
                        "email": "demoEmail{}@gmail.com".format(i),
                        "password": "pw{}".format(i),
                        "first_name": "Demo{}".format(i),
                        "last_name": "Example{}".format(i)
                    }
                }
            })

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, email, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
        }

    def get_api_headers_multiform(self, email, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Content-Type': 'multipart/form-data',
            'Accept': 'application/vnd.api+json'
        }

    def populate_database_with_users(self, num_users=None,
                                     direct_to_db=True):
        """Populate database with num_users from self.user_data_list.

        - If num_users is not defined, it will use the whole list
        - If direct_to_db is:
           True : data entered directly into the database,
           False: entered via POST requests (slow for large numbers)
        """
        if num_users is None:
            num_users = len(self.user_data_list)

        if direct_to_db:
            for i in range(num_users):
                attributes = self.user_data_list[i]['data']['attributes']
                p = User(email=attributes['email'],
                         password=attributes['password'],
                         first_name=attributes['first_name'],
                         last_name=attributes['last_name'])
                db.session.add(p)
            db.session.commit()
        else:
            url = '/api/v1/users/'
            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Accept': 'application/vnd.api+json'
                }
            for i in range(num_users):
                data = self.user_data_list[i]
                response = self.client().post(url,
                                              headers=headers,
                                              data=json.dumps(data))
                self.verify_response_is_201_CREATED(response)
                response_data = json.loads(response.data.decode())

        # Make the 2nd user a user manager
        if num_users > 1:
            u = User.query.filter_by(id='2').one()
            u.role = Role.query.filter_by(name='Usermanager').first()

    def get_token(self, user):
        #
        # Note: We use HTTPAUTH for authentication, which uses
        #       application/json for content-type
        #
        #       We encode the email and password into the headers,
        #       using b64encoding.
        #
        email = user['data']['attributes']['email']
        password = user['data']['attributes']['password']
        url = '/api/v1/token'
        headers = {
            'Content-Length': '0',
            'Authorization': 'Basic ' + b64encode("{0}:{1}".format(
                email, password).encode('utf-8')).decode(),
            'Content-Type': 'application/json'
        }
        response = self.client().post(url, headers=headers)
        self.verify_response_is_200_OK(response)
        if response.status_code != 200:
            return None
        else:
            token = json.loads(response.data.decode())['token']
            return token

    def verify_users_are_correctly_in_db(self):
        # During population, we made the first user an admin
        admins = User.query.filter_by(id='1').all()
        self.assertEqual(len(admins), 1)
        admin = admins[0]
        self.assertEqual(admin.role.name, 'Administrator')
        self.assertTrue(admin.is_administrator())
        self.assertTrue(admin.can(Permission.CRUD_OWNED))
        self.assertTrue(admin.can(Permission.CRUD_USERS))
        self.assertTrue(admin.can(Permission.ADMIN))

        # During population, we made the second user a usermanager
        p = User.query.filter_by(id='2').one()
        p.role = Role.query.filter_by(name='Usermanager').first()
        self.assertEqual(p.role.name, 'Usermanager')
        self.assertFalse(p.is_administrator())
        self.assertTrue(p.can(Permission.CRUD_OWNED))
        self.assertTrue(p.can(Permission.CRUD_USERS))
        self.assertFalse(p.can(Permission.ADMIN))

        #  All other users are Users. Check 3rd user.
        p = User.query.filter_by(id='3').one()
        self.assertEqual(p.role.name, 'User')
        self.assertFalse(p.is_administrator())
        self.assertTrue(p.can(Permission.CRUD_OWNED))
        self.assertFalse(p.can(Permission.CRUD_USERS))
        self.assertFalse(p.can(Permission.ADMIN))

    def verify_response_is_200_OK(self, response):
        self.assertEqual(response.status_code, 200)

    def verify_response_is_201_CREATED(self, response):
        self.assertEqual(response.status_code, 201)

    def verify_response_is_400_BAD_REQUEST(self, response):
        self.assertEqual(response.status_code, 400)

    def verify_response_is_401_UNAUTHORIZED(self, response):
        self.assertEqual(response.status_code, 401)

    def verify_response_is_403_FORBIDDEN(self, response):
        self.assertEqual(response.status_code, 403)

    def verify_response_is_404_NOT_FOUND(self, response):
        self.assertEqual(response.status_code, 404)

    def verify_response_is_405_METHOD_NOT_ALLOWED(self, response):
        self.assertEqual(response.status_code, 405)

    def verify_response_is_401_or_405(self, response):
        self.assertTrue(response.status_code == 401 or
                        response.status_code == 405)

    ##########################################################################
    def test_0_0_404(self):
        url = '/api/v1/wrong/url'
        headers = self.get_api_headers('email', 'password')
        response = self.client().get(url, headers=headers)
        self.verify_response_is_404_NOT_FOUND(response)
        # TODO: we need to get a JSON response back !
        # Right now, it returns an HTML page
        # Implement an error handler
        # json_response = json.loads(response.get_data(as_text=True))
        # self.assertEqual(json_response['error'], 'not found')

    def test_0_1_no_auth(self):
        url = '/api/v1/users/'
        response = self.client().get(url,
                                     content_type='application/json')
        self.verify_response_is_401_UNAUTHORIZED(response)

        # NOTE: we must be able to register a new user without auth,
        # but that is tested below

    def test_0_2_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        url = '/api/v1/users/{}'.format(u.id)
        headers = self.get_api_headers('john@example.com', 'dog')
        response = self.client().get(url, headers=headers)
        self.verify_response_is_401_UNAUTHORIZED(response)

    def test_0_3_token_auth(self):
        # add a confirmed
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        url = '/api/v1/users/{}'.format(u.id)
        headers = self.get_api_headers('bad-token', '')
        response = self.client().get(url, headers=headers)
        self.verify_response_is_401_UNAUTHORIZED(response)

        # get a token
        url = '/api/v1/token'
        headers = self.get_api_headers('john@example.com', 'cat')
        response = self.client().post(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        url = '/api/v1/users/{}'.format(u.id)
        headers = self.get_api_headers(token, '')
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)

    def test_0_4_anonymous(self):
        url = '/api/v1/users/'
        headers = self.get_api_headers('', '')
        response = self.client().get(url, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_0_5_unconfirmed_account(self):
        # add an unconfirmed user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=False,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # get user info with the unconfirmed account
        url = '/api/v1/users/{}'.format(u.id)
        headers = self.get_api_headers('john@example.com', 'cat')
        response = self.client().get(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

        # get a token with the unconfirmed account
        url = '/api/v1/token'
        headers = self.get_api_headers('john@example.com', 'cat')
        response = self.client().post(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

    def test_0_6_routes_info(self, print_routes=True):
        """As admin, Get all the available routes, for debug purposes"""
        url = '/api/v1/help'
        headers = self.get_api_headers(current_app.config['ADMIN_EMAIL'],
                                       current_app.config['ADMIN_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        if print_routes:
            pprint_response(response)

    def test_0_6_routes_info_again(self):
        """Get all the available routes again, to check that the
        rest_jsonapi.resources are reset properly from previous unittest"""
        self.test_0_6_routes_info(print_routes=False)

#     def test_0_0_playground_with_empty_database(self):
#         """Just a playground to use while in the debugger"""
#         # break here for playing with empty database
#         ...

#     def test_0_0_playground_with_populated_database(self):
#         """Just a playground to use while in the debugger"""
#         self.populate_database_with_users(direct_to_db=True)
#
#         # Check all is ok in the database
#         db_users = User.query.all()
#         self.assertEqual(len(db_users),len(self.user_data_list))
#
#         # break here for playing with populated database, no tokens are set
#         ...
#
#         # get a token for the first user (an admin)
#         admin = self.user_data_list[0]
#         admin_email = admin['data']['attributes']['email']
#         admin_token = self.get_token(admin)
#         admin_headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                     'Accept': 'application/vnd.api+json',
#                     'Authorization': 'Bearer {}'.format(admin_token)
#             }
#
#         # get a token for the second user (a usermanager)
#         usermanager = self.user_data_list[1]
#         usermanager_email = usermanager['data']['attributes']['email']
#         usermanager_token = self.get_token(usermanager)
#         usermanager_headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                     'Accept': 'application/vnd.api+json',
#                     'Authorization': 'Bearer {}'.format(usermanager_token)
#             }
#
#         # get a token for the third user (a regular user)
#         user = self.user_data_list[2]
#         user_email = user['data']['attributes']['email']
#         user_token = self.get_token(user)
#         user_headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 'Authorization': 'Bearer {}'.format(user_token)
#                 }
#
#         # break here for playing with populated database, 3 tokens are set
#         # for admin, usermanager, user
#         ...
#
#
#     def test_1_1_create_users_via_POST_requests(self):
#         """POST /api/v1/users/: creates new users with correct permissions"""
#         self.populate_database_with_users(num_users=3, direct_to_db=False)
#         # check that we have all the users in the database.
#         self.assertEqual(len(db.session.query(User).all()),3)
#         self.verify_users_are_correctly_in_db()
#
#     def test_1_2_get_token(self):
#         """POST /token: API must return a token"""
#         self.populate_database_with_users(num_users=1)
#
#         # get a token for the first user
#         user = self.user_data_list[0]
#         token = self.get_token(user)

    def test_1_3_invite(self):
        # An admin can invite a new user to join
        url = '/api/v1/invite/arjaan.buijk@gmail.com'
        headers = self.get_api_headers(current_app.config['ADMIN_EMAIL'],
                                       current_app.config['ADMIN_PW'])
        response = self.client().post(url, headers=headers)
        self.verify_response_is_201_CREATED(response)

        # A Usermanager can not invite a new user to join
        url = '/api/v1/invite/arjaan.buijk@gmail.com'
        headers = self.get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                       current_app.config['USERMANAGER_PW'])
        response = self.client().post(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

        # A User can not invite a new user to join
        url = '/api/v1/invite/arjaan.buijk@gmail.com'
        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().post(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

    def test_1_4_register(self):
        # Register a new user via POST command
        url = '/api/v1/users/'
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
            }
        data = {
            "data": {
                "type": "user",
                "attributes": {
                    "email": 'arjaan.buijk@gmail.com',
                    "password": "a_real_password",
                    "first_name": "Arjaan",
                    "last_name": "Buijk"
                }
            }
        }
        response = self.client().post(url,
                                      headers=headers,
                                      data=json.dumps(data))
        self.verify_response_is_201_CREATED(response)
        response_data = json.loads(response.data.decode())

        # get a token
        url = '/api/v1/token'
        headers = self.get_api_headers('arjaan.buijk@gmail.com',
                                       'a_real_password')

        # verify that when email is not yet confirmed, user cannot login or
        # receive a token
        response = self.client().post(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

        # activate the account
        # we activate it by going into the database directly...
        u = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        u.confirmed = True

        # now we can get a token
        response = self.client().post(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        url = '/api/v1/users/{}'.format(u.id)
        headers = self.get_api_headers(token, '')
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)

    def test_1_5_upload_profile_pic(self):
        # Register a new user via POST command
        url = '/api/v1/users/'
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
            }
        data = {
            "data": {
                "type": "user",
                "attributes": {
                    "email": 'arjaan.buijk@gmail.com',
                    "password": "a_real_password",
                    "first_name": "Arjaan",
                    "last_name": "Buijk"
                }
            }
        }
        response = self.client().post(url,
                                      headers=headers,
                                      data=json.dumps(data))
        self.verify_response_is_201_CREATED(response)
        response_data = json.loads(response.data.decode())

        # activate the account
        # we activate it by going into the database directly...
        u = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        u.confirmed = True

        # get a token
        url = '/api/v1/token'
        headers = self.get_api_headers('arjaan.buijk@gmail.com',
                                       'a_real_password')
        response = self.client().post(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # upload a profile picture, using multipart/form-data type request
        url = '/api/v1/profile_pic'
        headers = self.get_api_headers_multiform(token, '')
        with open('test_profile_pic.gif', 'rb') as fp:
            file = FileStorage(fp)
            data = {"profile_pic": file}
            response = self.client().post(url,
                                          headers=headers,
                                          data=data)
            self.verify_response_is_201_CREATED(response)
            response_data = json.loads(response.data.decode())

        # retrieve the profile picture
        url = '/api/v1/profile_pic'
        headers = self.get_api_headers_multiform(token, '')
#         headers = {
#                 'Content-Type': 'multipart/form-data',
#                 'Accept': 'application/vnd.api+json',
#                 'Authorization': 'Bearer {}'.format(token)
#                 }
        response = self.client().get(url,
                                     headers=headers)
        self.verify_response_is_200_OK(response)

    def test_1_6_block_account(self):
        # Register a new user via POST command
        url = '/api/v1/users/'
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
            }
        data = {
            "data": {
                "type": "user",
                "attributes": {
                    "email": 'arjaan.buijk@gmail.com',
                    "password": "a_real_password",
                    "first_name": "Arjaan",
                    "last_name": "Buijk"
                }
            }
        }
        response = self.client().post(url,
                                      headers=headers,
                                      data=json.dumps(data))
        self.verify_response_is_201_CREATED(response)
        response_data = json.loads(response.data.decode())

        # activate the account
        # we activate it by going into the database directly...
        u = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        u.confirmed = True
        # Get token 3 times with wrong password, after which account is blocked
        url = '/api/v1/token'
        headers = self.get_api_headers('arjaan.buijk@gmail.com',
                                       'a_wrong_password')
        for _ in range(2):
            response = self.client().post(url, headers=headers)
            self.verify_response_is_401_UNAUTHORIZED(response)

        # Verify that on 3rd and following attempts the account is blocked
        for _ in range(2):
            response = self.client().post(url, headers=headers)
            self.verify_response_is_403_FORBIDDEN(response)

        # Verify I also cannot re-register when account is blocked
        url = '/api/v1/users/'
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
            }
        data = {
            "data": {
                "type": "user",
                "attributes": {
                    "email": 'arjaan.buijk@gmail.com',
                    "password": "a_real_password",
                    "first_name": "Arjaan",
                    "last_name": "Buijk"
                }
            }
        }
        response = self.client().post(url,
                                      headers=headers,
                                      data=json.dumps(data))
        self.verify_response_is_403_FORBIDDEN(response)

        # Verify I cannot unblock myself
        url = '/api/v1/users/{}/unblock'.format(u.id)
        headers = self.get_api_headers('arjaan.buijk@gmail.com',
                                       'a_real_password')
        response = self.client().post(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

        # An admin can unblock the account
        url = '/api/v1/users/{}/unblock'.format(u.id)
        headers = self.get_api_headers(current_app.config['ADMIN_EMAIL'],
                                       current_app.config['ADMIN_PW'])
        response = self.client().post(url, headers=headers)
        self.verify_response_is_201_CREATED(response)
        self.assertFalse(u.blocked)
        self.assertEqual(u.failed_logins, 0)

        # block it again, and test that usermanager can unblock it
        u.failed_logins = 3
        u.blocked = True
        url = '/api/v1/users/{}/unblock'.format(u.id)
        headers = self.get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                       current_app.config['USERMANAGER_PW'])
        response = self.client().post(url, headers=headers)
        self.verify_response_is_201_CREATED(response)
        self.assertFalse(u.blocked)
        self.assertEqual(u.failed_logins, 0)

    def test_2_0_get_users(self):
        url = '/api/v1/users/'

        # admin can retrieve all 3 users
        headers = self.get_api_headers(current_app.config['ADMIN_EMAIL'],
                                       current_app.config['ADMIN_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 3)

        # manager can retrieve all 3 users
        headers = self.get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                       current_app.config['USERMANAGER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 3)

        # user can retrieve only self
        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 1)

    def test_2_1_get_user_by_id(self):
        url = '/api/v1/users/3'

        # admin can retrieve details of any user
        headers = self.get_api_headers(current_app.config['ADMIN_EMAIL'],
                                       current_app.config['ADMIN_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))

        # manager can retrieve details of any user
        headers = self.get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                       current_app.config['USERMANAGER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))

        # user can retrieve details of self only
        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))

        url = '/api/v1/users/2'
        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_403_FORBIDDEN(response)

    def test_2_2_get_user_by_category_id(self):
        url = '/api/v1/categories/1/user'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '3')

    def test_2_3_get_user_by_item_id(self):
        url = '/api/v1/items/1/user'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '3')

    def test_3_0_get_categories(self):
        url = '/api/v1/categories/'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 2)

    def test_3_1_get_category_by_id(self):
        url = '/api/v1/categories/2'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '2')

    def test_3_2_get_categories_of_user(self):
        url = '/api/v1/users/3/categories/'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 2)

    def test_4_0_get_items(self):
        url = '/api/v1/items/'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 40)

    def test_4_1_get_item_by_id(self):
        url = '/api/v1/items/21'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '21')

    def test_4_2_get_items_of_user(self):
        url = '/api/v1/users/3/items/'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 40)

        url = '/api/v1/users/2/items/'

        headers = self.get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                       current_app.config['USERMANAGER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 0)

    def test_4_3_get_items_of_category(self):
        url = '/api/v1/categories/2/items/'

        headers = self.get_api_headers(current_app.config['USER_EMAIL'],
                                       current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 20)

    def test_10_0_create_user_and_add_item(self):
        # Register a new user via POST command
        url = '/api/v1/users/'
        headers = {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
            }
        data = {
            "data": {
                "type": "user",
                "attributes": {
                    "email": 'arjaan.buijk@gmail.com',
                    "password": "a_real_password",
                    "first_name": "Arjaan",
                    "last_name": "Buijk"
                }
            }
        }
        response = self.client().post(url,
                                      headers=headers,
                                      data=json.dumps(data))
        self.verify_response_is_201_CREATED(response)
        response_data = json.loads(response.data.decode())

        # activate the account
        # we activate it by going into the database directly...
        u = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        u.confirmed = True

        # get a token
        url = '/api/v1/token'
        headers = self.get_api_headers('arjaan.buijk@gmail.com',
                                       'a_real_password')
        response = self.client().post(url, headers=headers)
        self.verify_response_is_200_OK(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

#         # Create an item for this user in the first category
#         url = '/api/v1/itemss/'
#         headers = self.get_api_headers(token, '')
#         data = {
#             "data": {
#                 "type": "item",
#                 "attributes": {
#                     "date": '{}'.format(date(2018,1,5)),
#                     "time": '{}'.format(time(18,5,15)),
#                     "description": "TODO !!!"
#                 }
#             }
#         }
#         response = self.client().post(url,
#                                       headers=headers,
#                                       data=json.dumps(data))
#         self.verify_response_is_201_CREATED(response)
#         response_data = json.loads(response.data.decode())
#         item_id = response_data['data']['id']
#
#     def test_2_1_verify_relationships(self):
#         """POST /api/v1/items/: verify relationships"""
#         self.populate_database_with_users(num_users=4,
#                                             direct_to_db=False)
#
#         # get a token for the third user (a regular user)
#         user = self.user_data_list[2]
#         token = self.get_token(user)
#         # Create a item for the 3rd user, while sending Bearer token
#         url = '/api/v1/items/'
#         headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 'Authorization': 'Bearer {}'.format(token)
#                 }
#         data = self.item_data_list[0]  # use list without history & weather
#         response = self.client().post(url,
#                                       headers=headers,
#                                       data=json.dumps(data))
#         self.verify_response_is_201_CREATED(response)
#         response_data = json.loads(response.data.decode())
#         item_id = response_data['data']['id']
#
#         ######################################################################
#         # Make sure the relationship to the user is correct
#         # - using links: 'related'
#         url = '/api/v1/items/{}/user'.format(item_id)
#         response = self.client().get(url, headers=headers)
#         response_data = json.loads(response.data.decode())
#         user_id = '3'
#         self.assertEqual(response_data['data']['id'],user_id)
#         # - using links: 'relationships'
#         url = '/api/v1/items/{}/relationships/user'.format(item_id)
#         response = self.client().get(url, headers=headers)
#         response_data = json.loads(response.data.decode())
#         #
#         # TODO: this seems a bug in Flask-REST-API
#         #       This url, using relationships, returns the id as an int
#         #       It should always return it as a string...
#         # user_id = '3'
#         user_id = 3
#         self.assertEqual(response_data['data']['id'],user_id)
#
#
#     def test_3_0_protect_access_to_items(self):
#         """Verify permissions to access items"""
#         self.populate_database_with_users(num_users=4,
#                                             direct_to_db=False)
#
#         # get a token for the third user (a regular user)
#         user = self.user_data_list[2]
#         token = self.get_token(user)
#         # Create a item for the 3rd user, while sending Bearer token
#         url = '/api/v1/items/'
#         headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 'Authorization': 'Bearer {}'.format(token)
#                 }
#         data = self.item_data_list[0]  # use list without history & weather
#         response = self.client().post(url,
#                                       headers=headers,
#                                       data=json.dumps(data))
#         self.verify_response_is_201_CREATED(response)
#         response_data = json.loads(response.data.decode())
#         item_id = response_data['data']['id']
#
#
#     def test_3_2_protect_endpoints_if_not_logged_in(self):
#         """/api/v1/--: protect endpoints if not logged in"""
#         self.populate_database_with_users(num_users=3)
#         self.populate_database_with_items(num_users=3, num_items=1)
#
#         headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 }
#
#         # Test that all the endpoints, except registration, require a login
#         # If not logged in, it must return one of these:
#         #  401 UNAUTHORIZED
#         #  405 METHOD NOT ALLOWED
#
#         ######################################################################
#         # Test all endpoints of api
#         #
#         urls_users = []
#         urls_items = []
#         urls_weeks = []
#         urls_users.append('/api/v1/users/')  # UserList
#         urls_users.append('/api/v1/users/3')  # UserDetail
#         urls_users.append('/api/v1/items/1/user')  # UserDetail
#         #urls_items.append('/api/v1/users/1/relationships/items')
#         urls_items.append('/api/v1/items/')  # ItemList
#         urls_items.append('/api/v1/users/3/items')  # ItemList
#         urls_items.append('/api/v1/items/1')  # ItemDetail
#         #urls_users.append('/api/v1/items/1/relationships/user')
#
#         data = self.user_data_list[2]  # User with role=User
#         for url in urls_users:
#             response = self.client().get(url, headers=headers)
#             self.verify_response_is_401_or_405(response)
#
#             if url is not '/api/v1/users/':  # register while not logged in
#                 response = self.client().post(url,
#                                               headers=headers,
#                                               data=json.dumps(data))
#                 self.verify_response_is_401_or_405(response)
#
#             response = self.client().put(url,
#                                          headers=headers,
#                                          data=json.dumps(data))
#             self.verify_response_is_401_or_405(response)
#
#             response = self.client().delete(url,
#                                             headers=headers,
#                                             data=json.dumps(data))
#             self.verify_response_is_401_or_405(response)
#
#
#         data = self.item_data_list[0]
#         for url in urls_items:
#             response = self.client().get(url,
#                                          headers=headers)
#             self.verify_response_is_401_UNAUTHORIZED(response)
#
#             response = self.client().post(url,
#                                           headers=headers,
#                                           data=json.dumps(data))
#             self.verify_response_is_401_or_405(response)
#
#             response = self.client().put(url,
#                                          headers=headers,
#                                          data=json.dumps(data))
#             self.verify_response_is_401_or_405(response)
#
#             response = self.client().delete(url,
#                                             headers=headers,
#                                             data=json.dumps(data))
#             self.verify_response_is_401_or_405(response)
#
#         for url in urls_weeks:
#             response = self.client().get(url,
#                                          headers=headers)
#             self.verify_response_is_401_UNAUTHORIZED(response)
#
#             # Note that only GET is implemented for /api/v1/weeks
#
#     def test_3_3_protect_create_user_twice(self):
#         """POST /api/v1/users: API must NOT create same user twice"""
#         self.populate_database_with_users(num_users=1)
#
#         # make sure we cannot register a user with the same email twice
#         url = self.user_url
#         headers = self.user_headers
#         data = self.user_data_list[0]
#         response = self.client().post(url,
#                                       headers=headers,
#                                       data=json.dumps(data))
#         response_data = json.loads(response.data.decode())
#         self.verify_response_is_400_BAD_REQUEST(response)
#
#     def test_3_4_protect_create_user_with_missing_email(self):
#         """POST /api/v1/users: API must catch missing email"""
#         url = self.user_url
#         headers = self.user_headers
#         data = self.user_data_list[0]
#         data['data']['attributes'].pop('email')  # omit email
#         response = self.client().post(url,
#                                       headers=headers,
#                                       data=json.dumps(data))
#         response_data = json.loads(response.data.decode())
#         self.verify_response_is_400_BAD_REQUEST(response)
#
#     def test_3_5_protect_create_user_with_missing_password(self):
#         """POST /api/v1/users: API must catch missing password"""
#         url = self.user_url
#         headers = self.user_headers
#         data = self.user_data_list[0]
#         data['data']['attributes'].pop('password')  # omit password
#         response = self.client().post(url,
#                                       headers=headers,
#                                       data=json.dumps(data))
#         response_data = json.loads(response.data.decode())
#         self.verify_response_is_400_BAD_REQUEST(response)
#
#     def test_4_0_pagination(self):
#         """Test pagination"""
#         num_users = 3
#         self.populate_database_with_users(num_users=num_users,
#                                             direct_to_db=True)
#         self.populate_database_with_items(num_users=num_users,
#                                          direct_to_db=True)
#
#         # Check all is ok in the database
#         db_users = User.query.all()
#         db_items = Item.query.all()
#         db_weeks = Week.query.all()
#         self.assertEqual(len(db_users),num_users)
#         self.assertEqual(len(db_items),
#                          num_users*len(self.item_data_list_history))  # NOQA
#
#         # get a token for the third user (a regular user)
#         user = self.user_data_list[2]
#         email = user['data']['attributes']['email']
#         token = self.get_token(user)
#         headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 'Authorization': 'Bearer {}'.format(token)
#                 }
#
#         # get list of this user's items
#         url='/api/v1/users/3/items'
#         response = self.client().get(url, headers=headers)
#         self.verify_response_is_200_OK(response)
#         response_data = json.loads(response.data.decode())
#
#         # verify that data is paginated
#         self.assertTrue('first' in response_data['links'])
#         self.assertTrue('last' in response_data['links'])
#         self.assertTrue('next' in response_data['links'])
#
#     def test_5_0_filtering(self):
#         """Test filtering
#
#         The tests are based on:
#         http://flask-rest-jsonapi.readthedocs.io/en/latest/filtering.html
#         """
#         self.populate_database_with_users(direct_to_db=True)
#         self.populate_database_with_items(direct_to_db=True)
#
#         # Check all is ok in the database
#         db_users = User.query.all()
#         db_items = Item.query.all()
#         self.assertEqual(len(db_users),len(self.user_data_list))
#         self.assertEqual(len(db_items),
#                          len(self.user_data_list)*\
#                          len(self.item_data_list_history))
#
#         # get a token for the first user (an admin)
#         admin = self.user_data_list[0]
#         admin_email = admin['data']['attributes']['email']
#         admin_token = self.get_token(admin)
#         admin_headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                     'Accept': 'application/vnd.api+json',
#                     'Authorization': 'Bearer {}'.format(admin_token)
#             }
#
#         # get a token for the second user (a usermanager)
#         usermanager = self.user_data_list[1]
#         usermanager_email = usermanager['data']['attributes']['email']
#         usermanager_token = self.get_token(usermanager)
#         usermanager_headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                     'Accept': 'application/vnd.api+json',
#                     'Authorization': 'Bearer {}'.format(usermanager_token)
#             }
#
#         # get a token for the third user (a regular user)
#         user = self.user_data_list[2]
#         user_email = user['data']['attributes']['email']
#         user_token = self.get_token(user)
#         user_headers = {
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 'Authorization': 'Bearer {}'.format(user_token)
#                 }
#
#         # get user's data
#         url='/api/v1/users/3'
#         response = self.client().get(url, headers=user_headers)
#         self.verify_response_is_200_OK(response)
#         response_data = json.loads(response.data.decode())
#         # save for next checks...
#         expected_data = response_data.copy()
#         expected_data_list = []
#         expected_data_list.append(expected_data['data'])
#
#         # Get user's info via a filter object in query string
#         qs=[{"name":"email","op":"eq","val":"{}".format(user_email)}]
#         # Nasty detail: json.dumps enforces "" for parameters!
#         # Using str(qs) will not work.
#         url = '/api/v1/users?filter='+json.dumps(qs)
#         response = self.client().get(url, headers=user_headers)
#         self.assertEqual(response.status_code, 200)
#         response_data = json.loads(response.data.decode())
#         self.assertListEqual(ordered(response_data['data']),
#                              ordered(expected_data_list))
#
#         # 'or' filter on users
#         email1 = self.user_data_list[2]['data']['attributes']['email']
#         email2 = self.user_data_list[3]['data']['attributes']['email']
#         email3 = self.user_data_list[4]['data']['attributes']['email']
#         qs=[{"or":[{"name":"email","op":"eq","val":"{}".format(email1)},
#                    {"name":"email","op":"eq","val":"{}".format(email2)},
#                    {"name":"email","op":"eq","val":"{}".format(email3)}
#                    ]
#              }
#             ]
#         url = '/api/v1/users?filter='+json.dumps(qs)
#         # admin should retrieve all 3
#         response = self.client().get(url, headers=admin_headers)
#         self.assertEqual(response.status_code, 200)
#         response_data = json.loads(response.data.decode())
#         self.assertEqual(response_data['meta']['count'], 3)
#         # usermanager should also retrieve all
#         response = self.client().get(url, headers=usermanager_headers)
#         self.assertEqual(response.status_code, 200)
#         response_data = json.loads(response.data.decode())
#         self.assertEqual(response_data['meta']['count'], 3)
#         # user should only retrieve itself
#         response = self.client().get(url, headers=user_headers)
#         self.assertEqual(response.status_code, 200)
#         response_data = json.loads(response.data.decode())
#         self.assertEqual(response_data['meta']['count'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
