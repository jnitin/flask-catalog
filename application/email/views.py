"""Define the URL routes (views) for the email blueprint and handle all the
HTTP requests into those routes. (front-end)
"""
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import logout_user, login_required, \
    current_user

from .utils import send_confirmation_email
from ..extensions import db

email = Blueprint('email', __name__)  # pylint: disable=invalid-name


@email.route('/confirm/<token>')
@login_required
def confirm(token):
    """Validate that confirmation token is valid and confirm user"""
    if current_user.confirmed:
        return redirect(url_for('auth.index'))

    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.')

    return redirect(url_for('auth.index'))


@email.route('/confirm')
@login_required
def resend_confirmation():
    """Resend user a new confirmation email"""
    send_confirmation_email(current_user)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('email.check_your_email'))


@email.route('/check_your_email')
def check_your_email():
    """Display message that user needs to check it's email.
    Flashed messages will explain why this is needed.
    For example when email is not yet confirmed.
    """
    logout_user()
    return render_template('email/check_your_email.html')
