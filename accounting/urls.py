from django.urls import path, include
from .views import  *
from .views_transaction import *
from .views_student_fee import *


urlpatterns = [
    path('dashboard/',index,name='indexaccounting'),
    path('expense_list/', expense_list, name='expense_list'),

    path('parent-fees/<int:parent_id>/<int:classe_id>/', parent_fees_view, name='parent_fees_view'),


        # URLs pour la caisse
    path('cash-register/open/',open_cash_register, name='open_cash_register'),
    path('cash-register/close/<int:register_id>/',close_cash_register, name='close_cash_register'),
    path("cash-register/list/", cash_register_list, name="cash_register_list"),
    path("cash-register/details/<int:pk>/", cash_register_details, name="cash_register_details"),
    path('cash-register/status/',cash_register_status, name='cash_register_status'),

    # URLs pour les transactions
    path('transactions/',transaction_list, name='transaction_list'),
    path('transactions/add/',add_transaction, name='add_transaction'),
    path('transactions/<int:pk>/details/',transaction_details, name='transaction_details'),

    path('add-payment/', add_payment, name='add_payment'),
    path('get-students/<int:parent_id>/', get_students_by_parent, name='get_students_by_parent'),
    path('students/<int:student_id>/details/', get_student_details, name='get_student_details'),
    path('payments/ajax/', payment_list_ajax, name='payment_list_ajax'),

    # URLs pour les frais étudiants
    path('student-fees/',student_fee_list, name='student_fee_list'),
    path('student-fees/add/',add_student_fee, name='add_student_fee'),
    #path('student-fees/<int:pk>/edit/',edit_student_fee, name='edit_student_fee'),
    #path('student-fees/<int:pk>/delete/',delete_student_fee, name='delete_student_fee'),

    





]