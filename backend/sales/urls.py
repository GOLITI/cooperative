from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'sales', views.SaleViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'promotions', views.PromotionViewSet)

app_name = 'sales'
urlpatterns = [
    path('', include(router.urls)),
]