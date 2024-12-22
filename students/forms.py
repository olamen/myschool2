from django.forms import ModelForm, TextInput, Select, DateInput, Textarea
from students.models import Composition, Devoir, Trimestre

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
        fields = ['name', 'trimestre', 'exam_date', 'coefficient', 'remarks']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter composition name'}),
            'trimestre': Select(attrs={'class': 'form-control'}),
            'exam_date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'coefficient': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coefficient'}),
            'remarks': Textarea(attrs={'class': 'form-control', 'placeholder': 'Add remarks (optional)'}),
        }