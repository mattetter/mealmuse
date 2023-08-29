# config.py
import os

class Config(object):
    """
    Common configurations
    """
    # Put any configurations here that are common across all environments
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY') or 'thrandomstring'
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
    
class DevelopmentConfig(Config):
    """
    Development configurations
    """
    DEBUG = True
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "postgresql://matt:echo@localhost/development_database"
    # CELERY_ALWAYS_EAGER = True


class TestingConfig(Config):
    """
    Testing configurations
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://matt:echo@localhost/development_database"
    WTF_CSRF_ENABLED = False  # Disable CSRF tokens in the Forms for simplicity in testing
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True



class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Get the DATABASE_URL environment variable
    SQLALCHEMY_ECHO = False
