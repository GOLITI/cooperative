"""URLs de l'application sales - Gestion des ventes."""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView.as_view(), name='list'),
    path('add/', views.SaleCreateView.as_view(), name='add'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='detail'),
]