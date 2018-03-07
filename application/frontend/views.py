from uuid import uuid4

from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, login_user, current_user, logout_user, \
    confirm_login, login_fresh

from application.user import User
from application.extensions import db, login_manager
from .forms import RegisterForm, LoginForm, RecoverPasswordForm, ReauthForm, \
    ChangePasswordForm


frontend = Blueprint('frontend', __name__)


@frontend.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
    return render_template('index.html')


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))

    form = LoginForm(login=request.args.get('login', None),
                     next=request.args.get('next', None))

    #
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash("Succesfully logged in", 'success')
            return redirect(form.next.data or url_for('user.profile'))
        else:
            flash('Sorry, invalid login', 'danger')

    return render_template('frontend/login.html', form=form)


@frontend.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        email = current_user.email
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            confirm_login()
            flash('Reauthenticated.', 'success')
            return redirect('/change_password')

        flash('Password is wrong.', 'danger')
    return render_template('frontend/reauth.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Succesfully logged out', 'success')
    return redirect(url_for('frontend.index'))


@frontend.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))

    form = RegisterForm(next=request.args.get('next'))

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        if login_user(user):
            flash('Registration successful!', 'success')
            return redirect(form.next.data or url_for('user.profile'))

    return render_template('frontend/register.html', form=form)


@frontend.route('/change_password', methods=['GET', 'POST'])
def change_password():
    user = None
    if current_user.is_authenticated:
        if not login_fresh():
            return login_manager.needs_refresh()
        user = current_user
    elif 'activation_key' in request.values and 'email' in request.values:
        activation_key = request.values['activation_key']
        email = request.values['email']
        user = User.query.filter_by(activation_key=activation_key) \
                         .filter_by(email=email).first()

    if user is None:
        abort(403)

    form = ChangePasswordForm(activation_key=user.activation_key)

    if form.validate_on_submit():
        user.password = form.password.data
        user.activation_key = None
        db.session.add(user)
        db.session.commit()

        flash("Your password has been changed, please log in again", "success")
        return redirect(url_for("frontend.login"))

    return render_template("frontend/change_password.html", form=form)


@frontend.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash('Please see your email for instructions on '
                  'how to access your account', 'success')

            user.activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()

            return render_template('frontend/reset_password.html', form=form)
        else:
            flash('Sorry, no user found for that email address', 'error')

    return render_template('frontend/reset_password.html', form=form)
