#!/usr/bin/env python3
"""Unit tests for catalog blueprint"""
import unittest
from test.setup_and_teardown import my_setup, my_teardown
from application.user import User
from application.catalog import Category, Item
from application.extensions import db

class ItemModelTestCase(unittest.TestCase):
    """Unit tests for Category and Item Models"""
    def setUp(self):
        my_setup(self)

    def tearDown(self):
        my_teardown(self)

    def test_0_0_add(self):
        """Test adding a category and an item"""
        usr = User(email='john@example.com', password='cat')
        db.session.add(usr)
        db.session.commit()

        cat = Category(name='Example Category')
        db.session.add(cat)
        db.session.commit()

        itm = Item(name='Example Beer',
                   description='Description goes here...',
                   user_id=usr.id,
                   category_id=cat.id)
        db.session.add(itm)
        db.session.commit()

        self.assertEqual(itm.user_id, usr.id)
        self.assertEqual(itm.category_id, cat.id)
        self.assertTrue(itm.timestamp)


if __name__ == '__main__':
    unittest.main(verbosity=2)
