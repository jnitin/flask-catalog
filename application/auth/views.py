from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, login_user, current_user, logout_user, \
    confirm_login, login_fresh

from ..email import send_confirmation_email
from ..user import User
from ..extensions import db, login_manager
from .forms import RegisterForm, RegisterInvitationForm, LoginForm, PasswordForm

auth = Blueprint('auth', __name__)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        #current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint != 'email.confirm' \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('auth.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/')
def index():
    if current_user.is_authenticated and current_user.is_active and \
       not current_user.blocked:
        return redirect(url_for('catalog.category_items'))
    return render_template('index.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    #if current_user.is_authenticated and current_user.is_active and \
       #not current_user.blocked:
        #return redirect(url_for('catalog.category_items'))

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
            nxt = request.args.get('next')
            if nxt is None or not nxt.startswith('/'):
                nxt = url_for('catalog.category_items')
            return redirect(nxt)

        flash('Sorry, invalid login', 'danger')

        # check again if account is blocked
        if user and user.blocked:
            return redirect(url_for('auth.blocked_account'))

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Succesfully logged out', 'success')
    return redirect(url_for('auth.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.blocked:
        return redirect(url_for('auth.blocked_account'))

    if current_user.is_authenticated and current_user.is_active:
        return redirect(url_for('catalog.category_items'))

    form = RegisterForm(next=request.args.get('next'))

    # check if user is blocked
    if form.is_submitted():
        email = form.email.data
        u = User.query.filter_by(email=email).first()
        if u and u.blocked:
            return redirect(url_for('auth.blocked_account'))

    if form.validate_on_submit():
        email = form.email.data
        if User.query.filter_by(email=email).first():
            flash('email already registerd by other user', 'danger')
            return render_template('auth/register.html', form=form)

        user = User()
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        # send user a confirmatin link via email
        send_confirmation_email(user)
        flash('Thanks for registering! ', 'success')
        return redirect(url_for('email.check_your_email'))

    return render_template('auth/register.html', form=form)

@auth.route('/register/<token>', methods=['GET', 'POST'])
def register_from_invitation(token):
    user_email = User.get_user_email_from_invitation_token(token)

    if user_email is False:
        flash('The invitation link is invalid or has expired.')
        return redirect(url_for('auth.index'))

    form = RegisterInvitationForm(next=request.args.get('next'))

    if form.validate_on_submit():
        email = user_email
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User(email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                    )
        user.confirm(token)  # auto-confirm invited users

        db.session.add(user)
        db.session.commit()

        # no need to send user a confirmatin link via email
        # send_confirmation_email(user)
        flash('Thanks for registering! ', 'success')
        #return redirect(url_for('email.check_your_email'))
        return redirect(url_for('auth.index'))

    return render_template('auth/register_from_invitation.html',
                           form=form,
                           user_email = user_email)

@auth.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = PasswordForm()

    if form.validate_on_submit():
        current_user.password = form.new_password.data

        db.session.commit()

        flash('Password updated.', 'success')
        return redirect(url_for('catalog.category_items'))

    return render_template('auth/password.html', form=form)


@auth.route('/blocked_account')
def blocked_account():
    flash('Your account has been blocked.', 'danger')
    flash('Contact the site administrator.', 'danger')
    return render_template('auth/blocked_account.html')
