from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.database.db import db
from backend.models.user import User

def admin_required():
    """Decorator to ensure the authenticated user has the ADMIN role."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            if not user or user.role != 'ADMIN':
                return jsonify({'error': 'Forbidden: Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def student_required():
    """Decorator to ensure the authenticated user has the STUDENT role."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            if not user or user.role != 'STUDENT':
                return jsonify({'error': 'Forbidden: Student access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """Helper to fetch the current User object from JWT identity."""
    verify_jwt_in_request()
    user_id = int(get_jwt_identity())
    return db.session.get(User, user_id)
