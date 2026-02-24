from django import forms
from .models import MedicalLog, MedicalDocument


class MedicalLogForm(forms.ModelForm):
    class Meta:
        model = MedicalLog
        fields = ['title', 'description']


class MedicalDocumentForm(forms.ModelForm):
    class Meta:
        model = MedicalDocument
        fields = ['title', 'file']