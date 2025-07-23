from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from .models import Payment, Transaction, CashRegister
from .forms import ChargeTypeForm, TransactionForm
from django.contrib.auth.decorators import login_required
from .models import ChargeType


# Liste des transactions
@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    total_income = transactions.filter(transaction_type='Credit').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='Debit').aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
    }
    return render(request, 'accounting/transaction_list.html', context)


@login_required
def transaction_list_adminf(request):
    # Ensure the user has the role 'Adminf'
    if request.user.role != 'Adminf':
        print("view transaction_list_adminf you are not permised")
        return render(request, "403.html")  # Render a '403 Forbidden' page or similar

    # Filter transactions for the current user
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Calculate totals
    total_income = transactions.filter(transaction_type='Credit').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='Debit').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
    }
    return render(request, 'accounting/transaction_list.html', context)


@login_required
def add_or_update_transaction(request):
    if request.user.role != 'Adminf':
        return render(request, "403.html")  # Render a '403 Forbidden' page or similar
    transaction = None  # Default: No transaction (creating a new one)
    transaction_id = request.POST.get("transaction_id") or request.GET.get("transaction_id")
    if transaction_id:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        form = TransactionForm(request.POST or None, instance=transaction)
    else:
        form = TransactionForm(request.POST or None)

    if request.method == 'POST':
        transaction_id = request.POST.get("transaction_id")  # Extract ID from form

        if transaction_id:  # If an ID is provided, update existing transaction
            transaction = get_object_or_404(Transaction, id=transaction_id)
            if transaction.user != request.user:
                messages.error(request, "Vous n'avez pas la permission de modifier cette transaction.")
                return redirect('transaction_list')
            form = TransactionForm(request.POST, instance=transaction)

        if form.is_valid():
            transaction = form.save(commit=False)

            # Récupérer la caisse ouverte pour l'utilisateur
            try:
                cash_register = CashRegister.objects.get(user=request.user, is_open=True)
            except CashRegister.DoesNotExist:
                messages.error(request, "Impossible d'ajouter ou de modifier une transaction : aucune caisse ouverte pour votre compte.")
                return redirect('transaction_list')

            # Vérification du solde de la caisse avant la transaction
            if transaction.transaction_type == 'Debit':  # Dépense
                if cash_register.current_balance < transaction.amount:
                    messages.error(request, f"Le solde de la caisse est insuffisant ({cash_register.current_balance:.2f} MRU).")
                    return redirect('add_or_update_transaction')
                cash_register.current_balance -= transaction.amount
            elif transaction.transaction_type == 'Credit':  # Revenu
                cash_register.current_balance += transaction.amount

            # Sauvegarder modifications
            cash_register.save()
            transaction.cash_register = cash_register
            transaction.user = request.user
            transaction.save()

            messages.success(request, "Transaction mise à jour avec succès." if transaction_id else "Transaction ajoutée avec succès.")
            return redirect('transaction_list')

    return render(request, 'accounting/add_or_update_transaction.html', {'form': form, 'transaction': transaction})



# Détails d'une transaction
@login_required
def transaction_details(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'accounting/transaction_details.html', {'transaction': transaction})


@login_required
def print_transaction_receipt(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Vérifier que l'utilisateur a le droit de voir cette transaction
    if transaction.user != request.user:
        print("Vous n'avez pas la permission d'imprimer ce reçu.")
        messages.error(request, "Vous n'avez pas la permission d'imprimer ce reçu.")
        return redirect('transaction_list')
    # Determine the type of receipt
    receipt_type = "Original" if transaction.is_original else "Copy"
    
    # Update the transaction to mark it as printed
    if transaction.is_original:
        transaction.is_original = False
        transaction.save()
    
    # Rendre une page HTML comme reçu
    context = {
        'transaction': transaction,
        "receipt_type": receipt_type,
        'cashier': request.user.get_full_name(),  # Nom complet du caissier
        'school_name': settings.SCHOOL_NAME,      # Nom de l'école
        "thank_you_message": "Merci pour votre confiance.",
    }
    return render(request, 'accounting/transaction_receipt.html', context)




@login_required
def transactions_by_month(request):
    today = now()
    start_date = today - timedelta(days=365)

    transactions = (
        Transaction.objects.filter(date__gte=start_date, date__lte=today)
        .values('date__month', 'date__year', 'transaction_type')
        .annotate(total_amount=Sum('amount'))
        .order_by('date__year', 'date__month')
    )

    payments = (
        Payment.objects.filter(date__gte=start_date, date__lte=today)
        .values('date__month', 'date__year')
        .annotate(total_amount=Sum('amount'))
        .order_by('date__year', 'date__month')
    )

    MONTH_MAP = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
    7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    # Ensure months appear even when no transactions exist
    months = [MONTH_MAP[m] for m in range(1, 13)]
    income_data = [0] * 12
    expense_data = [0] * 12

    # Populate with existing transaction data
    for transaction in transactions:
        month_index = transaction['date__month'] - 1  # Adjust for zero-based indexing
        if transaction['transaction_type'] == 'Credit':
            income_data[month_index] += float(transaction['total_amount'])
        elif transaction['transaction_type'] == 'Debit':
            expense_data[month_index] += float(transaction['total_amount'])

    # Populate payments into `income_data`
    for payment in payments:
        month_index = payment['date__month'] - 1
        income_data[month_index] += float(payment['total_amount'])


        # Populate with existing transaction data
    for transaction in transactions:
        month_index = transaction['date__month'] - 1  # Adjust for zero-based indexing
        if transaction['transaction_type'] == 'Credit':
            income_data[month_index] += float(transaction['total_amount'])
        elif transaction['transaction_type'] == 'Debit':
            expense_data[month_index] += float(transaction['total_amount'])

    # Populate payments into `income_data`
    for payment in payments:
        month_index = payment['date__month'] - 1
        income_data[month_index] += float(payment['total_amount'])

    return JsonResponse({"months": months, "income_data": income_data, "expense_data": expense_data})




# charge_from view
@login_required
def charge_form(request):
    if request.user.role != 'Adminf':
        return render(request, "403.html")  # Render a '403 Forbidden' page or similar
    charge = None
    form = ChargeTypeForm(request.POST or None)
    charges = ChargeType.objects.all()

    if request.method == 'POST':
        charge_id = request.POST.get("charge_id")  # Extract ID from form data

        if charge_id:  # If ID is provided, update existing record
            charge = get_object_or_404(ChargeType, id=charge_id)
            form = ChargeTypeForm(request.POST, instance=charge)
        else:  # Otherwise, create a new record
            form = ChargeTypeForm(request.POST)

        if form.is_valid():
            charge = form.save(commit=False)
            charge.save()
            messages.success(request, "Charge mise à jour avec succès." if charge_id else "Charge ajoutée avec succès.")
            return redirect('charge_form')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    return render(request, 'accounting/charges/charge_form.html', {'form': form, 'charge': charge, 'charges': charges})
# charge_list view
@login_required
def charge_list(request):
    charges = ChargeType.objects.all()
    return render(request, 'accounting/charges/charge_list.html', {'charges': charges})

@login_required
def charge_delete(request, charge_id):
    if request.user.role != 'Adminf':
        print("view transaction_list_adminf you are not permised")
        return render(request, "403.html")  # Render a '403 Forbidden' page or similar
    charge = get_object_or_404(ChargeType, id=charge_id)
    charge.delete()
    messages.success(request, "Charge supprimée avec succès.")
    return redirect('charge_form')
