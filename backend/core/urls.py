from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'activity-logs', views.ActivityLogViewSet)

app_name = 'core'
urlpatterns = [
    path('', include(router.urls)),
]