import os
import sys
import types

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Keep `backend.*` imports working when Vercel deploys this folder as project root.
if 'backend' not in sys.modules:
    backend_package = types.ModuleType('backend')
    backend_package.__path__ = [BASE_DIR]
    sys.modules['backend'] = backend_package

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.database.db import db
from backend.routes.auth_routes import auth_bp
from backend.routes.task_routes import task_bp
from backend.routes.progress_routes import progress_bp
from backend.routes.admin_routes import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    frontend_url = os.getenv('FRONTEND_URL', '*').rstrip('/')
    allowed_origins = '*' if frontend_url == '*' else [frontend_url]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    jwt = JWTManager(app)

    # Custom JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({'error': 'Missing or invalid authentication token.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({'error': 'Invalid authentication token.'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Authentication token has expired. Please log in again.'}), 401

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(admin_bp)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Smart Student Task Scheduler API',
            'dsa_engine': 'PriorityQueue (Min-Heap / heapq)'
        }), 200

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='127.0.0.1', port=port, debug=False)
