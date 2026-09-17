from .auth_routes import auth_bp
from .task_routes import task_bp
from .progress_routes import progress_bp
from .admin_routes import admin_bp

__all__ = ['auth_bp', 'task_bp', 'progress_bp', 'admin_bp']
