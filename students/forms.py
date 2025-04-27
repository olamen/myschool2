from django.forms import CheckboxInput, ModelForm, NumberInput, TextInput, Select, DateInput, Textarea
from students.models import Classe, Composition, Devoir, Trimestre
from django import forms
from .models import Teacher

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['subject', 'photo', 'name', 'nni','telephone','enrollment_date', 'salary', 'salary_type', 'is_active']
        widgets = {
            'subject': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'nni': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TrimestreForm(ModelForm):
    class Meta:
        model = Trimestre
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter trimester name'}),
        }

class DevoirForm(ModelForm):
    class Meta:
        model = Devoir
        fields = ['name', 'trimestre', 'classe', 'subject', 'date', 'description', 'coefficient']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter homework name'}),
            'trimestre': Select(attrs={'class': 'form-control'}),
            'classe': Select(attrs={'class': 'form-control'}),
            'subject': Select(attrs={'class': 'form-control'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter homework description'}),
            'coefficient': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coefficient'}),
        }

class CompositionForm(ModelForm):
    class Meta:
        model = Composition
        fields = ['name', 'trimestre', 'classe', 'subject', 'exam_date', 'remarks', 'coefficient']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter le nom'}),
            'trimestre': Select(attrs={'class': 'form-control'}),
            'classe': Select(attrs={'class': 'form-control'}),
            'subject': Select(attrs={'class': 'form-control'}),
            'exam_date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter une remarks '}),
            'coefficient': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coefficient'}),
        }

class ClasseForm(ModelForm):
    class Meta:
        model = Classe
        fields = ['name', 'grade', 'monthly_salary_fee', 'order', 'is_active']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la classe'}),
            'grade': Select(attrs={'class': 'form-select'}),
            'monthly_salary_fee': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Frais mensuels'}),
            'order': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ordre'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        