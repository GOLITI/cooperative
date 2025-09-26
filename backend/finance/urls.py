from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'transactions', views.FinancialTransactionViewSet)
router.register(r'member-savings', views.MemberSavingsViewSet)
router.register(r'loans', views.LoanViewSet)
router.register(r'loan-payments', views.LoanPaymentViewSet)
router.register(r'budgets', views.BudgetViewSet)
router.register(r'budget-lines', views.BudgetLineViewSet)

app_name = 'finance'
urlpatterns = [
    path('', include(router.urls)),
]