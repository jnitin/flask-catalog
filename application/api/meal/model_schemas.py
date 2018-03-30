from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from ...meal import Meal, Day

class MealSchema(Schema):
    """Flask-REST-JSONAPI: Create logical data abstraction for Meal model"""
    class Meta:
        type_ = 'meal'
        self_view = 'api.meal_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'api.meal_list'

    id = fields.Integer(as_string=True, dump_only=True)
    timestamp = fields.DateTime()
    date = fields.Date()
    time = fields.Time()
    description = fields.Str()
    calories = fields.Float()
    calories_daily_total = fields.Method("get_daily_total")
    calories_daily_target = fields.Method("get_daily_target")
    below_daily_max = fields.Method("check_below_daily_max")

    def get_daily_total(self, obj):
        day = Day.query.filter_by(date=obj.date).one()
        return day.calories

    def get_daily_target(self, obj):
        return obj.user.daily_calories_target

    def check_below_daily_max(self, obj):
        day = Day.query.filter_by(date=obj.date).one()
        return day.below_daily_max

    user = Relationship(attribute='user',
                        self_view='api.meal_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='api.user_detail',
                        related_view_kwargs={'meal_id': '<id>'},
                        schema='UserSchema',
                        type_='user')

    day = Relationship(attribute='day',
                       self_view='api.meal_day',
                       self_view_kwargs={'id': '<id>'},
                       related_view='api.day_detail',
                       related_view_kwargs={'meal_id': '<id>'},
                       schema='DaySchema',
                       type_='day')


class DaySchema(Schema):
    """Flask-REST-JSONAPI: Create logical data abstraction for Day model"""
    class Meta:
        type_ = 'day'
        self_view = 'api.day_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'api.day_list'

    id = fields.Integer(as_string=True, dump_only=True)
    date = fields.Date()
    calories = fields.Float()
    below_daily_max = fields.Boolean()

    user = Relationship(attribute='user',
                        self_view='api.day_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='api.user_detail',
                        related_view_kwargs={'day_id': '<id>'},
                        schema='UserSchema',
                        type_='user')


    meals = Relationship(self_view='api.day_meals',
                         self_view_kwargs={'id': '<id>'},
                         related_view='api.meal_list',
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         schema='MealSchema',
                         type_='meal')
