"""
Configuration Celery pour le système de coopératives.
Gestion des tâches asynchrones : rapports, notifications, sauvegardes
"""
import os
from celery import Celery

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')

app = Celery('cooperative')

# Configuration depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-découverte des tâches dans toutes les apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Tâche de test pour vérifier que Celery fonctionne."""
    print(f'Request: {self.request!r}')