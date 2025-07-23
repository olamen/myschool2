from django import forms
from django.urls import reverse_lazy
from .models import CashRegister, ChargeType, Fee, Payment, Transaction, StudentFee
from students.models import  Classe, Parent, Student
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'nni', 'mobile', 'student_class', 'has_discount', 'gender', 'photo']
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'nni': _('NNI'),
            'mobile': _('Mobile'),
            'student_class': _('Class'),
            'has_discount': _('Has Discount'),
            'gender': _('Gender'),
            'photo': _('Photo'),
        }
    # Fixed registration fee
    registration_fee = forms.DecimalField(
        initial=10000, 
        disabled=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_class'].queryset = Classe.objects.all() # Assuming you have a Classe model
        
class CashRegisterForm(forms.ModelForm):
    """
    Form to open a cash register with an initial balance.
    """
    class Meta:
        model = CashRegister
        fields = ['initial_balance']
        widgets = {
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Opening Balance'),
                'min': '0'
            }),
        }
        labels = {
            'initial_balance': _('Opening Balance'),
        }


class TransactionForm(forms.ModelForm):
    """
    Form to record a transaction.
    """
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'chargetype','amount', 'description']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'chargetype': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Amount'),
                'min': '0',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Transaction description (optional)'),
                'rows': 3,
            }),
            
        }
        labels = {
            'chargetype': _('Charge Type'),
            'transaction_type': _('Transaction Type'),
            'amount': _('Amount'),
            'description': _('Description'),
        }


class StudentFeeForm(forms.ModelForm):
    """
    Form to manage student fees.
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
                'placeholder': _('Amount Due'),
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
            'student': _('Student'),
            'amount': _('Amount Due'),
            'due_date': _('Due Date'),
            'is_paid': _('Paid?'),
            'payment_date': _('Payment Date'),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_paid = cleaned_data.get('is_paid')
        payment_date = cleaned_data.get('payment_date')

        if is_paid and not payment_date:
            raise forms.ValidationError(_("Please specify a payment date for paid fees."))
        return cleaned_data
    
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'amount_due', 'due_date', 'paid']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        parent = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Search Parent...')}),
        required=False,
        label=_('Parent')
    )
        labels = {
            'student': _('Student'),
            'amount_due': _('Amount Due'),
            'due_date': _('Due Date'),
            'paid': _('Paid'),
        }
        widgets = {
            'parent': forms.Select(attrs={
                'class': 'form-control parent-select',
                'data-ajax-url': reverse_lazy('parent_search_autocomplete')
            }),
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




class PaymentForm(forms.ModelForm):
    months_paid = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Months to be paid"),
    )

    class Meta:
        model = Payment
        fields = [
            # 'cash_register',
            'student',
            'parent',
            'classe',
            'months_paid',
            'amount',
            'method',
            'notes',
        ]
        widgets = {
            # 'cash_register': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'readonly': 'readonly'
            # }),
            'student': forms.Select(attrs={'class': 'form-control'}),
            # 'student': forms.Select(attrs={
            #     'class': 'form-control',
            #     'disabled': 'disabled'
            # }),
            'parent': forms.Select(attrs={
                'class': 'form-control parent-select',
                'data-ajax-url': reverse_lazy('parent_search_autocomplete')
            }),
            # 'classe': forms.Select(attrs={
            #     'class': 'form-control',
            #     'disabled': 'disabled'
            # }),
            'classe': forms.HiddenInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Amount')
            }),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Notes (optional)')
            }),
        }
        labels = {
            # 'cash_register': _('Cash Register'),
            'student': _('Student'),
            'parent': _('Parent'),
            'classe': _('Class'),
            'amount': _('Amount'),
            'method': _('Payment Method'),
            'notes': _('Notes'),
        }

        # Add a separate field for displaying cash register info, not for submission
    cash_register_display = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False,
        label=_("Cash Register")
    )
        
   #     # Initialize the form with dynamic data
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Parent.objects.all()
        self.fields['student'].queryset = Student.objects.all()

        
        # Dynamic initialization of the cash register
        if user:
            try:
                cash_register = CashRegister.objects.get(user=user, is_open=True)
                self.fields['cash_register_display'].initial = _("Open Cash Register - %(balance)s MRU") % {
                    'balance': cash_register.current_balance
                }
            except CashRegister.DoesNotExist:
                self.fields['cash_register_display'].initial = _("No open cash register")
        else:
            # If no user, set initial for display field as well
            self.fields['cash_register_display'].initial = _("No user provided")

        # Initialization of paid months
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
        student = cleaned_data.get('student') # student is already a Student object here
        parent = cleaned_data.get('parent')

        print("Raw student data from form:", student) # This will print the Student object

        if not student and not parent:
            raise forms.ValidationError("Select a student or parent.")

        # If student is selected, it's already a valid Student object due to ModelForm's handling
        # No need to re-validate existence or get it again by ID.

        # Auto-set classe if student is selected
        if student: # Check if student object exists
            cleaned_data['classe'] = student.student_class # Assign the class object directly
                                                          # Or student.student_class.id if 'classe' expects an ID

        months_paid = cleaned_data.get('months_paid', [])
        # Ensure months_paid is stored as a JSONField if 'months_paid' on Payment model is JSONField
        # Or if it's a CharField/TextField, ensure the format matches what your model expects
        # If your Payment model's months_paid is a JSONField, this format is usually correct:
        cleaned_data['months_paid'] = {month: 'paid' for month in months_paid}
        # If your Payment model's months_paid expects a list/array for MultipleChoiceField,
        # then the line below would be sufficient, but based on your `cleaned_data['months_paid'] = {month: 'paid' for month in months_paid}`
        # it seems like you're storing it as a dict/JSON. Ensure your model field matches.
        # cleaned_data['months_paid'] = months_paid


        return cleaned_data





#ChargeType forms
class ChargeTypeForm(forms.ModelForm):
    class Meta:
        model = ChargeType
        fields = ['name', 'amount', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name'),
            'amount': _('Amount'),
            'description': _('Description'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('charge_from', args=[self.instance.pk])
        self.helper.layout = Layout(
            Fieldset(
                _('Charge Type Details'),
                'name',
                'amount',
                'description',
            ),
            ButtonHolder(
                Submit('submit', _('Save'), css_class='btn btn-primary')
            )
        )

