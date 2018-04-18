from flask_rest_jsonapi import ResourceDetail, ResourceList, \
     ResourceRelationship
from flask_rest_jsonapi.exceptions import JsonApiException, BadRequest
from werkzeug.http import HTTP_STATUS_CODES
from flask import current_app, g, request, send_from_directory, jsonify, \
     url_for
from . import UserSchema
from .. import api as api_blueprint
from ..catalog import find_user_by_category_id, find_user_by_item_id
from ...user import User
from ...decorators import admin_required
from ...email import send_confirmation_email, send_invitation_email
from ...extensions import db
from ...extensions import api as rest_jsonapi


###############################################################################
# Flask-REST-JSONAPI: Create resource managers
# - For data layer methods and their parameters, see:
#    https://github.com/miLibris/flask-rest-jsonapi/blob/master/
#          flask_rest_jsonapi/data_layers/base.py
#    https://github.com/miLibris/flask-rest-jsonapi/blob/master/
#          flask_rest_jsonapi/resource.py

class UserList(ResourceList):
    """ResourceList: provides get and post methods to retrieve a collection of
                     objects or create one"""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html
    def query(self, view_kwargs):
        # we come here when querying:
        # GET /api/v1/users
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
            raise BadRequest('Must include email, password, first_name and'
                             'last_name fields')

        user = self.session.query(User).filter_by(email=data['email']).first()
        if user:
            if user.blocked:
                raise JsonApiException(detail='Account has been blocked.'
                                       'Contact the site administrator.',
                                       title='Permission denied',
                                       status='403')
            else:
                raise BadRequest('Email {} already registered'.format(
                    data['email']))

    def after_create_object(self, obj, data, view_kwargs):
        if obj.is_authenticated:
            # User was succesfully registered
            # send user a confirmatin link via email
            send_confirmation_email(obj)

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object}}


class UserDetail(ResourceDetail):
    """ResourceDetail: provides get, patch and delete methods to retrieve
                       details of an object, update an object and delete an
                       object"""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html
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
                                       title=HTTP_STATUS_CODES[403],
                                       status='403')

        # - GET /api/v1/categories/<category_id>/user
        if view_kwargs.get('category_id') is not None:
            user = find_user_by_category_id(view_kwargs['category_id'])
            view_kwargs['id'] = user.id

        # - GET /api/v1/items/<item_id>/user
        if view_kwargs.get('item_id') is not None:
            user = find_user_by_item_id(view_kwargs['item_id'])
            view_kwargs['id'] = user.id

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'before_get_object': before_get_object}}


class UserCategoryRelationship(ResourceRelationship):
    """ResourceRelationship: provides get, post, patch and delete methods to
                             get relationships, create relationships, update
                             relationships and delete relationships between
                             objects."""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User
                 }
    methods = ['GET']  # only implement GET. rest is done automatic.


class UserItemRelationship(ResourceRelationship):
    """ResourceRelationship: provides get, post, patch and delete methods to
                             get relationships, create relationships, update
                             relationships and delete relationships between
                             objects."""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                 }
    methods = ['GET']  # only implement GET. rest is done automatic.

###############################################################################
# Flask-REST-JSONAPI: Create endpoints (routes)
#
# http://flask-rest-jsonapi.readthedocs.io/en/latest/routing.html
# -> api.route(<Resource manager>, <endpoint name>, <url_1>, <url_2>, ...)
#
# http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html
# -> ResourceList:         provides get and post methods to retrieve a
#                          collection of objects or create one.
#
# -> ResourceDetail:       provides get, patch and delete methods to retrieve
#                          details of an object, update an object and delete an
#                          object
#
# -> ResourceRelationship: provides get, post, patch and delete methods to get
#                          relationships, create relationships, update
#                          relationships and delete relationships between
#                          objects.


rest_jsonapi.route(UserList, 'user_list',
                   '/users/')

rest_jsonapi.route(UserDetail, 'user_detail',
                   '/users/<int:id>',
                   '/categories/<int:category_id>/user',
                   '/items/<int:item_id>/user')

rest_jsonapi.route(UserCategoryRelationship, 'user_categories',
                   '/users/<int:id>/relationships/categories/')

rest_jsonapi.route(UserItemRelationship, 'user_items',
                   '/users/<int:id>/relationships/items/')


#############################################################################
# Custom routes, not going over Flask-REST-JSONAPI
@api_blueprint.route('/profile_pic', methods=['GET', 'POST'])
def upload_profile_pic():
    if request.method == 'POST':
        if 'profile_pic' in request.files:
            client_file_storage = request.files['profile_pic']
            g.current_user.profile_pic = client_file_storage  # Calls "setter"

            db.session.commit()

            response = jsonify({})
            response.status_code = 201
            response.headers['Location'] = url_for('api.upload_profile_pic',
                                                   _external=True)
            return response

        return jsonify(
            message='profile_pic not in request files'), 400

    if g.current_user.profile_pic_filename:
        return send_from_directory(
            current_app.config['UPLOADED_IMAGES_DEST'],
            g.current_user.profile_pic_filename)

    return jsonify(message="Profile picture for user not found"), 404


@api_blueprint.route('/invite/<string:user_email>', methods=['POST'])
@admin_required
def invite(user_email):
    user = User.query.filter_by(email=user_email).first()
    if user:
        return jsonify(message='Email {} already registered'.format(
            user_email)), 401

    send_invitation_email(user_email)
    return jsonify(message='New user was invited by email.'), 201
