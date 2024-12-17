from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from .models import Transaction, CashRegister
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required


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


# Ajouter une transaction
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            
            # Retrieve the open cash register for the current user
            try:
                cash_register = CashRegister.objects.get(user=request.user, is_open=True)
            except CashRegister.DoesNotExist:
                messages.error(request, "Impossible d'ajouter une transaction : aucune caisse ouverte pour votre compte.")
                return redirect('accounting:transaction_list')
            
            # Debugging: Print the current cash register balance and transaction amount
            print(f"Cash Register Balance: {cash_register.current_balance}")
            print(f"Transaction Amount: {transaction.amount}")
            print(f"Transaction Type: {transaction.transaction_type}")

            # Check the transaction type and update cash register balance
            if transaction.transaction_type == 'income':
                cash_register.current_balance += transaction.amount
            elif transaction.transaction_type == 'expense':
                if cash_register.current_balance >= transaction.amount:
                    cash_register.current_balance -= transaction.amount
                else:
                    messages.error(request, "Pas assez d'argent dans la caisse pour cette dépense.")
                    return redirect('accounting:add_transaction')

            # Save the updated cash register and transaction
            cash_register.save()
            transaction.cash_register = cash_register
            transaction.user = request.user  # Assign the current user to the transaction
            transaction.save()

            messages.success(request, "Transaction ajoutée avec succès.")
            return redirect('accounting:transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'accounting/add_transaction.html', {'form': form})


# Détails d'une transaction
@login_required
def transaction_details(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'accounting/transaction_details.html', {'transaction': transaction})