"""Define the REST api blueprint with a prefix for the URL routes (views)"""
from flask import Blueprint

api = Blueprint('api',  # pylint: disable=invalid-name
                __name__, url_prefix='/api/v1')
