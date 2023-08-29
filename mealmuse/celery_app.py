from celery import Celery

celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')

# If you want Celery to autodiscover tasks from specific modules
celery.autodiscover_tasks(['mealmuse.tasks'], force=True)
