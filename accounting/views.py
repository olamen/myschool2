from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from Auth.models import CustomUser
from students.models import Classe, Parent
from .models import  Expense, Fee, Payment
from accounting import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CashRegister, Transaction, StudentFee
from .forms import CashRegisterForm, TransactionForm, StudentFeeForm


def calculate_parent_fees(parent_id, classe_id):
    try:
        parent = Parent.objects.get(id=parent_id)
        classe = Classe.objects.get(id=classe_id)

        total_fees = 0
        children_details = []

        for child in parent.children.filter(student_class=classe):
            discount = 0.2 if child.has_discount else 0
            fee = child.student_class.monthly_salary_fee
            final_fee = fee - (fee * discount)
            total_fees += final_fee

            children_details.append({
                "name": f"{child.first_name} {child.last_name}",
                "fee": final_fee,
                "discount": "Yes" if discount > 0 else "No"
            })

        return {
            "parent_name": f"{parent.first_name} {parent.last_name}",
            "class_name": classe.name,
            "children": children_details,
            "total_fees": total_fees
        }
    except Parent.DoesNotExist:
        raise ValueError("Parent not found.")
    except Classe.DoesNotExist:
        raise ValueError("Class not found.")

def parent_fees_view(request, parent_id, classe_id):
    parent = get_object_or_404(Parent, id=parent_id)
    classe = get_object_or_404(Classe, id=classe_id)

    fee_details = calculate_parent_fees(parent_id, classe_id)

    return render(request, "accounting/parent_fees.html", {
        "fee_details": fee_details
    })


# older
# Vue du tableau de bord
@login_required
def index(request):
    # Statistiques fictives (à remplacer par vos données réelles)
    monthly_payments = Payment.objects.filter(status="Paid").aggregate(total=models.Sum("amount_paid"))["total"] or 0
    total_expenses = Expense.objects.aggregate(total=models.Sum("amount"))["total"] or 0
    cash_register = CashRegister.objects.filter(is_open=True).first()
    transactions = Transaction.objects.filter(cash_register=cash_register).order_by("-date") if cash_register else []

    context = {
        "cash_register": cash_register,
        "transactions": transactions,
        "monthly_payments": monthly_payments,
        "total_expenses": total_expenses,
    }
    return render(request,'accounting/dash.html',context)


def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'accounting/expense_list.html', {'expenses': expenses})



# Vue pour ouvrir la caisse
@login_required
def open_cash_register(request):
    # Ensure only users with the 'Adminf' role can access this functionality
    if request.user.role != 'Adminf':
        messages.error(request, "Seuls les administrateurs financiers (Adminf) peuvent ouvrir une caisse.")
        return redirect("home")  # Replace 'home' with the appropriate redirect URL

    if request.method == "POST":
        opening_balance = float(request.POST.get("initial_balance", 0.0))
        try:
            # Create a new cash register for the user
            CashRegister.objects.create(
                initial_balance=opening_balance,
                current_balance=opening_balance,
                is_open=True,
                user=request.user,
            )
            messages.success(request, "Caisse ouverte avec succès.")
            return redirect("cash_register_status")  # Replace with the correct URL name
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, "accounting/cash_register/open.html")


# Vue pour fermer la caisse
@login_required
def close_cash_register(request, register_id):
    """
    Close an open cash register for the logged-in user.
    """
    cash_register = get_object_or_404(CashRegister, id=register_id, is_open=True)

    if request.method == "POST":
        try:
            # Update the cash register state
            cash_register.is_open = False
            cash_register.closing_balance = cash_register.current_balance
            cash_register.user = request.user  # Ensure the user field is set correctly
            cash_register.save()

            messages.success(request, "Caisse fermée avec succès.")
            return redirect("cash_register_status")  # Replace with the appropriate URL name
        except Exception as e:
            messages.error(request, f"Erreur lors de la fermeture de la caisse : {e}")
            return redirect("cash_register_status")

    return render(request, "accounting/cash_register/close.html", {"cash_register": cash_register})


# Vue pour afficher l'état de la caisse
@login_required
def cash_register_status(request):
    cash_register = CashRegister.objects.get(user=request.user, is_open=True)
    if not cash_register:
        messages.error(request, "Aucune caisse ouverte actuellement pour se compte.")
        return redirect("indexaccounting")
    return render(request, "accounting/cash_register/status.html", {"cash_register": cash_register})

@login_required
def cash_register_list(request):
    cash_registers = CashRegister.objects.all().order_by("-id") 
    return render(request, "accounting/cash_register/list.html", {"cash_registers": cash_registers})

@login_required
def cash_register_list_byuser(request):
    cash_registers = CashRegister.objects.filter(user=request.user).order_by("-id") 
    return render(request, "accounting/cash_register/list.html", {"cash_registers": cash_registers})

@login_required
def cash_register_details(request, pk):
    cash_register = get_object_or_404(CashRegister, pk=pk)
    transactions = Transaction.objects.filter(cash_register=cash_register).order_by("-date")

    context = {
        "cash_register": cash_register,
        "transactions": transactions,
    }
    return render(request, "cash_register/details.html", context)
# Vue pour enregistrer une transaction
@login_required
def create_transaction(request):
    try:
        cash_register = CashRegister.objects.get(is_open=True)
    except CashRegister.DoesNotExist:
        messages.error(request, "Vous devez ouvrir une caisse avant de créer une transaction.")
        return redirect("dashboard")

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.cash_register = cash_register
            transaction.save()
            messages.success(request, "Transaction enregistrée avec succès.")
            return redirect("cash_register_status")
    else:
        form = TransactionForm()
    return render(request, "transactions/create.html", {"form": form})


# Vue pour afficher l'historique des transactions
@login_required
def transaction_history(request):
    transactions = Transaction.objects.select_related("cash_register").order_by("-date")
    return render(request, "transactions/history.html", {"transactions": transactions})


# Vue pour gérer les paiements des frais étudiants
@login_required
def manage_student_fees(request):
    try:
        cash_register = CashRegister.objects.get(is_open=True)
    except CashRegister.DoesNotExist:
        messages.error(request, "Vous devez ouvrir une caisse avant de gérer les frais.")
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentFeeForm(request.POST)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.cash_register = cash_register
            if fee.is_paid:
                fee.payment_date = form.cleaned_data.get("payment_date")
            fee.save()
            messages.success(request, "Frais étudiant mis à jour avec succès.")
            return redirect("manage_student_fees")
    else:
        form = StudentFeeForm()
    student_fees = StudentFee.objects.select_related("student").order_by("due_date")
    return render(request, "fees/manage.html", {"form": form, "student_fees": student_fees})





