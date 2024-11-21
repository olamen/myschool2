from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from .models import Expense, Fee, ParentAccount, Payment
from .serializers import ExpenseSerializer, FeeSerializer, ParentAccountSerializer, PaymentSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer

class ParentAccountViewSet(viewsets.ModelViewSet):
    queryset = ParentAccount.objects.all()
    serializer_class = ParentAccountSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'accounting/expense_list.html', {'expenses': expenses})

# accounting/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MonthPayment
from students.models import Student
from datetime import date

def student_payment_view(request, student_id):
    student = Student.objects.get(id=student_id)
    current_year = date.today().year

    # Fetch pending payments for the student (excluding "Paid" or "Skipped")
    pending_payments = MonthPayment.objects.filter(
        student=student,
        status='Pending',
        year=current_year
    )

    # Handle form submission
    if request.method == 'POST':
        selected_months = request.POST.getlist('months')  # List of selected months (as strings)
        total_to_pay = 0
        payments_to_update = []

        for month_str in selected_months:
            month = int(month_str)
            payment = pending_payments.filter(month=month).first()

            if payment:
                total_to_pay += payment.amount
                payments_to_update.append(payment)

        # Process payment and mark months as paid
        for payment in payments_to_update:
            payment.status = 'Paid'
            payment.payment_date = date.today()
            payment.save()

        messages.success(request, f"Payment of {total_to_pay} processed successfully!")
        return redirect('student_payment', student_id=student.id)

    context = {
        'student': student,
        'pending_payments': pending_payments,
    }
    return render(request, 'accounting/student_payment.html', context)

# accounting/views.py
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import MonthPayment, Transaction
from students.models import Student
import uuid

@method_decorator(login_required, name='dispatch')
def student_payment_view(request, student_id):
    student = Student.objects.get(id=student_id)
    current_year = now().year

    # Fetch pending payments for the student (excluding "Paid" or "Skipped")
    pending_payments = MonthPayment.objects.filter(
        student=student,
        status='Pending',
        year=current_year
    )

    if request.method == 'POST':
        selected_months = request.POST.getlist('months')  # List of selected months (as strings)
        total_to_pay = 0
        months_paid = []

        for month_str in selected_months:
            month = int(month_str)
            payment = pending_payments.filter(month=month).first()

            if payment:
                total_to_pay += payment.amount
                months_paid.append(payment.get_month_display())
                payment.status = 'Paid'
                payment.payment_date = now()
                payment.save()

        # Create a transaction record
        receipt_number = f"REC-{uuid.uuid4().hex[:8].upper()}"
        Transaction.objects.create(
            student=student,
            user=request.user,  # Current logged-in user
            total_amount=total_to_pay,
            months_paid=json.dumps(months_paid),
            receipt_number=receipt_number
        )

        messages.success(request, f"Payment of {total_to_pay} processed successfully!")
        return redirect('student_payment', student_id=student.id)

    context = {
        'student': student,
        'pending_payments': pending_payments,
    }
    return render(request, 'accounting/student_payment.html', context)

@login_required
def print_receipt_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    return render(request, 'accounting/print_receipt.html', {'transaction': transaction})