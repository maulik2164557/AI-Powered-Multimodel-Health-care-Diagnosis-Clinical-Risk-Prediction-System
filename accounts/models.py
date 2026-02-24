from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):

    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='PATIENT'
    )

    is_approved = models.BooleanField(default=False)

    # Personal Information (optional at model level — required in form)
    full_name = models.CharField(max_length=150, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    # Phone validator
    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )

    phone_number = models.CharField(
        max_length=10,
        validators=[phone_validator],
        blank=True
    )

    address = models.TextField(blank=True)

    # Doctor-specific fields (optional at model level)
    specialization = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = "ADMIN"
            self.is_approved = True
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.username} ({self.role})"
