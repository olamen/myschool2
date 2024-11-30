from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from students.models import Student
from .models import Fee, Payment
from .forms import FeeForm, PaymentForm

# Liste des frais des étudiants
def student_fee_list(request):
    fees = Fee.objects.all().order_by('-due_date')
    total_due = fees.filter(paid=False).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    total_paid = fees.filter(paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0

    context = {
        'fees': fees,
        'total_due': total_due,
        'total_paid': total_paid,
    }
    return render(request, 'accounting/student_fee_list.html', context)


# Ajouter un frais pour un étudiant
def add_student_fee(request):
    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f"Frais ajouté pour l'étudiant {fee.student.first_name} {fee.student.last_name}.")
            return redirect('student_fee_list')
    else:
        form = FeeForm()

    return render(request, 'accounting/add_student_fee.html', {'form': form})


# Modifier un frais d'étudiant
def edit_student_fee(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    if request.method == 'POST':
        form = FeeForm(request.POST, instance=fee)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f"Frais mis à jour pour l'étudiant {fee.student.first_name} {fee.student.last_name}.")
            return redirect('student_fee_list')
    else:
        form = FeeForm(instance=fee)

    return render(request, 'accounting/edit_student_fee.html', {'form': form, 'fee': fee})


# Supprimer un frais d'étudiant
def delete_student_fee(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, f"Frais supprimé pour l'étudiant {fee.student.first_name} {fee.student.last_name}.")
        return redirect('student_fee_list')

    return render(request, 'accounting/delete_student_fee.html', {'fee': fee})

def get_students_by_parent(request, parent_id):
    """
    Fetch students for a specific parent via AJAX.
    """
    students = Student.objects.filter(parents__id=parent_id).values('id', 'first_name', 'last_name')
    return JsonResponse(list(students), safe=False)

def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paiement enregistré avec succès.')
            return redirect('payment_list')  # Replace with the appropriate URL name
    else:
        form = PaymentForm()
    return render(request, 'accounting/add_payment.html', {'form': form})

def payment_list_ajax(request):
    """
    Returns a JSON response containing the list of payments.
    """
    if request.method == "GET":
        payments = Payment.objects.all().select_related('student', 'parent', 'user', 'cash_register')
        payment_data = [
            {
                "id": payment.id,
                "student": f"{payment.student.first_name} {payment.student.last_name}" if payment.student else "N/A",
                "parent": f"{payment.parent.first_name} {payment.parent.last_name}" if payment.parent else "N/A",
                "amount": f"{payment.amount:.2f}",
                "method": payment.get_method_display(),
                "date": payment.date.strftime('%d/%m/%Y'),
                "cash_register": f"{payment.cash_register.id}",
            }
            for payment in payments
        ]
        return JsonResponse(payment_data, safe=False)
    return JsonResponse({"error": "Invalid request method."}, status=400)