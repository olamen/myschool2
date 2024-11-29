from django import forms
from .models import CashRegister, Fee, Transaction, StudentFee
from students.models import Student

class CashRegisterForm(forms.ModelForm):
    """
    Formulaire pour ouvrir une caisse avec un solde initial.
    """
    class Meta:
        model = CashRegister
        fields = ['opening_balance']
        widgets = {
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Solde d\'ouverture',
                'min': '0'
            }),
        }
        labels = {
            'opening_balance': 'Solde d\'ouverture',
        }


class TransactionForm(forms.ModelForm):
    """
    Formulaire pour enregistrer une transaction.
    """
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant',
                'min': '0',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description de la transaction (optionnel)',
                'rows': 3,
            }),
        }
        labels = {
            'transaction_type': 'Type de transaction',
            'amount': 'Montant',
            'description': 'Description',
        }


class StudentFeeForm(forms.ModelForm):
    """
    Formulaire pour gérer les frais des étudiants.
    """
    class Meta:
        model = StudentFee
        fields = ['student', 'amount', 'due_date', 'is_paid', 'payment_date']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant dû',
                'min': '0',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'student': 'Étudiant',
            'amount_due': 'Montant dû',
            'due_date': 'Date d\'échéance',
            'is_paid': 'Payé ?',
            'payment_date': 'Date de paiement',
        }

    def clean(self):
        cleaned_data = super().clean()
        is_paid = cleaned_data.get('is_paid')
        payment_date = cleaned_data.get('payment_date')

        if is_paid and not payment_date:
            raise forms.ValidationError("Veuillez spécifier une date de paiement pour les frais payés.")
        return cleaned_data
    
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'amount_due', 'due_date', 'paid']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }