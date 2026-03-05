import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import ChatConversation, ChatMessage, MedicalScan
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import PIL.Image  
from django.core.files.storage import default_storage
from django.db.models import Count
from django.shortcuts import render
from datetime import date
from .models import ChatConversation, ChatMessage, MedicalScan, HealthMetric
from django.contrib.auth import get_user_model
from appointments.models import Appointment 
from .utils import GeminiEngine
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)



@login_required
def chatbot_page(request):
    """Renders the attractive chatbot UI."""
    return render(request, 'core/chatbot.html')




@login_required
def chatbot_api(request):

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            
            conversation, _ = ChatConversation.objects.get_or_create(
                user=request.user,
                title="Active Consultation"
            )

            # Save User Message
            ChatMessage.objects.create(conversation=conversation, role='user', content=user_message)

            # Format history for the Engine
            history = conversation.messages.all().order_by('timestamp')[:10]
            formatted_history = []
            for msg in history:
                role = "user" if msg.role == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg.content]})

            # --- Refactored Call to Utils ---
            ai_response = GeminiEngine.generate_chat_response(
                user_message=user_message, 
                history=formatted_history[:-1]
            )

            # Save AI Response
            ChatMessage.objects.create(conversation=conversation, role='bot', content=ai_response)

            return JsonResponse({"ai_response": ai_response})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def clear_chat(request):
    """Deletes the messages in the current conversation to start fresh."""
    if request.method == "POST":
        ChatMessage.objects.filter(conversation__user=request.user).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)



