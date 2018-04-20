#!/usr/bin/env python3
"""Unit tests for user blueprint"""
import unittest
import time
from test.setup_and_teardown import my_setup, my_teardown
from application.user import User, AnonymousUser, Role, Permission
from application.extensions import db


class UserModelTestCase(unittest.TestCase):
    """Unit tests for User Model"""
    # pylint: disable=too-many-public-methods
    def setUp(self):
        my_setup(self)

    def tearDown(self):
        my_teardown(self)

    def test_password_setter(self):
        """Test that password setter creates a password hash"""
        usr = User(password='cat')
        self.assertTrue(usr.password_hash is not None)

    def test_no_password_getter(self):
        """Test that trying to retrieve the password raises error"""
        usr = User(password='cat')
        with self.assertRaises(AttributeError):
            usr.password  # pylint: disable=W0104

    def test_password_verification(self):
        """Test verify_password method"""
        usr = User(password='cat')
        self.assertTrue(usr.verify_password('cat'))
        self.assertFalse(usr.verify_password('dog'))

    def test_password_salts_are_random(self):
        """Test that password hashes are always different due to salting"""
        usr = User(password='cat')
        usr2 = User(password='cat')
        self.assertTrue(usr.password_hash != usr2.password_hash)

    def test_valid_confirmation_token(self):
        """Test a valid email confirmation token"""
        usr = User(password='cat')
        db.session.add(usr)
        db.session.commit()
        token = usr.generate_confirmation_token()
        self.assertTrue(usr.confirm(token))

    def test_invalid_confirmation_token(self):
        """Test that a wrongly created email confirmation token fails"""
        usr1 = User(password='cat')
        usr2 = User(password='dog')
        db.session.add(usr1)
        db.session.add(usr2)
        db.session.commit()
        token = usr1.generate_confirmation_token()
        self.assertFalse(usr2.confirm(token))

    def test_expired_confirmation_token(self):
        """Test that an expired email confirmation token fails"""
        usr = User(password='cat')
        db.session.add(usr)
        db.session.commit()
        token = usr.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(usr.confirm(token))

    def test_valid_reset_pw_token(self):
        """Test a valid reset password token"""
        usr = User(password='cat')
        db.session.add(usr)
        db.session.commit()
        token = usr.generate_reset_password_token()
        self.assertEqual(User.verify_reset_password_token(token), usr)

    def test_invalid_reset_pw_token(self):
        """Test that a wrongly created reset password token fails"""
        usr = User(password='cat')
        db.session.add(usr)
        db.session.commit()
        token = usr.generate_reset_password_token()
        self.assertIsNone(User.verify_reset_password_token(token + 'a'))

    def test_expired_reset_pw_token(self):
        """Test that an expired reset password token fails"""
        usr = User(password='cat')
        db.session.add(usr)
        db.session.commit()
        token = usr.generate_reset_password_token(1)
        time.sleep(2)
        self.assertIsNone(User.verify_reset_password_token(token))

    def test_valid_email_change_token(self):
        """Test a valid email change token"""
        usr = User(email='john@example.com', password='cat')
        db.session.add(usr)
        db.session.commit()
        token = usr.generate_email_change_token('susan@example.org')
        self.assertTrue(usr.change_email(token))
        self.assertTrue(usr.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        """Test that an email change token for non-existing user fails"""
        usr1 = User(email='john@example.com', password='cat')
        usr2 = User(email='susan@example.org', password='dog')
        db.session.add(usr1)
        db.session.add(usr2)
        db.session.commit()
        token = usr1.generate_email_change_token('david@example.net')
        self.assertFalse(usr2.change_email(token))
        self.assertTrue(usr2.email == 'susan@example.org')

    def test_wrong_email_change_token(self):
        """Test that a email change token from another user fails"""
        usr1 = User(email='john@example.com', password='cat')
        usr2 = User(email='susan@example.org', password='dog')
        db.session.add(usr1)
        db.session.add(usr2)
        db.session.commit()
        token = usr2.generate_email_change_token('john@example.com')
        self.assertFalse(usr2.change_email(token))
        self.assertTrue(usr2.email == 'susan@example.org')

    def test_valid_invitation_token(self):
        """Test a valid invitation token"""
        user_email = 'john@example.com'
        token = User.generate_invitation_token(user_email)
        self.assertEqual(User.email_from_invitation_token(token),
                         user_email)

    def test_invalid_invitation_token(self):
        """Test that a invitation token from another user fails"""
        user_email1 = 'john@example.com'
        user_email2 = 'susan@example.org'
        token = User.generate_invitation_token(user_email1)
        self.assertNotEqual(User.email_from_invitation_token(token),
                            user_email2)

    def test_expired_invitation_token(self):
        """Test that an expired invitation token fails"""
        user_email = 'john@example.com'
        token = User.generate_invitation_token(user_email, 1)
        time.sleep(2)
        self.assertFalse(User.email_from_invitation_token(token),
                         user_email)

    def test_user_role(self):
        """Test CRUD permissions of regular user"""
        usr = User(email='john@example.com', password='cat')
        self.assertTrue(usr.can(Permission.CRUD_OWNED))
        self.assertFalse(usr.can(Permission.CRUD_USERS))
        self.assertFalse(usr.can(Permission.ADMIN))

    def test_usermanager_role(self):
        """Test CRUD permissions of manager"""
        role = Role.query.filter_by(name='Usermanager').first()
        usr = User(email='john@example.com', password='cat')
        usr.role = role
        self.assertTrue(usr.can(Permission.CRUD_OWNED))
        self.assertTrue(usr.can(Permission.CRUD_USERS))
        self.assertFalse(usr.can(Permission.ADMIN))

    def test_administrator_role(self):
        """Test CRUD permissions of administrator"""
        role = Role.query.filter_by(name='Administrator').first()
        usr = User(email='john@example.com', password='cat')
        usr.role = role
        self.assertTrue(usr.can(Permission.CRUD_OWNED))
        self.assertTrue(usr.can(Permission.CRUD_USERS))
        self.assertTrue(usr.can(Permission.ADMIN))

    def test_anonymous_user(self):
        """Test CRUD permissions of anonymous (i.e. not logged in) user"""
        usr = AnonymousUser()
        self.assertFalse(usr.can(Permission.CRUD_OWNED))
        self.assertFalse(usr.can(Permission.CRUD_USERS))
        self.assertFalse(usr.can(Permission.ADMIN))


if __name__ == '__main__':
    unittest.main(verbosity=2)
