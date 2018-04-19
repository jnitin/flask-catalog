#!/usr/bin/env python3
import os
import sys
import unittest
from config import Config
import time
from datetime import datetime, date, time
from application import create_app
from application.user import User, AnonymousUser, Role, Permission
from application.catalog import Category, Item
from application.extensions import db
from application.extensions import api as rest_jsonapi


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In memory database

    # turn CSRF off to enable unittesting of frontend without CSRF tokens
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False


class ItemModelTestCase(unittest.TestCase):
    def setUp(self):
        # avoid error from jsonapi. See description in tests_api.py
        rest_jsonapi.resources = []

        # self.app = create_app('testing') #TODO: set up like this
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        User.insert_default_users()
        Item.insert_default_items()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_0_0_user_id(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        c = Category(name='Example Category')
        db.session.add(c)
        db.session.commit()

        b = Item(name='Example Beer',
                 description='Description goes here...',
                 user_id=u.id,
                 category_id=c.id)
        db.session.add(b)
        db.session.commit()

        self.assertEqual(b.user_id, u.id)
        self.assertEqual(b.category_id, c.id)

    def test_0_1_default_timestamp(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        c = Category(name='Example Category')
        db.session.add(c)
        db.session.commit()

        b = Item(name='Example Beer',
                 description='Description goes here...',
                 user_id=u.id,
                 category_id=c.id)
        db.session.add(b)
        db.session.commit()

        self.assertTrue(b.timestamp)

    def test_0_4_to_json(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        c = Category(name='Example Category')
        db.session.add(c)
        db.session.commit()

        b = Item(name='Example Beer',
                 description='Description goes here...',
                 user_id=u.id,
                 category_id=c.id)
        db.session.add(b)
        db.session.commit()

        with self.app.test_request_context('/'):
            json_user = u.to_json()
            # TODO
            # json_category = c.to_json()
            # json_item = b.to_json()

        expected_keys = ['url']

        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/users/' + str(u.id), json_user['url'])

#         self.assertEqual(sorted(json_category.keys()), sorted(expected_keys))
#         self.assertEqual('/api/v1/items/' + str(c.id), json_category['url'])
#
#         self.assertEqual(sorted(json_item.keys()), sorted(expected_keys))
#         self.assertEqual('/api/v1/categories/' + str(b.id), json_item['url'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
