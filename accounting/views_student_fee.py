from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from students.models import Student
from .models import Fee
from .forms import FeeForm

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
            return redirect('accounting:student_fee_list')
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
            return redirect('accounting:student_fee_list')
    else:
        form = FeeForm(instance=fee)

    return render(request, 'accounting/edit_student_fee.html', {'form': form, 'fee': fee})


# Supprimer un frais d'étudiant
def delete_student_fee(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, f"Frais supprimé pour l'étudiant {fee.student.first_name} {fee.student.last_name}.")
        return redirect('accounting:student_fee_list')

    return render(request, 'accounting/delete_student_fee.html', {'fee': fee})