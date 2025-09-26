"""URLs de l'application reports - Rapports et statistiques."""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='list'),
    path('members/', views.MemberReportView.as_view(), name='members'),
    path('sales/', views.SalesReportView.as_view(), name='sales'),
    path('financial/', views.FinancialReportView.as_view(), name='financial'),
]