from . import MealSchema, DaySchema
from .. import api as api_blueprint
from ...user import User, Role, Permission
from ...meal import Meal, Day, get_calories_from_nutritionix
from ...decorators import admin_required, usermanager_required
from ...email import send_confirmation_email, send_invitation_email
from ...extensions import db, login_manager, images
from ...extensions import api as rest_jsonapi

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import JsonApiException, ObjectNotFound, \
     BadRequest
from werkzeug.http import HTTP_STATUS_CODES
from sqlalchemy.orm.exc import NoResultFound

from flask import current_app, g, request, send_from_directory, jsonify, url_for

def find_user_by_meal_id(meal_id):
    try:
        meal = Meal.query.filter_by(id=meal_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'meal_id'},
                             "Meal: {} not found".format(meal_id))
    else:
        if meal.user is not None:
            if (g.current_user.is_administrator() or
                meal.user == g.current_user):
                return meal.user
            else:
                # Unauthorized
                raise JsonApiException(' ',
                                       title = HTTP_STATUS_CODES[403],
                                       status = '403')
        return None

def find_user_by_day_id(day_id):
    try:
        day = Day.query.filter_by(id=day_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'day_id'},
                             "Day: {} not found".format(day_id))
    else:
        if day.user is not None:
            if (g.current_user.is_administrator() or
                day.user == g.current_user):
                return day.user
            else:
                # Unauthorized
                raise JsonApiException(' ',
                                       title = HTTP_STATUS_CODES[403],
                                       status = '403')
        return None

def find_day_by_meal_id(meal_id):
    try:
        meal = Meal.query.filter_by(id=meal_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'meal_id'},
                             "Meal: {} not found".format(meal_id))
    else:
        if meal.day is not None:
            if (g.current_user.is_administrator() or
                meal.user == g.current_user):
                return meal.day
            else:
                # Unauthorized
                raise JsonApiException(' ',
                                       title = HTTP_STATUS_CODES[403],
                                       status = '403')
        return None


class MealList(ResourceList):
    def query(self, view_kwargs):
        # we come here when querying meals:
        # GET /api/v1/meals
        # GET /api/v1/users/<id>/meals
        query_ = self.session.query(Meal)

        if view_kwargs.get('id') is not None:
            # If the user's id is given, query only for that user's meals
            try:
                self.session.query(User).filter_by(id=view_kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(view_kwargs['id']))
            else:
                if (g.current_user.is_administrator() or
                    g.current_user.id == view_kwargs['id']):
                    query_ = query_.join(User).filter(User.id == view_kwargs['id'])
                else:
                    # Forbidden
                    raise JsonApiException(' ',
                                           title = HTTP_STATUS_CODES[403],
                                           status = '403')
        else:
            # If the user's id is not given and current user is not
            # administrator, query only for current user's meals
            if not g.current_user.is_administrator():
                query_ = query_.join(User).filter(User.id == g.current_user.id)

        return query_

    def before_create_object(self, data, view_kwargs):
        # POST /meals

        # set the foreign key to the logged in user
        data['user_id'] = g.current_user.id

        if ('calories' not in data and
            'description' not in data):
            raise BadRequest('Must include description and/or calories fields')

        if 'calories' not in data:
            meal_calories = get_calories_from_nutritionix(data['description'])
            data['calories'] = meal_calories


    def after_create_object(self, obj, data, view_kwargs):
        if isinstance(obj,Meal):  # make sure Meal was succesfully created
            w = obj.add_meal_to_day()

    def before_update_object(self, obj, data, view_kwargs):
        if isinstance(obj,Meal):
            w = obj.remove_meal_from_day()

    def after_update_object(self, obj, data, view_kwargs):
        if isinstance(obj,Meal):
            w = obj.add_meal_to_day()

    def before_delete_object(self, obj, view_kwargs):
        if isinstance(obj,Meal):
            w = obj.remove_meal_from_day()


    def before_get_object(self, view_kwargs):
        ...
        pass

    schema = MealSchema
    data_layer = {'session': db.session,
                  'model': Meal,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object,
                      'before_update_object': before_update_object,
                      'after_update_object': after_update_object,
                      'before_delete_object': before_delete_object,
                      'before_get_object': before_get_object
                  }
                  }


class MealDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        # Find the user and check access permission if we got here through:
        meal_id = view_kwargs['id']
        user = find_user_by_meal_id(meal_id)
        if (g.current_user.is_administrator() or
            g.current_user.is_usermanager() or
            g.current_user.id == user.id):
            pass
        else:
            # Unauthorized
            raise JsonApiException(' ',
                                   title = HTTP_STATUS_CODES[403],
                                   status = '403')

    schema = MealSchema
    data_layer = {'session': db.session,
                  'model': Meal,
                  'methods': {
                      'before_get_object': before_get_object
                  }
                  }


