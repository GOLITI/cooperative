"""
URLs API pour le module financier.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AccountCategoryViewSet,
    AccountViewSet,
    FinancialTransactionViewSet,
    MemberLoanViewSet,
    MemberSavingsViewSet
)

# Configuration du routeur
router = DefaultRouter()

# Enregistrement des ViewSets
router.register(r'categories', AccountCategoryViewSet, basename='accountcategory')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'transactions', FinancialTransactionViewSet, basename='financialtransaction')
router.register(r'loans', MemberLoanViewSet, basename='memberloan')
router.register(r'savings', MemberSavingsViewSet, basename='membersavings')

urlpatterns = [
    path('', include(router.urls)),
]