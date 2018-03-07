import unittest
from config import Config
from flask_testing import TestCase
from application import create_app
from application.user import User
from application.extensions import db
from base64 import b64encode
import json


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In memory database

    # turn CSRF off to enable unittesting without sending CSRF tokens
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False

class BaseTestCase(TestCase):

    def create_app(self):
        app = create_app(TestConfig)
        return app

    def init_data(self):
        u = User(email='ab1@c.com',
                 password='ab1',
                 name='a1 b1',)
        db.session.add(u)
        db.session.commit()

    def setUp(self):
        """Reset all tables before testing."""

        db.create_all()
        self.init_data()

    def tearDown(self):
        """Clean db session and drop all tables."""

        db.session.remove()
        db.drop_all()

    def login(self, email, password, name):
        data = {
            'email': email,
            'password': password,
            'name': name
        }
        response = self.client.post('/login', data=data, follow_redirects=True)
        assert name in response.data.decode()
        return response

    def _logout(self):
        response = self.client.get('/logout')
        self.assertRedirects(response, location='/')

    def _test_get_request(self, endpoint, template=None):
        response = self.client.get(endpoint)
        self.assert_200(response)
        if template:
            self.assertTemplateUsed(name=template)
        return response


class TestFrontend(BaseTestCase):

    def test_1_index(self):
        self._test_get_request('/', 'index.html')

    def test_2_register(self):
        self._test_get_request('/register', 'auth/register.html')

        data = {
            'email': 'ab2@c.com',
            'password': 'ab2',
            'name': 'a2 b2',
            'agree': True,
        }
        response = self.client.post('/register', data=data, follow_redirects=True)
        assert "Registration successful" in response.data.decode()
        new_user = User.query.filter_by(email=data['email']).first()
        assert new_user.name == "a2 b2"

    def test_3_login(self):
        self._test_get_request('/login', 'auth/login.html')

        response = self.client.post('/login', data={
            'email': "ab1@c.com",
            'password': "ab1"}, follow_redirects=True)
        assert "a1 b1" in response.data.decode()

    def test_4_logout(self):
        self.login("ab1@c.com", "ab1", "a1 b1")
        self._logout()


class TestAPI(BaseTestCase):

    def test_1_2_get_token(self):
        """POST /api/v1/tokens: API must return a token"""

        email = "ab1@c.com"
        password = "ab1"
        url = '/api/v1/tokens'
        headers = {
            'Content-Length': 0,
            'Authorization': 'Basic ' +  b64encode("{0}:{1}".format(
            email,password).encode('utf-8')).decode(),
            'Content-Type': 'application/json'
                }
        response = self.client.post(url,headers=headers)
        self.assert200(response)
        token = json.loads(response.data.decode())['token']
        self.assertEqual(len(token), 32)


if __name__ == '__main__':
    unittest.main(verbosity=2)
