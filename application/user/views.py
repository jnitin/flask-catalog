import os

from flask import Blueprint, render_template, send_from_directory, request, \
    current_app, flash, redirect, url_for
from flask_login import login_required, current_user

from . import User
from .forms import profile_form
from ..extensions import db
from ..catalog import Category, Item
from ..utils import get_current_time


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Update profile of current user"""
    form = profile_form(obj=current_user)

    if form.validate_on_submit():
        client_file_storage = form.profile_pic.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        if client_file_storage:
            current_user.profile_pic = client_file_storage  # Calls our "setter"

        if email and email != current_user.email:
            # Note: in forms we already validate if email is unique
            current_user.email = email

        if first_name and first_name != current_user.first_name:
            current_user.first_name = first_name

        if last_name and last_name != current_user.last_name:
            current_user.last_name = last_name

        db.session.commit()

        flash('Profile updated.', 'success')

    return render_template('user/profile.html', form=form)


@user.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Delete account of current user"""
    #
    # NOTES:
    # Confirmation if user really wants to delete is done on client side
    # so, we do not use a form asking for confirmation, just go & delete it
    #
    email = current_user.email

    User.delete_account(current_user)

    flash("Deleted account '<b>{}</b>' and all owned Categories and Items".format(email),
          'success')

    return redirect(url_for('auth.index'))