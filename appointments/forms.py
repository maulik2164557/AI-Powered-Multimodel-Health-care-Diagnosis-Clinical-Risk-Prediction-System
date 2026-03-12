from django.utils import timezone
from django import forms
from .models import Appointment
from django.contrib.auth import get_user_model
import datetime

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
            'step': '900'  # 15 minute slot
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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Show only doctors
        self.fields['doctor'].queryset = User.objects.filter(
            role='DOCTOR'
        ).order_by('first_name')

        self.fields['doctor'].widget.attrs.update({
            'class': 'form-control'
        })

    def clean(self):
        cleaned_data = super().clean()

        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if not (doctor and date and time):
            return cleaned_data

        # Combine date + time
        appointment_datetime = datetime.datetime.combine(date, time)
        appointment_datetime = timezone.make_aware(appointment_datetime)

        now = timezone.now()

        # 1️⃣ Appointment must be strictly in the future
        if appointment_datetime <= now:
            raise forms.ValidationError(
                "Appointments must be scheduled for a future date and time."
            )

        # 2️⃣ Limit booking to 30 days ahead
        max_date = timezone.localdate() + datetime.timedelta(days=30)

        if date > max_date:
            raise forms.ValidationError(
                "Appointments can only be booked up to 30 days in advance."
            )

        # 3️⃣ Working days only (Mon–Fri)
        if date.weekday() >= 5:
            raise forms.ValidationError(
                "Appointments can only be booked on working days (Monday to Friday)."
            )

        # 4️⃣ Working hours (9 AM – 5 PM)
        start_time = datetime.time(9, 0)
        end_time = datetime.time(17, 0)

        if time < start_time or time > end_time:
            raise forms.ValidationError(
                "Appointments are available only between 9:00 AM and 5:00 PM."
            )

        # 5️⃣ Enforce 15-minute slots
        if (time.minute % 15) != 0 or time.second != 0:
            raise forms.ValidationError(
                "Consultation slots are every 15 minutes (e.g., 10:00, 10:15, 10:30)."
            )

        # 6️⃣ Check if slot is already booked
        slot_taken = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            time=time
        ).exclude(status__in=['cancelled', 'rejected']).exists()

        if slot_taken:
            raise forms.ValidationError(
                "This time slot is already booked. Please choose another."
            )

        # 7️⃣ Prevent same patient booking multiple appointments
        if self.user:
            existing = Appointment.objects.filter(
                patient=self.user,
                doctor=doctor,
                date=date
            ).exclude(status__in=['cancelled', 'rejected']).exists()

            if existing:
                raise forms.ValidationError(
                    "You already have an appointment with this doctor on this day."
                )

        return cleaned_data