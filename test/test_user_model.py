#!/usr/bin/env python3
import os
import sys
import unittest
from config import Config
import time
from datetime import datetime
from application import create_app
from application.user import User, AnonymousUser, Role, Permission
from application.extensions import db
from application.extensions import api as rest_jsonapi


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In memory database

    # turn CSRF off to enable unittesting of frontend without CSRF tokens
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        # avoid error from jsonapi. See description in tests_api.py
        rest_jsonapi.resources = []

#         self.app = create_app('testing') #TODO: set up like this
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        User.insert_default_users()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_password_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_password_token()
        self.assertEqual(User.verify_reset_password_token(token), u)

    def test_invalid_reset_password_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_password_token()
        self.assertIsNone(User.verify_reset_password_token(token + 'a'))

    def test_expired_reset_password_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_password_token(1)
        time.sleep(2)
        self.assertIsNone(User.verify_reset_password_token(token))

    def test_valid_email_change_token(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_valid_invitation_token(self):
        user_email = 'john@example.com'
        token = User.generate_invitation_token(user_email)
        self.assertEqual(User.email_from_invitation_token(token),
                         user_email)

    def test_invalid_invitation_token(self):
        user_email1 = 'john@example.com'
        user_email2 = 'susan@example.org'
        token = User.generate_invitation_token(user_email1)
        self.assertNotEqual(User.email_from_invitation_token(token),
                            user_email2)

    def test_expired_invitation_token(self):
        user_email = 'john@example.com'
        token = User.generate_invitation_token(user_email, 1)
        time.sleep(2)
        self.assertFalse(User.email_from_invitation_token(token),
                         user_email)

    def test_user_role(self):
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.CRUD_OWNED))
        self.assertFalse(u.can(Permission.CRUD_USERS))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_usermanager_role(self):
        r = Role.query.filter_by(name='Usermanager').first()
        u = User(email='john@example.com', password='cat')
        u.role = r
        self.assertTrue(u.can(Permission.CRUD_OWNED))
        self.assertTrue(u.can(Permission.CRUD_USERS))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='john@example.com', password='cat')
        u.role = r
        self.assertTrue(u.can(Permission.CRUD_OWNED))
        self.assertTrue(u.can(Permission.CRUD_USERS))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.CRUD_OWNED))
        self.assertFalse(u.can(Permission.CRUD_USERS))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_to_json(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        with self.app.test_request_context('/'):
            json_user = u.to_json()
        expected_keys = ['url']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/users/' + str(u.id), json_user['url'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
