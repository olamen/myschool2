from django.forms import CheckboxInput, ModelForm, NumberInput, TextInput, Select, DateInput, Textarea
from students.models import Classe, Composition, Devoir, Trimestre

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