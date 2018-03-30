from . import UserSchema
from .. import api as api_blueprint
from ...user import User, Role, Permission
from ...meal import Meal, Day
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


###############################################################################
# Flask-REST-JSONAPI: Create resource managers
# - For data layer methods and their parameters, see:
#    https://github.com/miLibris/flask-rest-jsonapi/blob/master/flask_rest_jsonapi/data_layers/base.py
#    https://github.com/miLibris/flask-rest-jsonapi/blob/master/flask_rest_jsonapi/resource.py

class UserList(ResourceList):
    def query(self, view_kwargs):
        # we come here when querying:
        # GET /api/users
        query_ = self.session.query(User)

        # If  current user is not administrator or usermanager,
        # filter by current user
        if not (g.current_user.is_administrator() or
                g.current_user.is_usermanager()):
            query_ = query_.filter_by(id=g.current_user.id)

        return query_

    def before_create_object(self, data, view_kwargs):
        # POST /users
        if ('email' not in data or 'password' not in data or
            'first_name' not in data or 'last_name' not in data):
            raise BadRequest('Must include email, password, first_name and last_name fields')

        u = self.session.query(User).filter_by(email=data['email']).first()
        if u:
            if u.blocked:
                raise JsonApiException(detail='Account has been blocked.'
                                    'Contact the site administrator.',
                                       title='Permission denied',
                                       status='403')
            else:
                raise BadRequest('Email {} already registered'.format(data['email']))

    def after_create_object(self, obj, data, view_kwargs):
        if obj.is_authenticated:
            # User was succesfully registered
            # send user a confirmatin link via email
            send_confirmation_email(obj)


    def before_get_object(self, view_kwargs):
        ...
        pass

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object,
                      'before_get_object': before_get_object
                  }
                  }


class UserDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        # Find the user and check access permission if we got here through:
        # - GET /api/v1/users/<id>
        if view_kwargs.get('id') is not None:
            if (g.current_user.is_administrator() or
                g.current_user.is_usermanager() or
                g.current_user.id == view_kwargs['id']):
                pass
            else:
                # Unauthorized
                raise JsonApiException(' ',
                                       title = HTTP_STATUS_CODES[403],
                                       status = '403')

        # - GET /api/v1/meals/<meal_id>/user
        if view_kwargs.get('meal_id') is not None:
            user = find_user_by_meal_id(view_kwargs['meal_id'])
            view_kwargs['id'] = user.id

        # - GET /api/v1/days/<day_id>/user
        if view_kwargs.get('day_id') is not None:
            user = find_user_by_day_id(view_kwargs['day_id'])
            view_kwargs['id'] = user.id

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'before_get_object': before_get_object
                  }
                  }


class UserMealRelationship(ResourceRelationship):
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  }

class UserDayRelationship(ResourceRelationship):
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  }

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


rest_jsonapi.route(UserList, 'user_list',
          '/users/')

rest_jsonapi.route(UserDetail, 'user_detail',
          '/users/<int:id>',
          '/meals/<int:meal_id>/user',
          '/days/<int:day_id>/user')

rest_jsonapi.route(UserMealRelationship, 'user_meals',
          '/users/<int:id>/relationships/meals/')

rest_jsonapi.route(UserDayRelationship, 'user_days',
          '/users/<int:id>/relationships/days/')



#############################################################################
# Custom routes, not going over Flask-REST-JSONAPI

@api_blueprint.route('/profile_pic', methods=['GET', 'POST'])
def upload_profile_pic():
    if request.method == 'POST':
        if 'profile_pic' in request.files:
            client_file_storage = request.files['profile_pic']
            g.current_user.profile_pic = client_file_storage  # Calls our "setter"

            db.session.commit()

            response = jsonify({})
            response.status_code = 201
            response.headers['Location'] = url_for('api.upload_profile_pic',
                                                   _external=True)
            return response
        else:
            return jsonify(
                message='profile_pic not in request files'), 400
    else:
        if g.current_user.profile_pic_filename:
            return send_from_directory(current_app.config['UPLOADED_IMAGES_DEST'],
                                       g.current_user.profile_pic_filename)
        else:
            return jsonify(message="Profile picture for user not found"), 404


@api_blueprint.route('/invite/<string:user_email>', methods=['POST'])
@admin_required
def invite(user_email):
    u = User.query.filter_by(email=user_email).first()
    if u:
        return jsonify(message='Email {} already registered'.format(
            user_email)), 401

    send_invitation_email(user_email)
    return jsonify(message='New user was invited by email.'), 201