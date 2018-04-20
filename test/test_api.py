"""Unit tests for api"""
import unittest
import json
from base64 import b64encode
from test.utils import pprint_response
from test.setup_and_teardown import my_setup, my_teardown
from flask import current_app
from flask_uploads import FileStorage
from application.user import User, Role
from application.extensions import db



def get_api_headers(email, password):
    """Creates the headers for an HTTP request using email & password, with:

    'Content-Type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json'
    """
    return {
        'Authorization': 'Basic ' + b64encode(
            (email + ':' + password).encode('utf-8')).decode('utf-8'),
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/vnd.api+json'
    }


def get_api_headers_multiform(email, password):
    """Creates the headers for an HTTP request using email & password, with:

    'Content-Type': 'multipart/form-data',
    'Accept': 'application/vnd.api+json'

    This type of header is used when uploading images.
    """
    return {
        'Authorization': 'Basic ' + b64encode(
            (email + ':' + password).encode('utf-8')).decode('utf-8'),
        'Content-Type': 'multipart/form-data',
        'Accept': 'application/vnd.api+json'
    }


class APITestCase(unittest.TestCase):
    """Unit tests for the REST API"""
    # pylint: disable=too-many-public-methods
    def setUp(self):
        my_setup(self)
        # reference the test client
        self.client = self.client

    def tearDown(self):
        my_teardown(self)

    def is_200_ok(self, response):
        """Verifies that the response status code=200"""
        self.assertEqual(response.status_code, 200)

    def is_201_created(self, response):
        """Verifies that the response status code=201"""
        self.assertEqual(response.status_code, 201)

    def is_400_bad_request(self, response):
        """Verifies that the response status code=400"""
        self.assertEqual(response.status_code, 400)

    def is_401_unauthorized(self, response):
        """Verifies that the response status code=401"""
        self.assertEqual(response.status_code, 401)

    def is_403_forbidden(self, response):
        """Verifies that the response status code=403"""
        self.assertEqual(response.status_code, 403)

    def is_404_not_found(self, response):
        """Verifies that the response status code=404"""
        self.assertEqual(response.status_code, 404)

    def is_405_method_not_allowed(self, response):
        """Verifies that the response status code=405"""
        self.assertEqual(response.status_code, 405)

    def verify_response_is_401_or_405(self, response):
        """Verifies that the response status code=401 or 405"""
        self.assertTrue(response.status_code == 401 or
                        response.status_code == 405)

    ##########################################################################
    def test_0_0_404(self):
        """Test that requesting a non-existing url returns status code 404"""
        url = '/api/v1/wrong/url'
        headers = get_api_headers('email', 'password')
        response = self.client().get(url, headers=headers)
        self.is_404_not_found(response)
        # Note: we need to get a JSON response back !
        # Right now, it returns an HTML page
        # Implement an error handler
        # json_response = json.loads(response.get_data(as_text=True))
        # self.assertEqual(json_response['error'], 'not found')

    def test_0_1_no_auth(self):
        """Test that requests without authentication return code 401"""
        url = '/api/v1/users/'
        response = self.client().get(url,
                                     content_type='application/json')
        self.is_401_unauthorized(response)

        # NOTE: we must be able to register a new user without auth,
        # but that is tested below

    def test_0_2_bad_auth(self):
        """Test that requests without wrong authentication return code 401"""
        # add a user
        role = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(role)
        usr = User(email='john@example.com', password='cat', confirmed=True,
                   role=role)
        db.session.add(usr)
        db.session.commit()

        # authenticate with bad password
        url = '/api/v1/users/{}'.format(usr.id)
        headers = get_api_headers('john@example.com', 'dog')
        response = self.client().get(url, headers=headers)
        self.is_401_unauthorized(response)

    def test_0_3_token_auth(self):
        """Test that a token is only provided after correct authentication"""
        # add a confirmed
        role = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(role)
        usr = User(email='john@example.com', password='cat', confirmed=True,
                   role=role)
        db.session.add(usr)
        db.session.commit()

        # issue a request with a bad token
        url = '/api/v1/users/{}'.format(usr.id)
        headers = get_api_headers('bad-token', '')
        response = self.client().get(url, headers=headers)
        self.is_401_unauthorized(response)

        # get a token
        url = '/api/v1/token'
        headers = get_api_headers('john@example.com', 'cat')
        response = self.client().post(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        url = '/api/v1/users/{}'.format(usr.id)
        headers = get_api_headers(token, '')
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)

    def test_0_4_anonymous(self):
        """Test that requests without authentication header of anonymous user
        return code 401
        """
        url = '/api/v1/users/'
        headers = get_api_headers('', '')
        response = self.client().get(url, headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_0_5_unconfirmed_account(self):
        """Test that a token is only provided for accounts with confirmed
        email.
        """
        # add an unconfirmed user
        role = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(role)
        usr = User(email='john@example.com', password='cat', confirmed=False,
                   role=role)
        db.session.add(usr)
        db.session.commit()

        # get user info with the unconfirmed account
        url = '/api/v1/users/{}'.format(usr.id)
        headers = get_api_headers('john@example.com', 'cat')
        response = self.client().get(url, headers=headers)
        self.is_403_forbidden(response)

        # get a token with the unconfirmed account
        url = '/api/v1/token'
        headers = get_api_headers('john@example.com', 'cat')
        response = self.client().post(url, headers=headers)
        self.is_403_forbidden(response)

    def test_0_6_routes_info(self, print_routes=True):
        """As admin, Get all the available routes, for debug purposes"""
        url = '/api/v1/help'
        headers = get_api_headers(current_app.config['ADMIN_EMAIL'],
                                  current_app.config['ADMIN_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        if print_routes:
            pprint_response(response)

    def test_0_6_routes_info_again(self):
        """Get all the available routes again, to check that the
        rest_jsonapi.resources are reset properly from previous unittest"""
        self.test_0_6_routes_info(print_routes=False)


    def test_1_3_invite(self):
        """Test that an admin and only an admin can invite users to join"""
        # An admin can invite a new user to join
        url = '/api/v1/invite/arjaan.buijk@gmail.com'
        headers = get_api_headers(current_app.config['ADMIN_EMAIL'],
                                  current_app.config['ADMIN_PW'])
        response = self.client().post(url, headers=headers)
        self.is_201_created(response)

        # A Usermanager can not invite a new user to join
        url = '/api/v1/invite/arjaan.buijk@gmail.com'
        headers = get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                  current_app.config['USERMANAGER_PW'])
        response = self.client().post(url, headers=headers)
        self.is_403_forbidden(response)

        # A User can not invite a new user to join
        url = '/api/v1/invite/arjaan.buijk@gmail.com'
        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().post(url, headers=headers)
        self.is_403_forbidden(response)

    def test_1_4_register(self):
        """Test typical scenario of user registration, confirmation and
        token retrieval.
        """
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
        self.is_201_created(response)
#         response_data = json.loads(response.data.decode())

        # get a token
        url = '/api/v1/token'
        headers = get_api_headers('arjaan.buijk@gmail.com',
                                  'a_real_password')

        # verify that when email is not yet confirmed, user cannot login or
        # receive a token
        response = self.client().post(url, headers=headers)
        self.is_403_forbidden(response)

        # activate the account
        # we activate it by going into the database directly...
        usr = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        usr.confirmed = True

        # now we can get a token
        response = self.client().post(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        url = '/api/v1/users/{}'.format(usr.id)
        headers = get_api_headers(token, '')
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)

    def test_1_5_upload_profile_pic(self):
        """Test that a user can upload and retrieve a profile picture."""
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
        self.is_201_created(response)
#         response_data = json.loads(response.data.decode())

        # activate the account
        # we activate it by going into the database directly...
        usr = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        usr.confirmed = True

        # get a token
        url = '/api/v1/token'
        headers = get_api_headers('arjaan.buijk@gmail.com',
                                  'a_real_password')
        response = self.client().post(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # upload a profile picture, using multipart/form-data type request
        url = '/api/v1/profile_pic'
        headers = get_api_headers_multiform(token, '')
        with open('test_profile_pic.gif', 'rb') as file:
            file_storage = FileStorage(file)
            data = {"profile_pic": file_storage}
            response = self.client().post(url,
                                          headers=headers,
                                          data=data)
            self.is_201_created(response)
#             response_data = json.loads(response.data.decode())

        # retrieve the profile picture
        url = '/api/v1/profile_pic'
        headers = get_api_headers_multiform(token, '')
        response = self.client().get(url,
                                     headers=headers)
        self.is_200_ok(response)

    def test_1_6_block_account(self):
        """Test that user account is blocked after 3 consecutive failed login
        attempts. Furthermore test that user cannot re-register, and that only
        an admin or usermanager can unblock the account.
        """
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
        self.is_201_created(response)
#         response_data = json.loads(response.data.decode())

        # activate the account
        # we activate it by going into the database directly...
        usr = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        usr.confirmed = True
        # Get token 3 times with wrong password, after which account is blocked
        url = '/api/v1/token'
        headers = get_api_headers('arjaan.buijk@gmail.com',
                                  'a_wrong_password')
        for _ in range(2):
            response = self.client().post(url, headers=headers)
            self.is_401_unauthorized(response)

        # Verify that on 3rd and following attempts the account is blocked
        for _ in range(2):
            response = self.client().post(url, headers=headers)
            self.is_403_forbidden(response)

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
        self.is_403_forbidden(response)

        # Verify I cannot unblock myself
        url = '/api/v1/users/{}/unblock'.format(usr.id)
        headers = get_api_headers('arjaan.buijk@gmail.com',
                                  'a_real_password')
        response = self.client().post(url, headers=headers)
        self.is_403_forbidden(response)

        # An admin can unblock the account
        url = '/api/v1/users/{}/unblock'.format(usr.id)
        headers = get_api_headers(current_app.config['ADMIN_EMAIL'],
                                  current_app.config['ADMIN_PW'])
        response = self.client().post(url, headers=headers)
        self.is_201_created(response)
        self.assertFalse(usr.blocked)
        self.assertEqual(usr.failed_logins, 0)

        # block it again, and test that usermanager can unblock it
        usr.failed_logins = 3
        usr.blocked = True
        url = '/api/v1/users/{}/unblock'.format(usr.id)
        headers = get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                  current_app.config['USERMANAGER_PW'])
        response = self.client().post(url, headers=headers)
        self.is_201_created(response)
        self.assertFalse(usr.blocked)
        self.assertEqual(usr.failed_logins, 0)

    def test_2_0_get_users(self):
        """Test retrieval of all users, and verify permissions of admin,
        usermanager and user.
        """
        url = '/api/v1/users/'

        # admin can retrieve all 3 users
        headers = get_api_headers(current_app.config['ADMIN_EMAIL'],
                                  current_app.config['ADMIN_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 3)

        # manager can retrieve all 3 users
        headers = get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                  current_app.config['USERMANAGER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 3)

        # user can retrieve only self
        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 1)

    def test_2_1_get_user_by_id(self):
        """Test retrieval of a user by it's ID, and verify permissions of
        admin, usermanager and user.
        """
        url = '/api/v1/users/3'

        # admin can retrieve details of any user
        headers = get_api_headers(current_app.config['ADMIN_EMAIL'],
                                  current_app.config['ADMIN_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
#         json_response = json.loads(response.get_data(as_text=True))

        # manager can retrieve details of any user
        headers = get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                  current_app.config['USERMANAGER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
#         json_response = json.loads(response.get_data(as_text=True))

        # user can retrieve details of self only
        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
#         json_response = json.loads(response.get_data(as_text=True))

        url = '/api/v1/users/2'
        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_403_forbidden(response)

    def test_2_2_get_user_by_cat_id(self):
        """Test retrieval of the user who owns a category"""
        url = '/api/v1/categories/1/user'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '3')

    def test_2_3_get_user_by_item_id(self):
        """Test retrieval of the user who owns an item"""
        url = '/api/v1/items/1/user'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '3')

    def test_3_0_get_categories(self):
        """Test retrieval of all categories. No permission control is
        applied to this.
        """
        url = '/api/v1/categories/'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 2)

    def test_3_1_get_category_by_id(self):
        """Test retrieval of a category by ID. No permission control is
        applied to this.
        """
        url = '/api/v1/categories/2'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '2')

    def test_3_2_get_categories_of_user(self):
        """Test retrieval of all categories that belong to a certain user"""
        url = '/api/v1/users/3/categories/'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 2)

    def test_4_0_get_items(self):
        """Test retrieval of all items. No permission control is
        applied to this.
        """
        url = '/api/v1/items/'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 40)

    def test_4_1_get_item_by_id(self):
        """Test retrieval of an item by ID. No permission control is
        applied to this.
        """
        url = '/api/v1/items/21'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['data']['id'], '21')

    def test_4_2_get_items_of_user(self):
        """Test retrieval of all items that belong to a certain user"""
        url = '/api/v1/users/3/items/'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 40)

        url = '/api/v1/users/2/items/'

        headers = get_api_headers(current_app.config['USERMANAGER_EMAIL'],
                                  current_app.config['USERMANAGER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 0)

    def test_4_3_get_items_of_category(self):
        """Test retrieval of all categories that belong to a certain
        category
        """
        url = '/api/v1/categories/2/items/'

        headers = get_api_headers(current_app.config['USER_EMAIL'],
                                  current_app.config['USER_PW'])
        response = self.client().get(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['meta']['count'], 20)

    def test_10_0_post_user(self):
        """Test registration of a new user via a POST request."""
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
        self.is_201_created(response)
#         response_data = json.loads(response.data.decode())

        # activate the account
        # we activate it by going into the database directly...
        usr = User.query.filter_by(email='arjaan.buijk@gmail.com').one()
        usr.confirmed = True

        # get a token
        url = '/api/v1/token'
        headers = get_api_headers('arjaan.buijk@gmail.com',
                                  'a_real_password')
        response = self.client().post(url, headers=headers)
        self.is_200_ok(response)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
#         token = json_response['token']


if __name__ == '__main__':
    unittest.main(verbosity=2)
