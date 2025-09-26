"""
URLs API pour l'application inventory.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet, CategoryViewSet, UnitViewSet, 
    StockMovementViewSet
)

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'units', UnitViewSet)
router.register(r'stock-movements', StockMovementViewSet)
# router.register(r'suppliers', SupplierViewSet)  # À ajouter plus tard

urlpatterns = [
    # Inclure les routes du router
    path('', include(router.urls)),
]