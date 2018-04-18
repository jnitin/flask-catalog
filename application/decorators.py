from functools import wraps
from flask import abort
from flask_login import current_user
from .user import Permission


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    return permission_required(Permission.ADMIN)(func)


def usermanager_required(func):
    return permission_required(Permission.CRUD_USERS)(func)
