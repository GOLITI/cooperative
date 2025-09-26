"""URLs API pour l'application sales."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'', api_views.SaleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]