class MealUserRelationship(ResourceRelationship):
    schema = MealSchema
    data_layer = {'session': db.session,
                  'model': Meal,
                  }

class MealDayRelationship(ResourceRelationship):
    schema = MealSchema
    data_layer = {'session': db.session,
                  'model': Meal,
                  }

class DayList(ResourceList):
    def query(self, view_kwargs):
        # we come here when querying days:
        # GET /api/v1/days
        # GET /api/v1/users/<id>/days
        query_ = self.session.query(Day)

        if view_kwargs.get('id') is not None:
            # If the user's id is given, query only for that user's days
            try:
                self.session.query(User).filter_by(id=view_kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(view_kwargs['id']))
            else:
                if (g.current_user.is_administrator() or
                    g.current_user.id == view_kwargs['id']):
                    query_ = query_.join(User).filter(User.id == view_kwargs['id'])
                else:
                    # Forbidden
                    raise JsonApiException(' ',
                                           title = HTTP_STATUS_CODES[403],
                                           status = '403')
        else:
            # If the user's id is not given and current user is not
            # administrator, query only for current user's meals
            if not g.current_user.is_administrator():
                query_ = query_.join(User).filter(User.id == g.current_user.id)

        return query_

    def before_get_object(self, view_kwargs):
        ...
        pass

    schema = DaySchema
    data_layer = {'session': db.session,
                  'model': Day,
                  'methods': {
                      'query': query,
                      'before_get_object': before_get_object
                  }
                  }
    methods = ['GET']  # only implement GET. rest is done automatic.


class DayDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        # Find the user and check access permission if we got here through:
        day_id = view_kwargs['id']
        user = find_user_by_day_id(day_id)
        if (g.current_user.is_administrator() or
            g.current_user.is_usermanager() or
            g.current_user.id == user.id):
            pass
        else:
            # Unauthorized
            raise JsonApiException(' ',
                                   title = HTTP_STATUS_CODES[403],
                                   status = '403')

        # - GET /api/v1/meals/<meal_id>/day
        if view_kwargs.get('meal_id') is not None:
            day = find_day_by_meal_id(view_kwargs['meal_id'])
            view_kwargs['id'] = day.id


    schema = DaySchema
    data_layer = {'session': db.session,
                  'model': Day,
                  'methods': {
                      'before_get_object': before_get_object
                  }
                  }
    methods = ['GET']  # only implement GET. rest is done automatic.


class DayUserRelationship(ResourceRelationship):
    schema = DaySchema
    data_layer = {'session': db.session,
                  'model': Day,
                  }
    methods = ['GET']  # only implement GET. rest is done automatic.

class DayMealRelationship(ResourceRelationship):
    schema = DaySchema
    data_layer = {'session': db.session,
                  'model': Day,
                  }
    methods = ['GET']  # only implement GET. rest is done automatic.


###############################################################################
# Flask-REST-JSONAPI: Create endpoints (routes)
#
#http://flask-rest-jsonapi.readthedocs.io/en/latest/flask-rest-jsonapi.html
#
#Parameters given to api.route:
#
# resource (Resource) – a resource class inherited from
#                       flask_rest_jsonapi.resource.Resource
#                       -> see resource_managers.py
# view (str) – the view name
#              -> used eg. in check_permissions
# urls (list) – the urls of the view
#               -> used by clients in CRUD requests
# kwargs (dict) – additional options of the route

##########################################################################

rest_jsonapi.route(MealList, 'meal_list',
          '/meals/',
          '/users/<int:id>/meals/',
          '/days/<int:id>/meals/')

rest_jsonapi.route(MealDetail, 'meal_detail',
          '/meals/<int:id>')

rest_jsonapi.route(MealUserRelationship, 'meal_user',
          '/meals/<int:id>/relationships/user')

rest_jsonapi.route(MealDayRelationship, 'meal_day',
          '/meals/<int:id>/relationships/day')

##########################################################################
rest_jsonapi.route(DayList, 'day_list',
          '/days/',
          '/users/<int:id>/days/')

rest_jsonapi.route(DayDetail, 'day_detail',
          '/days/<int:id>',
          '/meals/<int:meal_id>/day')

rest_jsonapi.route(DayUserRelationship, 'day_user',
          '/days/<int:id>/relationships/user')

rest_jsonapi.route(DayMealRelationship, 'day_meals',
          '/days/<int:id>/relationships/meals/')

##########################################################################
