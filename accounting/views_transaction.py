from django.conf import settings
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
            
            # Récupérer la caisse ouverte pour l'utilisateur
            try:
                cash_register = CashRegister.objects.get(user=request.user, is_open=True)
            except CashRegister.DoesNotExist:
                messages.error(request, "Impossible d'ajouter une transaction : aucune caisse ouverte pour votre compte.")
                return redirect('transaction_list')
            
            # Vérification pour maintenir un solde positif
            if transaction.transaction_type == 'Debit':  # Dépense
                if cash_register.current_balance < transaction.amount:
                    messages.error(request, "Le solde de la caisse est insuffisant pour cette dépense. Solde actuel : {:.2f} MRU".format(cash_register.current_balance))
                    return redirect('add_transaction')
                cash_register.current_balance -= transaction.amount
            elif transaction.transaction_type == 'Credit':  # Revenu
                cash_register.current_balance += transaction.amount
            
            # Sauvegarder les modifications
            cash_register.save()
            transaction.cash_register = cash_register
            transaction.user = request.user  # Lier l'utilisateur actuel à la transaction
            transaction.save()

            messages.success(request, "Transaction ajoutée avec succès.")
            return redirect('transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'accounting/add_transaction.html', {'form': form})


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