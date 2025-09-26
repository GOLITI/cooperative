"""
URLs de l'application core - Fonctionnalités centrales du système.
Page d'accueil, tableau de bord, vues générales.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]