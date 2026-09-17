import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def database_url():
    value = os.getenv('DATABASE_URL', '').strip()
    # Some providers still return the deprecated postgres:// prefix.
    if value.startswith('postgres://'):
        value = 'postgresql://' + value[len('postgres://'):]
    return value or f'sqlite:///{os.path.join(BASE_DIR, "taskscheduler.db")}'

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'local-development-secret-change-me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'local-development-jwt-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    CORS_HEADERS = 'Content-Type'
