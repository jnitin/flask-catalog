import os

from flask import Blueprint, render_template, send_from_directory, request, \
    current_app, flash
from flask_login import login_required, current_user

from .forms import ProfileForm

from ..extensions import db
from ..utils import get_current_time


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)

        db.session.commit()

        flash('Public profile updated.', 'success')

    return render_template('user/profile.html', form=form)
