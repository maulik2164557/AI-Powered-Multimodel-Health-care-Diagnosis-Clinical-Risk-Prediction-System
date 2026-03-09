from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from .utils import GeminiEngine
import json
import logging
from django.utils import timezone
from django.views.decorators.http import require_POST
from medical_history.models import MedicalLog, MedicalDocument
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.files.base import ContentFile
import google.genai as genai


logger = logging.getLogger(__name__)

def ai_chat_placeholder(request):
    return JsonResponse({"message": "AI Engine is active."})

@login_required
def get_health_advice(request):
    # Backwards-compatible alias that delegates to the unified helper.
    advice = GeminiEngine.generate_health_plan(request.user)
    return render(request, 'ai_engine/advice_report.html', {'advice': advice})


@login_required
def health_advice_view(request):
    # Call the function from utils.py
    ai_response = GeminiEngine.generate_health_plan(request.user)

    return render(request, 'ai_engine/advice_report.html', {
        'advice': ai_response
    })


@login_required
def medical_chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        scan_file = request.FILES.get('scan')

        # Build a structured clinical prompt that instructs the model
        # to return illness explanation, prescription, lifestyle advice,
        # and triage guidance (including which specialist to see).
        base_prompt = f"""
You are an AI clinical assistant helping a patient.

Patient description of symptoms:
{user_message}

If a medical report or scan image is available, incorporate its findings into your answer.

Provide a clear, structured response using these sections:

1. Illness Summary
2. Probable Diagnosis and Severity
3. Prescription Plan
   - List medicines with: name, dose, route, frequency, duration (number of days).
   - For each medicine, specify timing schedule like:
     - Morning: after breakfast ...
     - Noon: before lunch ...
     - Night: after dinner ...
4. Dietary and Food Care Advice
5. Recommended Exercises and Lifestyle Guidance
6. When to See a Doctor
   - If illness appears serious, clearly state that the patient should visit a doctor
     and recommend the most appropriate specialist (e.g., neurologist, cardiologist,
     gastroenterologist) and the urgency (e.g., "as soon as possible", "within 24 hours").
7. Safety Disclaimer
   - Clearly mention that this is AI-generated guidance and not a substitute for an in-person doctor visit.

Use headings and bullet points so the output is easy to copy into a report.
"""
        try:
            # If a scan/report is uploaded, use the multimodal helper,
            # otherwise fall back to text-only generation.
            if scan_file:
                ai_response = GeminiEngine.analyze_medical_scan(
                    image_file=scan_file,
                    prompt=base_prompt
                )
            else:
                ai_response = GeminiEngine.get_response(base_prompt)
            return JsonResponse({'status': 'success', 'response': ai_response})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return render(request, 'ai_engine/chatbot.html')

    
@login_required
def download_prescription(request):
    analysis_text = request.GET.get('text', 'No data')
    
    # --- PDF GENERATION ---
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "AI CLINICAL PRESCRIPTION")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    p.line(100, 720, 500, 720)

    text_object = p.beginText(100, 700)
    text_object.setFont("Helvetica", 10)
    # Simple wrap for lines
    for line in analysis_text.split('\n'):
        text_object.textLine(line)
    p.drawText(text_object)

    p.showPage()
    p.save()

    # Move back to the beginning of the buffer so we can both save
    # a copy in the database and return it to the browser.
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    # --- REQUIREMENT: COMPULSORY SAVE ---
    # Save this AI-generated prescription into the patient's medical history
    # with the requested prefix and current date/time.
    title = f"AI generated Prescription - {timezone.now().strftime('%Y-%m-%d %H:%M')}"

    # 1) Save a text log entry
    MedicalLog.objects.create(
        patient=request.user,
        title=title,
        description=analysis_text,
    )

    # 2) Save the PDF itself as a medical document for later download
    filename = f"ai_prescription_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    MedicalDocument.objects.create(
        patient=request.user,
        title=title,
        file=ContentFile(pdf_bytes, name=filename),
    )

    # Finally, return the PDF to the user for immediate download.
    return FileResponse(io.BytesIO(pdf_bytes), as_attachment=True, filename="AI_Prescription.pdf")
# def download_prescription(request):
#     """Generates a PDF and automatically logs the entry into Medical History."""
#     analysis_text = request.GET.get('text', 'No clinical data available.')
#     user = request.user

#     # 2. Auto-Save to Medical History
#     # We save this as a record with the specific prefix you requested

#     MedicalScan.objects.create(
#         user=request.user,
#         analysis=f"AI generate prescription: {analysis_text}", # Your requested prefix
#         uploaded_at=timezone.now()
#     )
    
#     # 1. Create PDF
#     buffer = io.BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)
#     p.setFont("Helvetica-Bold", 16)
#     p.drawString(100, 750, "AI GENERATED CLINICAL PRESCRIPTION")
    
#     p.setFont("Helvetica", 10)
#     p.drawString(100, 730, f"Patient: {user.username}")
#     p.drawString(100, 715, f"Date/Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     p.line(100, 705, 500, 705)
    
#     # Text wrapping for AI response
#     p.setFont("Helvetica", 11)
#     text_object = p.beginText(100, 680)
#     lines = analysis_text.split('\n')
#     for line in lines:
#         text_object.textLine(line)
#     p.drawText(text_object)
    
#     p.showPage()
#     p.save()
#     buffer.seek(0)


#     return FileResponse(buffer, as_attachment=True, filename=f"AI_Prescription_{user.username}.pdf")

@login_required
@require_POST
def save_scan_analysis(request):
    analysis_text = request.POST.get('analysis')
    
    if analysis_text:
        # Store a generic AI analysis entry in the patient's medical history.
        new_record = MedicalLog.objects.create(
            patient=request.user,
            title=f"AI Chat Analysis - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            description=analysis_text,
        )

        return JsonResponse({
            'status': 'success', 
            'message': f'Saved to history on {new_record.created_at.strftime("%Y-%m-%d %H:%M")}'
        })
    
    return JsonResponse({'status': 'error', 'message': 'No data to save.'})