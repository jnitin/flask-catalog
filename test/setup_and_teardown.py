"""Define the setUp and tearDown actions for our unit tests"""
from config import TestConfig
from application import create_app
from application.user import User, Role
from application.catalog import Item
from application.extensions import db
from application.extensions import api as rest_jsonapi

def my_setup(obj):
    """Call this function from setUp as:

    def setUp(self):
        my_setup(self)

    """
    # This seems a bug in Flask_REST_JSONAPI
    #
    # The Flask_REST_JSONAPI does not remove the Blue Blueprint objects
    # stored internally when the application objects they are applied to
    # is destroyed.
    #
    # I found this same issue is there for Flask Restful extension as
    # discovered and described in the book Mastering Flask:
    # https://books.google.com/books?id=NdZOCwAAQBAJ&pg=PA219&lpg=PA219&dq=flask:+how+to+destroy+application+object&source=bl&ots=nx7L_UG3EM&sig=yA-DG-ZYPtM5JxKJsFiXrhSkwzQ&hl=en&sa=X&ved=0ahUKEwies8G-x-7ZAhUh_IMKHdYKDCsQ6AEIdDAG#v=onepage&q=flask%3A%20how%20to%20destroy%20application%20object&f=false
    #
    # The result is that during a 2nd test, the view routes are created
    # twice and this error will be thrown:
    # builtins.AssertionError: View function mapping is overwriting an
    # existing endpoint function: api.api.user_list
    #
    # Workaround is to reset them manually
    rest_jsonapi.resources = []

    obj.app = create_app(TestConfig)
    # initialize the test client
    obj.client = obj.app.test_client
    obj.app_context = obj.app.app_context()
    obj.app_context.push()
    db.create_all()
    Role.insert_roles()
    User.insert_default_users()
    Item.insert_default_items()

def my_teardown(obj):
    """Call this function from tearDown as:

    def tearDown(self):
        my_teardown(self)

    """
    db.session.remove()
    db.drop_all()
    obj.app_context.pop()