@login_required
def download_chat_pdf(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Clinical_Consultation.pdf"'

    # Fetch the conversation messages
    messages = ChatMessage.objects.filter(conversation__user=request.user).order_by('timestamp')

    # Build the PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title and Header
    story.append(Paragraph("SMART AI HEALTH - Clinical Consultation Report", styles['Title']))
    story.append(Paragraph(f"Patient: {request.user.username}", styles['Normal']))
    story.append(Paragraph(f"Date: {messages.first().timestamp.strftime('%Y-%m-%d %H:%M') if messages else 'N/A'}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("------------------------------------------------------------------", styles['Normal']))
    story.append(Spacer(1, 12))

    # Add messages to PDF
    for msg in messages:
        sender = "PATIENT" if msg.role == "user" else "AI ASSISTANT"
        text = f"<b>{sender}:</b> {msg.content}"
        story.append(Paragraph(text, styles['Normal']))
        story.append(Spacer(1, 8))

    # Safety Footer
    story.append(Spacer(1, 24))
    story.append(Paragraph("<i>Disclaimer: This report is AI-generated and intended for informational purposes only. Please consult a licensed medical professional.</i>", styles['Small']))

    doc.build(story)
    return response


@login_required
def scan_analysis_api(request):
    if request.method == "POST" and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            
            # Save the image record first
            scan = MedicalScan.objects.create(
                user=request.user,
                image=image_file,
                scan_type='xray' 
            )

            # --- Refactored Call to Utils ---
            # Pass the raw image file to our utility
            ai_analysis = GeminiEngine.analyze_medical_scan(image_file)
            
            # Save analysis back to the instance
            scan.ai_analysis = ai_analysis
            scan.save()

            return JsonResponse({
                "analysis": ai_analysis,
                "scan_id": scan.id
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "No image uploaded"}, status=400)


# Also add the page renderer
@login_required
def scan_analysis_page(request):
    return render(request, 'core/scan_analysis.html')


@login_required
def patient_dashboard(request):
    """
    Main Backend hub for the User Profile and Medical History.
    """
    user = request.user
    
    # 1. Fetch Conversations with message counts
    # We use prefetch_related to optimize the database hits
    conversations = ChatConversation.objects.filter(user=user).annotate(
        num_messages=Count('messages')
    ).order_by('-updated_at')

    # 2. Fetch Medical Scans
    scans = MedicalScan.objects.filter(user=user).order_by('-uploaded_at')

    # 3. Aggregate Clinical Stats
    # These will be used for the 'Quick Stats' cards in your UI
    context = {
        'user_profile': user, # Accessing full_name, role, gender etc.
        'conversations': conversations,
        'scans': scans,
        'stats': {
            'total_chats': conversations.count(),
            'total_scans': scans.count(),
            'last_scan': scans.first().uploaded_at if scans.exists() else None,
        }
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def view_scan_detail(request, scan_id):
    """
    Retrieves the specific analysis for a stored X-Ray/MRI.
    """
    try:
        scan = MedicalScan.objects.get(id=scan_id, user=request.user)
        return JsonResponse({
            "scan_type": scan.get_scan_type_display(),
            "analysis": scan.ai_analysis,
            "date": scan.uploaded_at.strftime("%Y-%m-%d"),
            "image_url": scan.image.url
        })
    except MedicalScan.DoesNotExist:
        return JsonResponse({"error": "Scan not found"}, status=404)
    

def home_dashboard(request):
    # This matches the path inside your templates folder
    return render(request, 'core/home.html')


# def login_view(request):
    # return render(request, 'core/login.html')

def register_view(request):
    return render(request, 'core/register.html')

from .utils import GeminiEngine  # Import our new utility

@login_required
def predict_clinical_risk(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        
        # Calculate age
        age = (date.today() - user.date_of_birth).days // 365 if user.date_of_birth else "Unknown"

        # Use the utility instead of writing all the Gemini code here
        patient_info = {
            'age': age,
            'gender': user.gender,
            'bp_sys': data['bp_sys'],
            'bp_dia': data['bp_dia'],
            'glucose': data['glucose'],
            'bmi': data['bmi']
        }
        
        ai_assessment = GeminiEngine.predict_clinical_risk(patient_info)

        # Save to DB
        HealthMetric.objects.create(
            user=user,
            blood_pressure_sys=data['bp_sys'],
            blood_pressure_dia=data['bp_dia'],
            glucose_level=data['glucose'],
            bmi=data['bmi'],
            heart_rate=data['heart_rate'],
            risk_score=ai_assessment 
        )
        
        return JsonResponse({"assessment": ai_assessment})
    
@login_required
def get_consultation_detail(request, conversation_id):
    """
    Backend API to retrieve all messages for a specific past session.
    """
    try:
        # Security: Ensure the conversation belongs to the logged-in user
        conversation = ChatConversation.objects.get(id=conversation_id, user=request.user)
        
        # Serialize messages
        messages = conversation.messages.all().values('role', 'content', 'timestamp')
        
        return JsonResponse({
            "title": conversation.title,
            "created_at": conversation.created_at.strftime("%Y-%m-%d"),
            "messages": list(messages)
        })
    except ChatConversation.DoesNotExist:
        return JsonResponse({"error": "Consultation not found"}, status=404)
    

@login_required
def doctor_dashboard(request):
    """
    The complete, unified backend hub for the DOCTOR role. 
    Integrates AI Practice Summaries, Patient Metrics, and Admin-approved Schedules.
    """
    # 1. Role-Based Access Control: Ensure only doctors enter
    if request.user.role != 'DOCTOR':
        return HttpResponse("Unauthorized", status=403)

    # 2. Appointment Logic: Only show 'approved' slots confirmed by the Admin
    # This respects your model fields: 'date', 'time', and 'status'
    confirmed_schedule = Appointment.objects.filter(
        doctor=request.user,
        status='approved'
    ).order_by('date', 'time')

    # 3. Patient Oversight: Fetch all patients with aggregated report/scan counts
    # This helps doctors identify high-activity patients at a glance
    patients = User.objects.filter(role='PATIENT').annotate(
        report_count=Count('conversations', distinct=True),
        scan_count=Count('medicalscan', distinct=True)
    )

    # 4. Clinical Practice AI Summary
    # We pull recent patient data to give the doctor a brief executive overview
    practice_summary = "No recent data for AI summary."
    if patients.exists():
        try:
            # Preparing text snippet for the AI Utility
            summary_context = " ".join([
                f"Patient {p.username} has {p.report_count} consultations and {p.scan_count} scans." 
                for p in patients[:5]
            ])
            practice_summary = GeminiEngine.generate_patient_summary(summary_context)
        except Exception:
            practice_summary = "AI Summary is currently unavailable."

    # 5. Consolidate Context for the Template
    context = {
        'doctor': request.user,
        'schedule': confirmed_schedule,
        'patients': patients,
        'practice_summary': practice_summary,
        'stats': {
            'total_patients': patients.count(),
            'today_count': confirmed_schedule.filter(date=date.today()).count(),
            'total_confirmed': confirmed_schedule.count(),
        }
    }

    return render(request, 'core/doctor_dashboard.html', context)

@login_required
def doctor_view_patient(request, patient_id):
    """
    Detailed clinical view for Doctors to review a specific patient's history.
    Includes: AI history summary, radiology scans, and vital sign trends.
    """
    # 1. Access Control: Restrict to Doctors only
    if request.user.role != 'DOCTOR':
        return HttpResponse("Unauthorized", status=403)

    # 2. Fetch Patient Data from accounts.User
    try:
        patient = User.objects.get(id=patient_id, role='PATIENT')
    except User.DoesNotExist:
        return HttpResponse("Patient not found", status=404)

    # 3. Retrieve all associated clinical records
    conversations = ChatConversation.objects.filter(user=patient).order_by('-updated_at')
    scans = MedicalScan.objects.filter(user=patient).order_by('-uploaded_at')
    metrics = HealthMetric.objects.filter(user=patient).order_by('-timestamp')
    
    # 4. Generate AI Executive Summary
    # We collect snippets from recent messages and scans to feed the utility
    recent_chat_data = " ".join([msg.content[:100] for conv in conversations[:3] for msg in conv.messages.all()[:3]])
    recent_scan_data = " ".join([scan.ai_analysis[:100] for scan in scans[:2]])
    
    combined_history = f"CHATS: {recent_chat_data} | SCANS: {recent_scan_data}"
    
    patient_ai_summary = "Insufficient data for summary."
    if conversations.exists() or scans.exists():
        try:
            # Using our pre-built utility
            patient_ai_summary = GeminiEngine.generate_patient_summary(combined_history)
        except Exception:
            patient_ai_summary = "AI Summary generation failed."

    # 5. Build Context for the Template
    context = {
        'patient': patient,
        'ai_summary': patient_ai_summary,
        'conversations': conversations,
        'scans': scans,
        'health_metrics': metrics,
        'patient_age': (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else "N/A",
    }

    return render(request, 'core/doctor_patient_detail.html', context)



@login_required
def book_appointment_api(request):
    """
    Backend API for patients to request a new clinical session.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Fetch the doctor user object
            doctor = User.objects.get(id=data['doctor_id'], role='DOCTOR')
            
            # Create the appointment record
            appointment = Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                date=data['date'],
                time=data['time'],
                message=data.get('message', ''),
                status='pending' # Default status from your model
            )
            
            return JsonResponse({"status": "success", "appointment_id": appointment.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
def update_appointment_status(request, appt_id):
    """
    Allows doctors to approve or reject pending appointments.
    """
    if request.user.role != 'DOCTOR':
        return JsonResponse({"error": "Unauthorized"}, status=403)
        
    if request.method == "POST":
        data = json.loads(request.body)
        new_status = data.get('status') # e.g., 'approved', 'rejected'
        
        appointment = Appointment.objects.get(id=appt_id, doctor=request.user)
        appointment.status = new_status
        appointment.save()
        
        return JsonResponse({"status": "updated", "new_status": appointment.status})
    

@login_required
def book_appointment(request):
    """
    Entry point for patients to request an appointment.
    Stored as 'pending' for Admin review.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            doctor_id = data.get('doctor_id')
            
            # Validation: Get Doctor
            doctor = User.objects.get(id=doctor_id, role='DOCTOR')

            # Create the 'Pending' request for the Admin to see
            appointment = Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                date=data.get('date'),
                time=data.get('time'),
                message=data.get('message', ''),
                status='pending'  # Stays pending until Admin acts
            )

            # AI Triage: Pre-analyze the reason for the Admin/Doctor
            # Using your existing GeminiEngine utility
            triage_prompt = (
                f"Analyze this patient's reason for visiting: '{appointment.message}'. "
                "Classify the urgency and provide a 1-sentence summary for the clinical staff."
            )
            appointment.description = GeminiEngine.generate_chat_response(triage_prompt)
            appointment.save()

            return JsonResponse({
                "status": "success", 
                "message": "Your request has been sent to the Admin for slot verification."
            })

        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Doctor not found."}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # GET: Provide the list of doctors for the booking form
    doctors = User.objects.filter(role='DOCTOR')
    return render(request, 'core/book_appointment.html', {'doctors': doctors})



@staff_member_required
def admin_appointment_manager(request):
    """
    Centralized Admin view to manage appointments for all doctors.
    """
    # 1. Fetch all pending appointments
    pending_appointments = Appointment.objects.filter(status='pending').order_by('date', 'time')
    
    # 2. Fetch all doctors to filter their specific schedules
    doctors = User.objects.filter(role='DOCTOR')

    return render(request, 'admin_panel/appointment_approval.html', {
        'pending_requests': pending_appointments,
        'doctors': doctors
    })

@staff_member_required
def approve_appointment_api(request, appt_id):
    """
    API for Admin to approve an appointment after verifying the slot.
    """
    if request.method == "POST":
        try:
            appointment = Appointment.objects.get(id=appt_id)
            
            # Backend Validation: Check if the doctor already has an approved appt at this time
            conflict = Appointment.objects.filter(
                doctor=appointment.doctor,
                date=appointment.date,
                time=appointment.time,
                status='approved'
            ).exists()

            if conflict:
                return JsonResponse({
                    "status": "error", 
                    "message": "This slot is already filled for this doctor."
                }, status=400)

            appointment.status = 'approved'
            appointment.save()
            return JsonResponse({"status": "success", "message": "Appointment Approved."})
            
        except Appointment.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Not found."}, status=404)
        

@staff_member_required
def admin_approval_dashboard(request):
    """
    Centralized dashboard for Admin to manage pending appointment requests.
    """
    # 1. Fetch all pending requests for all doctors
    pending_requests = Appointment.objects.filter(status='pending').order_by('date', 'time')
    
    # 2. Fetch all doctors to help filter the view if needed
    doctors = User.objects.filter(role='DOCTOR')

    return render(request, 'admin_panel/appointment_approval.html', {
        'pending_requests': pending_requests,
        'doctors': doctors,
        'total_pending': pending_requests.count()
    })

@staff_member_required
def approve_appointment(request, appt_id):
    """
    API endpoint for Admin to confirm an appointment after slot verification.
    """
    if request.method == "POST":
        try:
            appointment = Appointment.objects.get(id=appt_id)
            
            # 1. CHECK FOR SLOT CONFLICTS (The core Admin responsibility)
            # Check if this doctor already has an 'approved' slot at this date and time
            is_taken = Appointment.objects.filter(
                doctor=appointment.doctor,
                date=appointment.date,
                time=appointment.time,
                status='approved'
            ).exists()

            if is_taken:
                return JsonResponse({
                    "status": "error", 
                    "message": "Conflict: This slot is already booked for this doctor."
                }, status=400)

            # 2. If no conflict, approve the request
            appointment.status = 'approved'
            appointment.save()
            
            return JsonResponse({"status": "success", "message": "Appointment confirmed."})

        except Appointment.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Record not found."}, status=404)
            
    return JsonResponse({"status": "error", "message": "Invalid method."}, status=405)