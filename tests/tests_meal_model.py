#!/usr/bin/env python3
# to get access to application/*.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from config import Config
import time
from datetime import datetime, date, time
from application import create_app
from application.user import User, AnonymousUser, Role, Permission
from application.meal import Meal, Day, get_calories_from_nutritionix
from application.extensions import db
from application.extensions import api as rest_jsonapi

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In memory database

    # turn CSRF off to enable unittesting of frontend without CSRF tokens
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False

class MealModelTestCase(unittest.TestCase):
    def setUp(self):
        # avoid error from jsonapi. See description in tests_api.py
        rest_jsonapi.resources = []

        #self.app = create_app('testing') #TODO: set up like this
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


    def test_0_0_user_id(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        m = Meal(calories=365,description='French fries', user_id=u.id)
        db.session.add(m)
        db.session.commit()

        m.add_meal_to_day()
        db.session.commit()

        self.assertEqual(m.user_id, u.id)
        self.assertEqual(u.days[0].user_id, u.id)

    def test_0_1_default_date_and_time(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        m = Meal(calories=365,description='French fries', user_id=u.id)
        db.session.add(m)
        db.session.commit()

        self.assertTrue(m.timestamp)
        self.assertTrue(m.date)
        self.assertTrue(m.time)


    def test_0_2_nutritionix(self):
        cals = get_calories_from_nutritionix('Potatoes, a Veggie Patty '
                                             'and a Milk')
        self.assertAlmostEqual(cals, 409.73999999999995)

        # test a bogus description
        cals = get_calories_from_nutritionix('Scissors')
        self.assertAlmostEqual(cals, 0)


    def test_0_3_calories_from_description(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        meal_date = date(2018, 2, 1)
        meal_time = time(18, 5, 10)
        m = Meal(description='French fries',
                 date = meal_date,
                 time = meal_time,
                 user_id=u.id)
        db.session.add(m)
        db.session.commit()

        m.set_calories_from_description()

        # check calories for this meal
        self.assertAlmostEqual(m.calories, 365.04)

        # check total calories for the Day of the meal
        d = Day.query.filter_by(user_id=u.id,
                                date=m.date).first()
        self.assertTrue(d)
        self.assertEqual(d,u.days[0])
        self.assertEqual(d.calories, m.calories)


    def test_0_4_to_json(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        m = Meal(calories=365,description='French fries', user_id=u.id)
        db.session.add(m)
        db.session.commit()

        m.add_meal_to_day()
        db.session.commit()

        d = u.days[0]  # the day where it was accumulated

        with self.app.test_request_context('/'):
            json_user = u.to_json()
            json_meal = m.to_json()
            json_day = d.to_json()

        expected_keys = ['url']

        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/users/' + str(u.id), json_user['url'])

        self.assertEqual(sorted(json_meal.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/meals/' + str(m.id), json_meal['url'])

        self.assertEqual(sorted(json_day.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/days/' + str(d.id), json_day['url'])

if __name__ == '__main__':
    unittest.main(verbosity=2)

