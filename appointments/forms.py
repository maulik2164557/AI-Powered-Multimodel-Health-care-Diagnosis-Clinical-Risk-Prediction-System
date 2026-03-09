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
            'class': 'form-control',
            # 15 minutes slot step (900 seconds)
            'step': '900',
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

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if time:
            # Enforce 15-minute consultation slots
            if (time.minute % 15) != 0 or time.second != 0 or time.microsecond != 0:
                raise forms.ValidationError(
                    "Consultation slots are 15 minutes. Please choose a time like 10:00, 10:15, 10:30, 10:45."
                )

        if doctor and date and time:
            # Slot is considered occupied if there is any non-cancelled/rejected appointment
            slot_taken = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=time,
            ).exclude(status__in=['cancelled', 'rejected']).exists()

            if slot_taken:
                raise forms.ValidationError(
                    "This slot is already booked. Please select another date or time."
                )

        return cleaned_data

