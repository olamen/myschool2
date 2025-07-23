import datetime
from django.forms import CheckboxInput, ModelForm, NumberInput, TextInput, Select, DateInput, Textarea
from django.urls import  reverse_lazy
from students.models import Classe, Composition, Devoir, Trimestre
from django import forms
from .models import Student, Teacher, Assignment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django.utils.translation import gettext_lazy as _


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'nni', 'mobile', 'student_class', 'has_discount', 'gender', 'photo', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter last name'}),
            'nni': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter NNI'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter mobile'}),
            'student_class': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'has_discount': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'gender': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'photo': forms.FileInput(attrs={'class': 'form-control form-control-lg'}),
            'bio': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'rows': 4, 'placeholder': 'Enter bio'}),
        }
        registration_fee = forms.DecimalField(
            initial=10000, 
            disabled=True, 
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['student_class'].queryset = Classe.objects.all() # Assuming you have a Classe model

    
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['classroom', 'title', 'description', 'file', 'due_date', 'is_active']
        widgets = {
            'classroom': Select(attrs={'class': 'form-control'}),
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter assignment title')}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter assignment description')}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
            'due_date': DateInput(attrs={'class': 'form-control', 'type': 'date', 'max':datetime.date.today()}),
        }
        labels = {
            'classroom': _('Classroom'),
            'title': _('Title'),
            'description': _('Description'),
            'file': _('File'),
            'due_date': _('Due Date'),
            'is_active': _('Is Active'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('upload_assignment')
        self.helper.layout = Layout(
            Fieldset(
                _('Assignment Details'),
                'classroom',
                'title',
                'description',
                'file',
                'due_date',
                'is_active',
            ),
            ButtonHolder(
                Submit('submit', _('Submit'), css_class='btn btn-success')
            )
        )

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['subject', 'classes','photo', 'name', 'nni','telephone','enrollment_date', 'salary', 'salary_type', 'is_active']
        widgets = {
            'subject': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'classes': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'name': TextInput(attrs={'class': 'form-control'}),
            'nni': TextInput(attrs={'class': 'form-control','hx-get': reverse_lazy('check_nni'), 'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#nni_response'}),
            'telephone': TextInput(attrs={'class': 'form-control'}),
            'enrollment_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'subject': _('Subject'),
            'classes': _('Classes'),
            'photo': _('Photo'),
            'name': _('Name'),
            'nni': _('NNI'),
            'telephone': _('Telephone'),
            'enrollment_date': _('Enrollment Date'),
            'salary': _('Salary'),
            'salary_type': _('Salary Type'),
            'is_active': _('Is Active'),
        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper(self)
            self.helper.form_action = reverse_lazy('teacher_create')
            self.helper.layout = Layout(
                Fieldset(
                    _('Teacher Details'),
                    'subject',
                    'classes',
                    'photo',
                    'name',
                    'nni',
                    'telephone',
                    'enrollment_date',
                    'salary',
                    'salary_type',
                    'is_active'
                ),
                ButtonHolder(
                    Submit(_('Submit'), _('Submit'), css_class='btn btn-success')
                )
            )
        

class TrimestreForm(ModelForm):
    class Meta:
        model = Trimestre
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter trimester name')}),
        }
        labels = {
            'name': _('Name'),
        }

class DevoirForm(ModelForm):
    class Meta:
        model = Devoir
        fields = ['name', 'trimestre','date', 'description', 'coefficient']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter homework name')}),
            'trimestre': Select(attrs={'class': 'form-control'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter homework description')}),
            'coefficient': TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter coefficient')}),
        }
        labels = {
            'name': _('Name'),
            'trimestre': _('Trimester'),
            'date': _('Date'),
            'description': _('Description'),
            'coefficient': _('Coefficient'),
        }

class CompositionForm(ModelForm):
    class Meta:
        model = Composition
        fields = ['name', 'trimestre', 'exam_date', 'remarks', 'coefficient']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter le nom')}),
            'trimestre': Select(attrs={'class': 'form-control'}),
            'exam_date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter une remarks ')}),
            'coefficient': TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter coefficient')}),
        }
        labels = {
            'name': _('Name'),
            'trimestre': _('Trimester'),
            'exam_date': _('Exam Date'),
            'remarks': _('Remarks'),
            'coefficient': _('Coefficient'),
        }

class ClasseForm(ModelForm):
    class Meta:
        model = Classe
        fields = ['name', 'grade', 'monthly_salary_fee', 'order', 'is_active']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom de la classe')}),
            'grade': Select(attrs={'class': 'form-select'}),
            'monthly_salary_fee': NumberInput(attrs={'class': 'form-control', 'placeholder': _('Frais mensuels')}),
            'order': NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ordre')}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': _('Name'),
            'grade': _('Grade'),
            'monthly_salary_fee': _('Monthly Salary Fee'),
            'order': _('Order'),
            'is_active': _('Is Active'),
        }