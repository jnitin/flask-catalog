from flask import g, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.http import HTTP_STATUS_CODES
from flask_login import login_user, login_manager
from .errors import error_response, bad_request, unauthorized, forbidden
from .. import api as api_blueprint
from ...user import User, AnonymousUser

# basic_auth is for checking the password during log in
# - if OK, it will create and return a token to the requester
# - if NOT OK, it will send back a 401 UNAUTHORIZED error
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        # We make 1 exception:
        #  POST /api/v#/users/ to register a new user is allowed without login
        if (request.endpoint == 'api.user_list' and request.method=='POST'):
            g.current_user = AnonymousUser()
            return True

        return False

    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False

    if user.verify_password(password):
        # Also login to flask_login
        login_user(user, remember=False)
        return True

    return False


@basic_auth.error_handler
def auth_error():
    #return unauthorized('Invalid credentials')
    # g.current_user might not be defined, so wrap it into a try block
    try:
        if g.current_user is not None and g.current_user.blocked:
            return error_response(403,'Account has been blocked.'
                                  'Contact the site administrator.')

        if g.current_user is not None and g.current_user.is_active is False:
            return error_response(403,"Account is not yet activated."
                                  "Please check your email to activate.")

        return unauthorized('Invalid credentials')
    except:
        return unauthorized('Invalid credentials')

@api_blueprint.before_request
@basic_auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')
