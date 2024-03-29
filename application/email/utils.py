"""Utilities used by the email blueprint"""
from flask import current_app, url_for, render_template
from flask_mail import Message
# from threading import Thread
from ..extensions import mail
from ..user import User


##############################################################################
# mail helper functions
# See: http://flask.pocoo.org/snippets/50/
#      https://gitlab.com/patkennedy79/flask_recipe_app/blob/master/web/
# #            project/users/views.py
#
##############################################################################

def send_async_email(msg):
    """Sends email from a thread"""
    with current_app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body):
    """Sends emails to recipients"""
    msg = Message(subject, recipients=recipients)
    msg.html = html_body

    mail.send(msg)  # outcomment this to do async
    # To send async
    # thr = Thread(target=send_async_email, args=[msg])
    # thr.start()


def get_confirmation_link(user):
    """Generates a token and returns a URL for email confirmation"""
    token = user.generate_confirmation_token()
    return url_for('email.confirm', token=token, _external=True)


def get_invitation_link(user_email):
    """Generates a token and returns a URL for invitation to register"""
    token = User.generate_invitation_token(user_email)
    return url_for('auth.register_from_invitation', token=token,
                   _external=True)


def get_reset_password_link(user):
    """Generates a token and returns a URL for a password reset"""
    token = user.generate_reset_password_token()
    return url_for('auth.reset_password', token=token, _external=True)


def send_confirmation_email(user):
    """Send confirmation email to registered user"""
    confirm_url = get_confirmation_link(user)

    email_html_body = render_template(
        'email/email_confirmation.html',
        confirm_url=confirm_url)

    send_email('Confirm Your Email Address', [user.email], email_html_body)


def send_invitation_email(user_email):
    """Send invitation email to a new user_email"""
    invitation_url = get_invitation_link(user_email)

    email_html_body = render_template(
        'email/email_invitation.html',
        invitation_url=invitation_url)

    send_email('You are invited to join Catalog',
               [user_email], email_html_body)


def send_password_reset_email(user):
    """Send password reset email to a registered user"""
    reset_password_url = get_reset_password_link(user)

    email_html_body = render_template(
        'email/email_reset_password.html',
        reset_password_url=reset_password_url)

    send_email('Reset Your Password', [user.email], email_html_body)
