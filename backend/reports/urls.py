from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet)
router.register(r'dashboards', views.DashboardViewSet)
router.register(r'report-templates', views.ReportTemplateViewSet)

app_name = 'reports'
urlpatterns = [
    path('', include(router.urls)),
]