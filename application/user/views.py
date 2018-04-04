import os

from flask import Blueprint, render_template, send_from_directory, request, \
    current_app, flash
from flask_login import login_required, current_user

from .forms import profile_form, profile_pic_form

from ..extensions import db
from ..utils import get_current_time


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = profile_form(obj=current_user)

    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        if email != current_user.email:
            # Note: in forms we already check if email is unique
            current_user.email = email

        if first_name != current_user.first_name:
            current_user.first_name = first_name

        if last_name != current_user.last_name:
            current_user.last_name = last_name

        db.session.commit()

        flash('Public profile updated.', 'success')

    return render_template('user/profile.html', form=form)

@user.route('/profile_pic', methods=['GET', 'POST'])
@login_required
def profile_pic():
    form = profile_pic_form(obj=current_user)

    if form.validate_on_submit():
        client_file_storage = form.profile_pic.data
        if client_file_storage:
            current_user.profile_pic = client_file_storage  # Calls our "setter"

        db.session.commit()
        flash('Profile picture updated.', 'success')

    return render_template('user/profile_pic.html', form=form)
