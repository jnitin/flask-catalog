from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

class UserSchema(Schema):
    """Flask-REST-JSONAPI: Create logical data abstraction for User model"""
    class Meta:
        type_ = 'user'
        self_view = 'api.user_detail'   # Note: For usage of api.user_details see this discussion:
                                                # https://github.com/miLibris/flask-rest-jsonapi/issues/35
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'api.user_list'


    id = fields.Integer(as_string=True, dump_only=True)
    email = fields.Email(load_only=True)
    password = fields.Str(load_only=True)
    first_name = fields.Str()
    last_name = fields.Str()

    # Extra: a nicely formatted display name
    display_name = fields.Function(lambda obj: "{} {} <{}>".format(
        obj.first_name.upper(), obj.last_name.upper(), obj.email))
    # Extra: a message
    a_message = fields.Function(lambda obj: None if obj.confirmed else 'Please check your email to activate your account.')

    # profile pic
    profile_pic = fields.Str(load_only=True)
    profile_pic_filename = fields.Str(load_only=True)
    profile_pic_url = fields.Str()

    daily_calories_target = fields.Float()

    meals = Relationship(self_view='api.user_meals',
                         self_view_kwargs={'id': '<id>'},
                         related_view='api.meal_list',
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         schema='MealSchema',
                         type_='meal')

    days = Relationship(self_view='api.user_days',
                         self_view_kwargs={'id': '<id>'},
                         related_view='api.day_list',
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         schema='DaySchema',
                         type_='day')
