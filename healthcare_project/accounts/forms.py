from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegistrationForm(UserCreationForm):

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    email = forms.EmailField(required=True)
    full_name = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=True)
    phone_number = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'full_name',
            'date_of_birth',
            'gender',
            'phone_number',
            'address',
            'role',
            'specialization',
            'license_number',
            'password1',
            'password2',
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        specialization = cleaned_data.get("specialization")
        license_number = cleaned_data.get("license_number")

        # Doctor validation
        if role == "DOCTOR":
            if not specialization:
                self.add_error('specialization', "Specialization is required for doctors.")
            if not license_number:
                self.add_error('license_number', "License number is required for doctors.")

        return cleaned_data


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
