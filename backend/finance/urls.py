"""URLs de l'application finance - Gestion financière."""
from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.FinancialTransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', views.FinancialTransactionCreateView.as_view(), name='transaction_add'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
]