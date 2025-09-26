"""Celery application instance for the project."""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')

app = Celery('cooperative')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Baseline task to verify Celery worker wiring."""
    print(f'Request: {self.request!r}')
