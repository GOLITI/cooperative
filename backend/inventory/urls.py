from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'units', views.UnitViewSet)
router.register(r'products', views.ProductViewSet)

router.register(r'stock-movements', views.StockMovementViewSet)
router.register(r'inventories', views.InventoryViewSet)
router.register(r'inventory-lines', views.InventoryLineViewSet)

app_name = 'inventory'
urlpatterns = [
    path('', include(router.urls)),
]