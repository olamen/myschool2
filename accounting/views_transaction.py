from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from .models import Transaction, CashRegister
from .forms import TransactionForm

# Liste des transactions
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


# Ajouter une transaction
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
           # cash_register = CashRegister.objects.filter(is_open=True).first()
            cash_register = CashRegister.objects.get(user=request.user, is_open=True)

            if not cash_register:
                messages.error(request, "Impossible d'ajouter une transaction : la caisse est fermée.")
                return redirect('accounting:transaction_list')

            # Mettre à jour le solde de la caisse
            if transaction.transaction_type == 'income':
                cash_register.current_balance += transaction.amount
            elif transaction.transaction_type == 'expense':
                if cash_register.current_balance >= transaction.amount:
                    cash_register.current_balance -= transaction.amount
                else:
                    messages.error(request, "Le solde de la caisse est insuffisant pour cette dépense.")
                    return redirect('accounting:add_transaction')

            cash_register.save()
            transaction.cash_register = cash_register
            transaction.user = request.user  # Set the user field
            transaction.save()

            messages.success(request, "Transaction ajoutée avec succès.")
            return redirect('transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'accounting/add_transaction.html', {'form': form})


# Détails d'une transaction
def transaction_details(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'accounting/transaction_details.html', {'transaction': transaction})