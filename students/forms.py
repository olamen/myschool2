# Forms
from django.forms import ModelForm

from students.models import Composition, Devoir, Trimestre


class TrimestreForm(ModelForm):
    class Meta:
        model = Trimestre
        fields = ['name']

class DevoirForm(ModelForm):
    class Meta:
        model = Devoir
        fields = ['name', 'trimestre', 'classe', 'subject', 'date', 'description', 'coefficient']

class CompositionForm(ModelForm):
    class Meta:
        model = Composition
        fields = ['name', 'trimestre', 'exam_date', 'coefficient', 'remarks']