
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import PatientProfile, DiagnosisRecord
from django.http import JsonResponse
from ai_engine.main import ai_bridge
import json


def home(request):
    """Entry point for the website"""
    return render(request, 'core/home.html')

def login_view(request):
    """Authentication view for R.2.1"""
    return render(request, 'core/login.html')

def dashboard(request):
    """
    Main dashboard view. Shows recent diagnoses if the user is a patient.
    """
    context = {}
    if request.user.is_authenticated:
        # If user is a patient, get their records
        if hasattr(request.user, 'patient_profile'):
            context['records'] = DiagnosisRecord.objects.filter(
                patient=request.user.patient_profile
            ).order_by('-timestamp')
    
    return render(request, 'core/dashboard.html', context)

def register_patient(request):
    """
    Placeholder for Patient Registration logic.
    We will expand this when we build the HTML forms.
    """
    return render(request, 'core/register.html')


def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            
            # Call the Gemini Engine
            ai_summary = ai_bridge.get_diagnosis_summary(user_message)
            
            return JsonResponse({
                "status": "success",
                "ai_response": ai_summary
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "POST request required"}, status=400)