"""Define the URL routes (views) for the help package of the REST api
blueprint and handle all the HTTP requests into those api routes.

This package provides a helper function to allow an admin to retrieve a list
of all application URLs
"""
from werkzeug.utils import import_string
from flask import jsonify, current_app
from .. import api as api_blueprint
from ...decorators import admin_required


@api_blueprint.route('/help', methods=['GET'])
@admin_required
def routes_info():
    """Print all defined routes and their endpoint docstrings

    This also handles flask-router, which uses a centralized scheme
    to deal with routes, instead of defining them as a decorator
    on the target function.
    """
    routes = []
    for rule in current_app.url_map.iter_rules():
        try:
            if rule.endpoint != 'static':
                if hasattr(current_app.view_functions[rule.endpoint],
                           'import_name'):
                    import_name = current_app.view_functions[
                        rule.endpoint].import_name
                    obj = import_string(import_name)
                    routes.append({rule.rule: "%s\n%s" % (",".join(
                        list(rule.methods)), obj.__doc__)})
                else:
                    routes.append({rule.rule: current_app.view_functions[
                        rule.endpoint].__doc__})
        except AttributeError:
            routes.append({rule.rule:
                           "(%s) INVALID ROUTE DEFINITION!!!" % rule.endpoint})
            route_info = "%s => %s" % (rule.rule, rule.endpoint)
            current_app.logger.error("Invalid route: %s" % route_info,
                                     exc_info=True)
            # func_list[rule.rule] = obj.__doc__

    return jsonify(code=200, data=routes)
