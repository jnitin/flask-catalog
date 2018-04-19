from flask_rest_jsonapi import ResourceDetail, ResourceList, \
     ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound, \
     BadRequest
from sqlalchemy.orm.exc import NoResultFound
from flask import g
from . import CategorySchema, ItemSchema
from ...user import User
from ...catalog import Category, Item
from ...extensions import db
from ...extensions import api as rest_jsonapi


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
        raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(
            user_id))
    else:
        query_ = query_.join(User).filter(User.id == user_id)

    return query_


def query_for_category_only(query_, category_id):
    """Query only for that category's data only"""
    try:
        Category.query.filter_by(id=category_id).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': 'category_id'},
                             "Category: {} not found".format(category_id))
    else:
        query_ = query_.join(Category).filter(Category.id == category_id)

    return query_


class CategoryList(ResourceList):
    """ResourceList: provides get and post methods to retrieve a collection of
                     objects or create one"""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html
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
                      'before_create_object': before_create_object}}


class CategoryDetail(ResourceDetail):
    """ResourceDetail: provides get, patch and delete methods to retrieve
                       details of an object, update an object and delete an
                       object"""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html

    schema = CategorySchema
    data_layer = {'session': db.session,
                  'model': Category}


class CategoryUserRelationship(ResourceRelationship):
    """ResourceRelationship: provides get, post, patch and delete methods to
                             get relationships, create relationships, update
                             relationships and delete relationships between
                             objects."""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html
    schema = CategorySchema
    data_layer = {'session': db.session,
                  'model': Category}
    methods = ['GET']  # only implement GET. rest is done automatic.


# class CategoryItemRelationship(ResourceRelationship):
#     """ResourceRelationship: provides get, post, patch and delete methods to
#                              get relationships, create relationships, update
#                              relationships and delete relationships between
#                              objects.
#     """
#     # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager
#     schema = CategorySchema
#     data_layer = {'session': db.session,
#                   'model': Category
#                   }


class ItemList(ResourceList):
    """ResourceList: provides get and post methods to retrieve a collection of
                     objects or create one"""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html
    def query(self, view_kwargs):
        # we come here when querying items:
        # GET /api/v1/items
        # GET /api/v1/users/<id>/items
        query_ = self.session.query(Item)

        user_id = view_kwargs.get('id')
        if user_id:
            query_ = query_for_user_only(query_, user_id)

        category_id = view_kwargs.get('category_id')
        if category_id:
            query_ = query_for_category_only(query_, category_id)

        return query_

    def before_create_object(self, data, view_kwargs):
        # POST /api/v1/categories/<int:category_id>/items

        category_id = view_kwargs.get('category_id')

        if ('name' not in data and
                'description' not in data):
            raise BadRequest('Must include id (of category), name and '
                             'description fields')

        try:
            category = Category.query.filter_by(id=category_id).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': 'category_id'},
                                 "Category with id: {} not found".format(
                                     data['category_id']))

        # set the foreign key to the logged in user
        data['user_id'] = g.current_user.id

        # set the foreign key for category
        data['category_id'] = category.id

    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object}}


class ItemDetail(ResourceDetail):
    """ResourceDetail: provides get, patch and delete methods to retrieve
                       details of an object, update an object and delete an
                       object"""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html

    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item}


class ItemUserRelationship(ResourceRelationship):
    """ResourceRelationship: provides get, post, patch and delete methods to
                             get relationships, create relationships, update
                             relationships and delete relationships between
                             objects."""
    # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager.html

    schema = ItemSchema
    data_layer = {'session': db.session,
                  'model': Item}


# class ItemCategoryRelationship(ResourceRelationship):
#     """ResourceRelationship: provides get, post, patch and delete methods to
#                              get relationships, create relationships, update
#                              relationships and delete relationships between
#                              objects."""
#     # http://flask-rest-jsonapi.readthedocs.io/en/latest/resource_manager
#
#     schema = ItemSchema
#     data_layer = {'session': db.session,
#                   'model': Item
#                   }


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

##########################################################################
rest_jsonapi.route(CategoryList, 'category_list',
                   '/categories/',
                   '/users/<int:id>/categories/')

rest_jsonapi.route(CategoryDetail, 'category_detail',
                   '/categories/<int:id>')

rest_jsonapi.route(CategoryUserRelationship, 'category_user',
                   '/categories/<int:category_id>/relationships/user')


##########################################################################
rest_jsonapi.route(ItemList, 'item_list',
                   '/items/',
                   '/users/<int:id>/items/',
                   '/categories/<int:category_id>/items/')

rest_jsonapi.route(ItemDetail, 'item_detail',
                   '/items/<int:id>')

rest_jsonapi.route(ItemUserRelationship, 'item_user',
                   '/items/<int:item_id>/relationships/user')

##########################################################################
