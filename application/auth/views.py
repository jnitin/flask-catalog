from uuid import uuid4

from flask import Blueprint, render_template, current_app, request, flash, \
    url_for, redirect, session, abort
from flask_login import login_required, login_user, current_user, logout_user, \
    confirm_login, login_fresh

from ..user import User
from ..extensions import db, login_manager
from .forms import RegisterForm, LoginForm, PasswordForm


auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
    return render_template('index.html')


@auth.route('/login', methods=['GET', 'POST'])
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
            #    flash("Succesfully logged in", 'success')
                return redirect(form.next.data or url_for('user.profile'))

        flash('Sorry, invalid login', 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Succesfully logged out', 'success')
    return redirect(url_for('auth.index'))


@auth.route('/register', methods=['GET', 'POST'])
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

    return render_template('auth/register.html', form=form)

@auth.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = PasswordForm()

    if form.validate_on_submit():
        current_user.password = form.new_password.data

        db.session.commit()

        flash('Password updated.', 'success')
        return redirect(url_for('user.profile'))

    return render_template('auth/password.html', form=form)
