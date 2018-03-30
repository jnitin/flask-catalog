from flask import Blueprint, abort, flash, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, \
    current_user

from .utils import send_confirmation_email
from ..extensions import db

email = Blueprint('email', __name__)


@email.route('/confirm/<token>')
@login_required
def confirm(token):
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
    send_confirmation_email(current_user)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('email.check_your_email'))

@email.route('/check_your_email')
def check_your_email():
    flash('Please check your email to activate your account.', 'success')
    return render_template('email/check_your_email.html')
