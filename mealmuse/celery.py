# # celery.py
# from celery import Celery
# from mealmuse import create_app

# app = create_app('config.DevelopmentConfig')

# def make_celery(app):
#     celery = Celery(
#         app.import_name,
#         broker='redis://127.0.0.1:6379/0',
#         backend='redis://127.0.0.1:6379/1')
#     celery.conf.update(app.config)

#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)

#     celery.Task = ContextTask
#     celery.autodiscover_tasks(['mealmuse.tasks'], force=True)

#     return celery

# celery = make_celery(app)