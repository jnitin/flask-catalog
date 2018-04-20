"""Provide clear JSON style error messages in response to bad, unauthorized or
forbidden requests.
"""
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    """Formatting of the error response in JSON format"""
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    """Handle 400 BAD REQUEST error"""
    return error_response(400, message)


def unauthorized(message):
    """Handle 401 UNAUTHORIZED error"""
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    """Handle 403 FORBIDDEN error"""
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response
