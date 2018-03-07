from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from ...user import User
from .errors import error_response
from flask_rest_jsonapi.exceptions import JsonApiException
from werkzeug.http import HTTP_STATUS_CODES
from flask_login import login_user

# basic_auth is for checking the password during log in
# - if OK, it will create and return a token to the requester
# - if NOT OK, it will send back a 401 UNAUTHORIZED error
basic_auth = HTTPBasicAuth()

# token_auth is used to protect endpoints that can only be accessed by a
# logged in user. Protect them with the decorator:@token_auth.login_required
# Then, token_auth.verify_token is called to check if the token sent with
# request belongs to a user, and if so, that it has not expired.
# - if OK,the user that currently bears this token becomes the current_user
#    and the endpoints that were protected by @token_auth.login_required will
#    be handled.
# - if NOT OK, it will send back a 401 UNAUTHORIZED error
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    u = User.query.filter_by(email=email).first()
    if u is None:
        return False
    g.current_user = u
    return u.verify_password(password)

@basic_auth.error_handler
def basic_auth_error():
    raise JsonApiException("Invalid email or password",
                           title = HTTP_STATUS_CODES[401],
                           status = '401')

@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    if g.current_user is not None:
        login_user(g.current_user, remember=False)  # Register with Flask-Login
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    raise JsonApiException("Invalid token",
                           title = HTTP_STATUS_CODES[401],
                           status = '401')


