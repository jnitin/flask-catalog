from flask import jsonify, g
from ...extensions import db
from .. import api
from .utils import basic_auth

@api.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})

