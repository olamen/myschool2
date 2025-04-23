from django import forms
from django.urls import reverse_lazy
from .models import CashRegister, Fee, Payment, Transaction, StudentFee
from students.models import Classe, Parent, Student

class CashRegisterForm(forms.ModelForm):
    """
    Formulaire pour ouvrir une caisse avec un solde initial.
    """
    class Meta:
        model = CashRegister
        fields = ['initial_balance']
        widgets = {
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Solde d\'ouverture',
                'min': '0'
            }),
        }
        labels = {
            'initial_balance': 'Solde d\'ouverture',
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
        labels = {
            'student': 'Étudiant',
            'amount_due': 'Montant dû',
            'due_date': 'Date d\'échéance',
            'paid': 'Payé',
        }
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'amount_due': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        def __init__(self, *args, **kwargs):
            super(FeeForm, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'form-check-input'  # For checkboxes
                else:
                    field.widget.attrs['class'] = 'form-control form-control-lg'  # For other inputs

from django import forms
from .models import Payment, Student, Parent, Classe, CashRegister

from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

class PaymentForm(forms.ModelForm):
    months_paid = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Mois à payer")
    )

    class Meta:
        model = Payment
        fields = [
            'cash_register',
            'student',
            'parent',
            'classe',
            'months_paid',
            'amount',
            'method',
            'notes',
        ]
        widgets = {
            'cash_register': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'student': forms.Select(attrs={
                'class': 'form-control',
                'disabled': 'disabled'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control parent-select',
                'data-ajax-url': reverse_lazy('parent_search_autocomplete')
            }),
            'classe': forms.Select(attrs={
                'class': 'form-control',
                'disabled': 'disabled'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Montant')
            }),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Notes (facultatif)')
            }),
        }
        labels = {
            'cash_register': _('Caisse'),
            'student': _('Étudiant'),
            'parent': _('Parent'),
            'classe': _('Classe'),
            'amount': _('Montant'),
            'method': _('Méthode de paiement'),
            'notes': _('Notes'),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Parent.objects.none()
        self.fields['student'].queryset = Student.objects.none()
        
        # Initialisation dynamique de la caisse
        if user:
            try:
                cash_register = CashRegister.objects.get(user=user, is_open=True)
                self.fields['cash_register'].initial = _("Caisse ouverte - %(balance)s MRU") % {
                    'balance': cash_register.current_balance
                }
            except CashRegister.DoesNotExist:
                self.fields['cash_register'].initial = _("Aucune caisse ouverte")

        # Initialisation des mois payés
        if self.instance and self.instance.pk:
            student = self.instance.student
            if student:
                paid_months = Payment.objects.filter(student=student)\
                    .exclude(pk=self.instance.pk)\
                    .values_list('months_paid', flat=True)
                
                paid_months = {month for sublist in paid_months for month in sublist}
                self.fields['months_paid'].choices = [
                    (code, name) 
                    for code, name in Payment.MONTH_CHOICES 
                    if code not in paid_months
                ]
        else:
            self.fields['months_paid'].choices = Payment.MONTH_CHOICES

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        parent = cleaned_data.get('parent')
        classe = cleaned_data.get('classe')

        # Validation: Au moins un des trois champs doit être rempli
        if not any([student, parent, classe]):
            raise forms.ValidationError(
                _("Vous devez sélectionner au moins un étudiant, un parent ou une classe.")
            )

        return cleaned_data