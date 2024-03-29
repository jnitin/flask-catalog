"""Define the URL routes (views) for the auth package of the REST api blueprint
and handle all the HTTP requests into those api routes
"""
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask import jsonify, g
from .errors import unauthorized
from .. import api as api_blueprint
from ...user import User
from ...decorators import usermanager_required


@api_blueprint.route('/token', methods=['POST'])
def get_token():
    """Return a token in response to API request.
    Make sure that authentication is done via email & password.
    """
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})


@api_blueprint.route('/users/<int:user_id>/unblock', methods=['POST'])
@usermanager_required
def unblock(user_id):
    """Unblock a user account, if authenticated requester has sufficient
    permissions at level of usermanager or admin
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise ObjectNotFound("This user does not exist")

    user.unblock()
    return jsonify(message='User account succesfully unblocked'), 201
