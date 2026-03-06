from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import GeminiEngine 
import json
import logging
from django.utils import timezone
from django.views.decorators.http import require_POST
from medical_history.models import MedicalScan # Import from root folder

logger = logging.getLogger(__name__)

def ai_chat_placeholder(request):
    return JsonResponse({"message": "AI Engine is active."})

@login_required
def get_health_advice(request):
    advice = GeminiEngine(request.user)
    return render(request, 'ai_engine/advice_report.html', {'advice': advice})


@login_required
def health_advice_view(request):
    # Call the function from utils.py
    ai_response = GeminiEngine(request.user)
    
    return render(request, 'ai_engine/advice_report.html', {
        'advice': ai_response
    })

@login_required
def medical_chatbot(request):
    if request.method == "POST":
        user_message = request.POST.get('message')
        uploaded_file = request.FILES.get('scan')  # Capture X-Ray, MRI, or CT Scan
        
        try:
            # We call your existing get_response method
            # It handles image logic if 'image' is passed
            ai_response = GeminiEngine.get_response(
                prompt=user_message, 
                image=uploaded_file
            )
            
            return JsonResponse({
                'status': 'success', 
                'response': ai_response
            })
            
        except Exception as e:
            logger.error(f"Chatbot Error: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': "I encountered an error processing your request."
            })

    # For the initial page load
    return render(request, 'ai_engine/chatbot.html')


@login_required
@require_POST
def save_scan_analysis(request):
    analysis_text = request.POST.get('analysis')
    scan_image = request.FILES.get('scan')
    
    if analysis_text:
        # Create the record with the current timestamp
        new_record = MedicalScan.objects.create(
            user=request.user,
            analysis_result=analysis_text,
            image=scan_image,
            # 'uploaded_at' is likely the field name in your medical_history model
            uploaded_at=timezone.now() 
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Saved to history on {new_record.uploaded_at.strftime("%Y-%m-%d %H:%M")}'
        })
    
    return JsonResponse({'status': 'error', 'message': 'No data to save.'})