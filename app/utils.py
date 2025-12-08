from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """Kullanım: @role_required('admin', 'moderator')"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if not current_user.has_role(*roles):
                # 403 ya da flash+redirect istersen değiştir
                from flask import flash, redirect, url_for
                flash("Bu işlemi yapma yetkiniz yok.", "error")
                return redirect(url_for('views.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
