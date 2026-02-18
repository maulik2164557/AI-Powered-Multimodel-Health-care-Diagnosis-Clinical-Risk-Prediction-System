from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Defining roles for your team and users
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'System Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    email = models.EmailField(unique=True) # Ensure email is unique for medical security

    def __str__(self):
        return f"{self.username} ({self.role})"

class PatientProfile(models.Model):
    # Link to the Custom User defined above
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    blood_group = models.CharField(max_length=5, blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

class DiagnosisRecord(models.Model):
    # The heart of your AI system
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='diagnoses')
    symptoms_input = models.TextField()
    uploaded_scan = models.ImageField(upload_to='medical_scans/', null=True, blank=True)
    
    # AI Logic Fields
    result_diagnosis = models.CharField(max_length=255)
    confidence_score = models.FloatField(default=0.0)
    ai_prescription = models.TextField(blank=True) # To be filled by your Chatbot
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis - {self.patient.user.username} - {self.timestamp.date()}"