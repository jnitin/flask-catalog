from . import CategorySchema, ItemSchema
from .. import api as api_blueprint
from ...user import User, Role, Permission
from ...catalog import Category, Item
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

def find_user_by_category_id(category_id):
    try:
        category = Category.query.filter_by(id=category_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'category_id'},
                             "Category: {} not found".format(category_id))
    else:
        return category.user


def find_user_by_item_id(item_id):
    try:
        item = Item.query.filter_by(id=item_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'item_id'},
                             "Item: {} not found".format(item_id))
    else:
        return item.user


def query_for_user_only(query_, user_id):
    """If the user's id is given, query only for that user's data only"""
    try:
        User.query.filter_by(id=user_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(user_id))
    else:
        query_ = query_.join(User).filter(User.id == user_id)

    return query_

class CategoryList(ResourceList):
    def query(self, view_kwargs):
        # we come here when querying categories:
        # GET /api/v1/categories
        # GET /api/v1/users/<id>/categories
        query_ = self.session.query(Category)

        user_id = view_kwargs.get('id')
        if user_id:
            query_ = query_for_user_only(query_, user_id)

        return query_

    def before_create_object(self, data, view_kwargs):
        # POST /api/v1/categories

        if 'name' not in data:
            raise BadRequest('Must include name field')

        # set the foreign key to the logged in user
        data['user_id'] = g.current_user.id


    schema = CategorySchema
    data_layer = {'session': db.session,
                  'model': Category,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }
                  }


class CategoryDetail(ResourceDetail):
    schema = CategorySchema
    data_layer = {'session': db.session,
                  'model': Category
                  }


class CategoryUserRelationship(ResourceRelationship):
    schema = CategorySchema
    data_layer = {'session': db.session,
                  'model': Category
                  }
    methods = ['GET']  # only implement GET


class CategoryItemRelationship(ResourceRelationship):
    schema = CategorySchema
    data_layer = {'session': db.session,
                  'model': Category
                  }
    methods = ['GET']  # only implement GET


class ItemList(ResourceList):
    def query(self, view_kwargs):
        # we come here when querying items:
        # GET /api/v1/items
        # GET /api/v1/users/<id>/items
        query_ = self.session.query(Item)

        user_id = view_kwargs.get('id')
        if user_id:
            query_ = query_for_user_only(query_, user_id)

        return query_

    def before_create_object(self, data, view_kwargs):
        # POST /api/v1/items

        if ('category_id' not in data and
            'name' not in data and
            'description' not in data):
            raise BadRequest('Must include category_id, name and description ',
                             'fields')

        try:
            category = Category.query.filter_by(id=data['category_id']).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': 'category_id'},
                                 "Category with id: {} not found".format(
                                     data['category_id']))

        # set the foreign key to the logged in user
        data['user_id'] = g.current_user.id

    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }
                  }


class ItemDetail(ResourceDetail):
    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item
                  }


class ItemUserRelationship(ResourceRelationship):
    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item
                  }
    methods = ['GET']  # only implement GET


class ItemCategoryRelationship(ResourceRelationship):
    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item
                  }
    methods = ['GET']  # only implement GET


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

rest_jsonapi.route(CategoryList, 'category_list',
                   '/categories/',
          '/users/<int:id>/categories/',
          '/items/<int:id>/categories/')

rest_jsonapi.route(CategoryDetail, 'category_detail',
                   '/categories/<int:id>')

rest_jsonapi.route(CategoryUserRelationship, 'category_user',
                   '/categories/<int:id>/relationships/user')

rest_jsonapi.route(CategoryItemRelationship, 'category_item',
                   '/categories/<int:id>/relationships/item')

##########################################################################
rest_jsonapi.route(ItemList, 'item_list',
                   '/items/',
          '/users/<int:id>/items/')

rest_jsonapi.route(ItemDetail, 'item_detail',
                   '/items/<int:id>',
          '/categories/<int:category_id>/item')

rest_jsonapi.route(ItemUserRelationship, 'item_user',
                   '/items/<int:id>/relationships/user')

rest_jsonapi.route(ItemCategoryRelationship, 'item_categories',
                   '/items/<int:id>/relationships/categories/')

##########################################################################
