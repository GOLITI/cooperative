"""
URLs API pour l'application sales.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet, SaleViewSet, SaleLineViewSet, 
    SalePaymentViewSet
)

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'sale-lines', SaleLineViewSet)
router.register(r'payments', SalePaymentViewSet)

urlpatterns = [
    # Inclure les routes du router
    path('', include(router.urls)),
]