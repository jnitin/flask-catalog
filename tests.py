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

    def login(self, username, password):
        data = {
            'login': username,
            'password': password,
        }
        response = self.client.post('/login', data=data, follow_redirects=True)
        assert "Logged in" in response.data.decode()
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
        self._test_get_request('/register', 'frontend/register.html')

        data = {
            'email': 'new_user@example.com',
            'password': '123456',
            'name': 'new_user',
            'agree': True,
        }
        response = self.client.post('/signup', data=data, follow_redirects=True)
        assert "Signed up" in response.data.decode()
        new_user = User.query.filter_by(email=data['email']).first()
        assert new_user.name == "new_user"

    def test_3_login(self):
        self._test_get_request('/login', 'frontend/login.html')

        response = self.client.post('/login', data={
            'login': "demo@example.com",
            'password': "123456"}, follow_redirects=True)
        assert "Logged in" in response.data.decode()

    def test_4_logout(self):
        self.login("demo@example.com", "123456")
        self._logout()


class TestAPI(BaseTestCase):

    def test_1_2_get_token(self):
        """POST /api/v1/tokens: API must return a token"""

        email = "demo@example.com"
        password = "123456"
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
