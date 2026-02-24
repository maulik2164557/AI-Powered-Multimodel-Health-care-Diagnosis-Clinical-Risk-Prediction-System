from django.utils import timezone
from django import forms
from .models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()


class AppointmentForm(forms.ModelForm):

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )

    message = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Short reason for visit',
            'class': 'form-control'
        })
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe your symptoms...',
            'class': 'form-control',
            'rows': 4
        })
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'message', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 Only show doctors
        self.fields['doctor'].queryset = User.objects.filter(role='DOCTOR')

        self.fields['doctor'].widget.attrs.update({
            'class': 'form-control'
        })

    from django.utils import timezone

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError("You cannot book an appointment in the past.")
        return date

