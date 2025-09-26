"""
Initialisation du projet cooperative.
Import de Celery pour la configuration des tâches asynchrones.
"""

# Import de Celery pour s'assurer qu'il est chargé avec Django
from .celery import app as celery_app

__all__ = ('celery_app',)