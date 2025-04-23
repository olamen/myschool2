import calendar
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from students.models import Parent, Student
from .models import CashRegister, Fee, Payment
from .forms import FeeForm, PaymentForm
from accounting import models


@login_required
def student_fee_list(request):
    # Check if the user has the 'Adminf' or 'Super Admin' role
    if request.user.role not in ['Adminf', 'Super Admin']:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home

    # Check if the user has an open cash register (only for Adminf role)
    if request.user.role == 'Adminf':
        try:
            cash_register = CashRegister.objects.get(user=request.user, is_open=True)
        except CashRegister.DoesNotExist:
            messages.error(request, "Aucune caisse ouverte pour votre compte. Veuillez ouvrir une caisse.")
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home

    # Retrieve fees data
    fees = Fee.objects.filter(archived=False).order_by('-due_date')
    total_due = fees.filter(paid=False).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    total_paid = fees.filter(paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0

    context = {
        'fees': fees,
        'total_due': total_due,
        'total_paid': total_paid,
        'cash_register': cash_register if request.user.role == 'Adminf' else None,  # Pass cash_register if applicable
    }
    return render(request, 'accounting/student_fee_list.html', context)



@login_required
def add_student_fee(request):
    # Check if the user's role is 'Adminf'
    if request.user.role != 'Adminf':
        messages.error(request, "Vous n'êtes pas autorisé à effectuer cette action.")
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect back to the previous page or home if not available

    # Retrieve the current open cash register for the logged-in user
    try:
        cash_register = CashRegister.objects.get(user=request.user, is_open=True)
    except CashRegister.DoesNotExist:
        messages.error(request, "Aucune caisse ouverte pour cet utilisateur.")
        return redirect("cash_register_status")  # Redirect to cash register status page

    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            fee = form.save()

            # Update the cash register's balance
            if fee.paid:
                cash_register.update_current_balance(fee.amount_due, transaction_type="income")

            messages.success(
                request, f"Frais ajouté pour l'étudiant {fee.student.first_name} {fee.student.last_name}."
            )
            return redirect('student_fee_list')
    else:
        form = FeeForm()

    return render(request, 'accounting/add_student_fee.html', {'form': form, 'cash_register': cash_register})

@login_required
def get_student_fee_amount(request, student_id):
    """
    AJAX endpoint to retrieve the fee amount for the selected student.
    """
    student = get_object_or_404(Student, id=student_id)
    amount_due = student.get_final_fee()  # Assuming this method calculates the fee for the student
    return JsonResponse({'amount_due': amount_due})

@login_required
def edit_student_fee(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    student = fee.student
    month_name = calendar.month_name[fee.due_date.month]  # Get the full month name

    # Retrieve the current open cash register
    cash_register = CashRegister.objects.filter(user=request.user, is_open=True).first()
    if not cash_register:
        messages.error(request, "Aucune caisse ouverte. Veuillez ouvrir une caisse pour continuer.")
        return redirect("cash_register_list")

    if request.method == "POST":
        form = FeeForm(request.POST, instance=fee)
        if form.is_valid():
            old_amount = fee.amount_due
            fee = form.save()

            # Update cash register if the fee's payment status or amount changes
            if fee.paid:
                difference = fee.amount_due - old_amount
                cash_register.update_current_balance(difference, "income")
            else:
                # Revert the previous amount if unpaid
                cash_register.update_current_balance(-old_amount, "expense")

            messages.success(request, "Le frais a été mis à jour avec succès.")
            return redirect("student_fee_list")
    else:
        form = FeeForm(instance=fee)

    return render(request, "accounting/edit_student_fee.html", {
        "form": form,
        "student": student,
        "month_name": month_name.capitalize(),
    })

@login_required
def archive_student_fee(request, fee_id):
    """
    Archive a student fee and update the associated CashRegister.
    """
    fee = get_object_or_404(Fee, id=fee_id)

    # Retrieve the open cash register for the current user
    cash_register = CashRegister.objects.filter(user=request.user, is_open=True).first()
    if not cash_register:
        messages.error(request, "Aucune caisse ouverte. Veuillez ouvrir une caisse pour continuer.")
        return redirect("student_fee_list")

    if fee.paid:
        # Adjust the CashRegister balance by subtracting the archived fee amount
        cash_register.update_current_balance(-fee.amount_due, "expense")

    # Archive the fee (delete or set an archived flag)
    fee.delete()  # You can also set `fee.is_archived = True` if using a soft-delete approach.

    messages.success(request, "Le frais a été archivé avec succès et la caisse mise à jour.")
    return redirect("student_fee_list")
@login_required
def delete_student_fee(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    fee.delete()
    messages.success(request, "Le frais de l'étudiant a été supprimé avec succès.")
    return redirect('student_fee_list')
 
@login_required
def get_students_by_parent(request, parent_id):
    """
    Fetch students for a specific parent via AJAX.
    """
    students = Student.objects.filter(parents__id=parent_id).values('id', 'first_name', 'last_name')
    return JsonResponse(list(students), safe=False)

@login_required
def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Retrieve the current open cash register for the user
            try:
                cash_register = CashRegister.objects.get(user=request.user, is_open=True)
            except CashRegister.DoesNotExist:
                messages.error(request, "Aucune caisse ouverte. Impossible d'enregistrer le paiement.")
                return redirect('payment_list')  # Replace with the appropriate URL name
            
            # Update the cash register balance
            cash_register.current_balance += payment.amount
            cash_register.save()

            # Assign the cash register to the payment and save it
            payment.cash_register = cash_register
            payment.save()

            messages.success(request, 'Paiement enregistré avec succès et caisse mise à jour.')
            return redirect('payment_list')  # Replace with the appropriate URL name
    else:
        form = PaymentForm(user=request.user)

    return render(request, 'accounting/add_payment.html', {'form': form})

@login_required
def get_unpaid_months(request, student_id):
    try:
        student = Student.objects.get(pk=student_id)
        paid_months = Payment.objects.filter(
            student=student
        ).values_list('months_paid', flat=True)
        
        # Aplatir la liste des mois payés
        all_paid = set()
        for month_list in paid_months:
            if isinstance(month_list, list):
                all_paid.update(month_list)
        
        # Générer la liste des mois non payés
        unpaid_months = [
            {'value': code, 'label': name} 
            for code, name in Payment.MONTH_CHOICES 
            if code not in all_paid
        ]
        
        return JsonResponse(unpaid_months, safe=False)
    
    except Student.DoesNotExist:
        return JsonResponse([], safe=False)
@login_required    
def calculate_payment_amount(request):
    student_id = request.GET.get("student_id")
    selected_months = request.GET.get("months").split(",")

    student = get_object_or_404(Student, id=student_id)
    
    # Suppose que `monthly_fee` est le tarif mensuel de l'étudiant
    monthly_fee = student.monthly_fee  
    total_amount = len(selected_months) * monthly_fee

    return JsonResponse({"total_amount": total_amount})

@login_required
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
@login_required
def get_student_details(request, student_id):
    """
    Fetch student details including class and fee information.
    """
    try:
        student = Student.objects.select_related('student_class').get(id=student_id)
        response_data = {
            "class_name": student.student_class.name,
            "monthly_fee": student.get_final_fee(),
        }
        return JsonResponse(response_data, safe=False)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Étudiant introuvable."}, status=404)
    
def parent_search_autocomplete(request):
    query = request.GET.get('q', '')
    if query:
        parents = Parent.objects.filter(
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(nni__icontains=query)
        ).values('id', 'first_name', 'last_name', 'nni')[:10]
        results = [
            {
                'id': parent['id'],
                'name': f"{parent['first_name']} {parent['last_name']}",
                'nni': parent['nni']
            }
            for parent in parents
        ]
    else:
        results = []
    return JsonResponse(results, safe=False)