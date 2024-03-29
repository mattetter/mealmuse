from flask import Flask
from flask_login import LoginManager
from celery import Celery
from mealmuse.models import db, User
import logging
from flask_migrate import Migrate

celery = Celery(__name__, broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/1')
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)

    # Set up logging
    logging_config = app.config.get('LOGGING_CONFIG', {})
    logging.basicConfig(**logging_config)

    # Bind the app with extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    with app.app_context():
        db.create_all()

    # Register the blueprint
    from .views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    # Configure Celery to use Flask's app context
    celery.conf.update(app.config)

    return app

app = create_app('config.DevelopmentConfig')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))