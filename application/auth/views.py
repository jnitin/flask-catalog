"""Define the URL routes (views) for the auth blueprint and handle all the
HTTP requests into those routes. (front-end)
"""
import random
import string
import json
import httplib2
import requests
from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, make_response
from flask_login import login_user, current_user, logout_user
from werkzeug.urls import url_parse
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from ..email import send_confirmation_email, send_password_reset_email
from ..user import User
from ..extensions import db
from .forms import RegisterForm, RegisterInvitationForm, LoginForm, \
     ResetPasswordRequestForm, ResetPasswordForm

auth = Blueprint('auth', __name__)  # pylint: disable=invalid-name


@auth.before_app_request
def before_request():
    """Redirect unconfirmed users to the proper landing page"""
    if current_user.is_authenticated and not current_user.confirmed:
        if request.blueprint != 'auth' and \
           request.endpoint != 'email.confirm' and \
           request.endpoint != 'email.check_your_email' and \
           request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

    return None


@auth.route('/unconfirmed')
def unconfirmed():
    """Display message to user that email is not yet confirmed"""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('auth.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/')
def index():
    """Display main landing page, which is different for a visitor versus a
    logged in user.
    """
    if current_user.is_authenticated and current_user.confirmed and \
       not current_user.blocked:
        return redirect(url_for('catalog.categories'))
    return render_template('index.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Allow user to login."""
    if current_user.is_authenticated and current_user.confirmed and \
       not current_user.blocked:
        return redirect(url_for('catalog.categories'))

    # Create anti-forgery state token for google oauth logic with Ajax request
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state

    # Pass client_id of google oauth2 to template
    client_id = current_app.config['GOOGLE_OAUTH2']['web']['client_id']

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        # check if account is blocked
        if user and user.blocked:
            return redirect(url_for('auth.blocked_account'))

        if user and user.verify_password(password):
            login_user(user, form.remember.data)

            # check if flask-login has redirected us via login_required
            # if so, it appended a next query string to the request
            # verify we have a URL that stays within our domain
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('catalog.categories')
            return redirect(next_page)

        flash('Sorry, invalid login', 'danger')

        # check again if account is blocked
        if user and user.blocked:
            return redirect(url_for('auth.blocked_account'))

    # Extract next URL to go to after a successfull login, and pass to
    # to template to be passed on to gconnect
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('catalog.categories')

    return render_template('auth/login.html', form=form,
                           google_oauth2_client_id=client_id,
                           state=state,
                           nxt=next_page)


@auth.route('/logout')
def logout():
    """Allow user to logout."""
    logout_user()
    flash('Succesfully logged out', 'success')
    return redirect(url_for('auth.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Allow user to register."""
    if current_user.is_authenticated and current_user.blocked:
        return redirect(url_for('auth.blocked_account'))

    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('catalog.categories'))

    # Create anti-forgery state token for google oauth logic with Ajax request
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state

    # Pass client_id of google oauth2 to template
    client_id = current_app.config['GOOGLE_OAUTH2']['web']['client_id']

    form = RegisterForm()

    # check if user is blocked
    if form.is_submitted():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.blocked:
            return redirect(url_for('auth.blocked_account'))

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('email already registerd by other user', 'danger')
            return render_template('auth/register.html', form=form)

        user = User.create_user(email=form.email.data,
                                password=form.password.data,
                                first_name=form.first_name.data,
                                last_name=form.last_name.data,
                                confirmed=False)

        # send user a confirmatin link via email
        send_confirmation_email(user)
        flash('Thanks for registering! ', 'success')
        flash('Check your email for the instructions to activate your account',
              'success')
        return redirect(url_for('email.check_your_email'))

    # Set next page to go go after registration via google, which also logs in
    next_page = url_for('catalog.categories')

    return render_template('auth/register.html', form=form,
                           google_oauth2_client_id=client_id,
                           state=state,
                           nxt=next_page)


@auth.route('/register/<token>', methods=['GET', 'POST'])
def register_from_invitation(token):
    """Allow user to register from a link in an invitation email."""
    if current_user.is_authenticated:
        logout_user()

    user_email = User.email_from_invitation_token(token)

    if user_email is False:
        flash('The invitation link is invalid or has expired.')
        return redirect(url_for('auth.index'))

    if User.query.filter_by(email=user_email).first():
        flash('Registration was already completed before', 'success')
        return redirect(url_for('auth.login'))

    form = RegisterInvitationForm(next=request.args.get('next'))

    if form.validate_on_submit():
        User.create_user(email=user_email,
                         password=form.password.data,
                         first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         confirmed=True)  # auto-confirm invited users

        flash('Thanks for registering! ', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_from_invitation.html',
                           form=form,
                           user_email=user_email)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Allow user to request reset password email."""
    if current_user.is_authenticated and current_user.blocked:
        return redirect(url_for('auth.blocked_account'))

    if current_user.is_authenticated:
        send_password_reset_email(current_user)
        flash('Check your email for the instructions to reset your password',
              'success')
        return redirect(url_for('email.check_your_email'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # always show this message, even if email not yet registered
        flash('Check your email for the instructions to reset your password',
              'success')
        return redirect(url_for('email.check_your_email'))

    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Allow user to reset password from a link in a reset password email."""
    if current_user.is_authenticated:
        logout_user()

    user = User.verify_reset_password_token(token)
    if not user:
        flash('The reset password link is invalid or has expired.')
        return redirect(url_for('auth.index'))

    if user.blocked:
        return redirect(url_for('auth.blocked_account'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/blocked_account')
def blocked_account():
    """Display message that account has been blocked"""
    flash('Your account has been blocked.', 'danger')
    flash('Contact the site administrator.', 'danger')
    return render_template('auth/blocked_account.html')


###############################################################################
# Handle the AJAX request that the client sends to the server after succesful
# authentication with the Google+ API server.
#
@auth.route('/gconnect', methods=['POST'])
def gconnect():
    """Login (and register on the fly) via Google OAUTH2 authentication"""
    # Validate state token protect against cross-site reference forgery attacks
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    # This is the one-time code that Google+ API had sent to the client
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object:
        # ask google+ api server for a credentials object, using the one-time
        # code that was provided to the client and passed on via the AJAX
        # request to this gconnect function.
        file = current_app.config['GOOGLE_OAUTH2_FILE']

        oauth_flow = flow_from_clientsecrets(file, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that all is OK with credentials, and if not, return message
    response = check_google_credentials(credentials)
    if response is not None:
        return response

    # Store the access token in the session for later use.
    # For now, we don't stay connected to google, so not needed to store this
    # session['access_token'] = credentials.access_token
    # session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # session['username'] = data['name']
    # session['picture'] = data['picture']
    # session['email'] = data['email']

    user = User.query.filter_by(email=data['email']).first()
    if user:
        # check if account is blocked
        if user.blocked:
            return redirect(url_for('auth.blocked_account'))
    else:
        user = User.create_user(email=data['email'],
                                password=None,
                                first_name=data['given_name'],
                                last_name=data['family_name'],
                                confirmed=True,  # email is confirmed
                                with_google=True,
                                profile_pic_url=data['picture'])

    # when we get here, all is kosher with google login
    # login with Flask_Login
    login_user(user, remember=True)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('catalog.categories')

    return next_page


def check_google_credentials(credentials):
    """Check validity of google credentials"""

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    http = httplib2.Http()
    result = json.loads(http.request(url, 'GET')[1].decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this current_app
    client_id = current_app.config['GOOGLE_OAUTH2']['web']['client_id']
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    return None

###############################################################################
# DISCONNECT - Revoke a current user's token and reset their session
# We did not stay connected to Google, so we do not need this function at this
# this time...
# @auth.route('/gdisconnect')
# def gdisconnect():
#     access_token = session.get('access_token')
#     if access_token is None:
#         print('Access Token is None')
#         response = make_response(json.dumps(
#             'Current user not connected.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     print('In gdisconnect access token is {}'.format(access_token))
#     print('User name is: ')
#     print(session['username'])
#     url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
#         session['access_token'])
#     h = httplib2.Http()
#     result = http.request(url, 'GET')[0]
#     print('result is ')
#     print(result)
#     if result['status'] == '200':
#         del session['access_token']
#         del session['gplus_id']
#         del session['username']
#         del session['email']
#         del session['picture']
#         response = make_response(json.dumps(
#             'Successfully disconnected.'), 200)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     else:
#         response = make_response(json.dumps(
#             'Failed to revoke token for given user.', 400))
#         response.headers['Content-Type'] = 'application/json'
#         return response
