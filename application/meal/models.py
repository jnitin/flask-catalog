from sqlalchemy import Column, desc
from sqlalchemy.orm import backref
from flask import current_app, g, url_for
from flask_login import UserMixin, AnonymousUserMixin
from . import get_calories_from_nutritionix
from ..extensions import db, login_manager, bcrypt
from ..user import User
import os
import base64
from datetime import datetime, date, time


class Meal(db.Model):

    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date = db.Column(db.Date, index=True, default=date(datetime.utcnow().year,
                                                       datetime.utcnow().month,
                                                       datetime.utcnow().day))
    time = db.Column(db.Time, index=True,
                     default=time(datetime.utcnow().hour,
                                  datetime.utcnow().minute,
                                  datetime.utcnow().second))
    description = db.Column(db.String(96))
    calories = db.Column(db.Float, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('meals'))

    day_id = db.Column(db.Integer, db.ForeignKey('days.id'))
    day = db.relationship('Day', backref=db.backref('meals'))

    def set_calories_from_description(self):
        """Set the calories of this meal based on data from nutritionix."""

        meal_calories = get_calories_from_nutritionix(self.description)
        if meal_calories > 0:
            self.calories = meal_calories
            db.session.commit()
            self.add_meal_to_day()


    def add_meal_to_day(self):
        """Add this meal to the daily totals tracked in the day table.

        If an entry in day table does not yet exists, it will first create it.

        Returns:
            the entry in the day table
        """
        #
        # check if this date is already tracked for this user
        #
        d = Day.query.filter_by(user_id=self.user_id,
                                date=self.date).first()
        if d is None:
            d = Day(user_id=self.user_id,
                    date=self.date)
            db.session.add(d)
            db.session.commit()

        d.update_daily_count(self.calories)
        #d.calories += self.calories
        #db.session.commit()

        #d.check_daily_target()

        return d

    def remove_meal_from_day(self):
        """Subtract calories of this meal from daily totals in the day table.

        Returns:
            the entry in the day table, or None if it does not exist
        """
        #
        # check if this date is tracked for this user
        #
        d = Day.query.filter_by(user_id=self.user_id,
                                date=self.date).first()
        if d is not None:
            d.update_daily_count(-self.calories)
            #d.calories -= self.calories
            #db.session.commit()

        return d

    def to_json(self):
        json_meal = {
                'url': url_for('api.meal_detail', id=self.id)
            }
        return json_meal

class Day(db.Model):
    """Table to store data for calculating totals per day."""

    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    calories = db.Column(db.Integer, default=0)
    below_daily_max = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('days'))


    def update_daily_count(self, new_calories):
        """Update daily calorie count and
        check if the total calories for this day are below user's target"""
        self.calories += new_calories

        u = User.query.filter_by(id=self.user_id).first()
        if u:
            if self.calories < u.daily_calories_target:
                self.below_daily_max = True
            else:
                self.below_daily_max = False

        db.session.commit()

    def to_json(self):
        json_day = {
                'url': url_for('api.day_detail', id=self.id)
            }
        return json_day

