"""URLs API pour l'application reports."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', api_views.DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('export/', api_views.ExportReportAPIView.as_view(), name='export-report'),
]