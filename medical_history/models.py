from django.db import models
from django.conf import settings


class MedicalLog(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_logs'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.patient.username}"


class MedicalDocument(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_documents'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='medical_documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.patient.username}"
    

class ChatConversation(models.Model):
    """Groups multiple messages into a single session/consultation."""
    # Using settings.AUTH_USER_MODEL makes this compatible with your 'accounts' app
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, default="New Consultation")

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Consultation {self.id} - {self.user}"

class ChatMessage(models.Model):
    """Stores individual messages between the User and the AI."""
    ROLE_CHOICES = (
        ('user', 'User'),
        ('bot', 'AI Assistant'),
    )
    
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role.capitalize()}: {self.content[:50]}..."


class MedicalScan(models.Model):
    SCAN_TYPES = (
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct', 'CT Scan'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='medical_scans/%Y/%m/%d/')
    scan_type = models.CharField(max_length=10, choices=SCAN_TYPES)
    ai_analysis = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scan_type.upper()} - {self.user.username} ({self.uploaded_at.date()})"

class HealthMetric(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blood_pressure_sys = models.IntegerField(help_text="Systolic")
    blood_pressure_dia = models.IntegerField(help_text="Diastolic")
    heart_rate = models.IntegerField()
    glucose_level = models.FloatField()
    bmi = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    risk_score = models.CharField(max_length=50, blank=True) # AI Generated result

    def __str__(self):
        return f"Metrics for {self.user.username} - {self.timestamp.date()}"