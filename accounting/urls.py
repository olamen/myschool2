from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, FeeViewSet, ParentAccountViewSet, PaymentViewSet, expense_list, print_receipt_view, student_payment_view

router = DefaultRouter()
router.register('expenses', ExpenseViewSet)
router.register('fees', FeeViewSet)
router.register('parent-accounts', ParentAccountViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('expense_list/', expense_list, name='expense_list'),
    path('student/<int:student_id>/payment/', student_payment_view, name='student_payment'),
    path('transaction/<int:transaction_id>/print/', print_receipt_view, name='print_receipt'),


]