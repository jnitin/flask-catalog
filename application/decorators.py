from functools import wraps
from flask import abort
from flask_login import current_user
from .user import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

def usermanager_required(f):
    return permission_required(Permission.CRUD_USERS)(f)
