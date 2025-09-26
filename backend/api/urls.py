"""
URLs de l'application API - Routes pour l'API REST.
Endpoints pour l'intégration avec le frontend React.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

# Router pour les ViewSets DRF
router = DefaultRouter()

urlpatterns = [
    # API Router
    path('', include(router.urls)),
    
    # Authentification API
    path('auth/', include('rest_framework.urls')),
    
    # Endpoints spécifiques par application
    path('members/', include('members.api_urls')),
    path('inventory/', include('inventory.api_urls')),
    path('sales/', include('sales.api_urls')),
    path('finance/', include('finance.api_urls')),
    path('reports/', include('reports.api_urls')),
]