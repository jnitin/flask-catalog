"""Decorators used by the application"""
from functools import wraps
from flask import abort
from flask_login import current_user
from .user import Permission


def permission_required(permission):
    """Decorator for permission control.

    Example usage:

    @permission_required(Permission.ADMIN)
    def a_method_that_needs_protection():
        ...
    """
    def decorator(func):  # pylint: disable=C0111
        @wraps(func)
        def decorated_function(*args, **kwargs):  # pylint: disable=C0111
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    """Special decorator for admin permission control.

    Example usage:

    @admin_required
    def a_method_that_needs_protection():
        ...
    """
    return permission_required(Permission.ADMIN)(func)


def usermanager_required(func):
    """Special decorator for usermanager permission control.

    Example usage:

    @usermanager_required
    def a_method_that_needs_protection():
        ...
    """
    return permission_required(Permission.CRUD_USERS)(func)
