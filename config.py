import os
from sqlalchemy.pool import NullPool
import logging

class Config(object):
    """
    Common configurations
    """
    # Common configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY') or 'thrandomstring'
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
    # Common Logging Configuration
    # LOGGING_CONFIG = {
    #     'level': logging.INFO,
    #     'filename': 'common.log',
    #     'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # }

class DevelopmentConfig(Config):
    """
    Development configurations
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "postgresql://matt:echo@localhost/development_database"
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    # # Logging Configuration for Development
    # LOGGING_CONFIG = {
    #     'level': logging.DEBUG,
    #     'filename': 'development.log',
    #     'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # }

class TestingConfig(Config):
    """
    Testing configurations
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://matt:echo@localhost/development_database"
    WTF_CSRF_ENABLED = False  # Disable CSRF tokens in the Forms for simplicity in testing
    CELERY_ALWAYS_EAGER = True
    # Logging Configuration for Testing
    # LOGGING_CONFIG = {
    #     'level': logging.WARNING,
    #     'filename': 'testing.log',
    #     'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # }

class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Get the DATABASE_URL environment variable
    SQLALCHEMY_ECHO = False
    # Logging Configuration for Production
    LOGGING_CONFIG = {
        'level': logging.ERROR,
        'filename': 'production.log',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
