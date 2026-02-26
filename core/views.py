import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import ChatConversation, ChatMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import PIL.Image  
from django.core.files.storage import default_storage


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

@login_required
def chatbot_page(request):
    """Renders the attractive chatbot UI."""
    return render(request, 'core/chatbot.html')

@login_required
def chatbot_api(request):
    """Handles the logic of sending messages and maintaining memory."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            
            # 1. Get or Create a conversation for the user
            # For now, we use a single active conversation per user
            conversation, created = ChatConversation.objects.get_or_create(
                user=request.user,
                title="Active Consultation"
            )

            # 2. Save User Message to Database (Pillar 1)
            ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_message
            )

            # 3. Build Memory Context (Pillar 3)
            # Fetch last 10 messages to keep the AI focused
            history = conversation.messages.all().order_by('timestamp')[:10]
            formatted_history = []
            for msg in history:
                role = "user" if msg.role == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg.content]})

            # 4. Call Gemini Engine
            model = genai.GenerativeModel('gemini-1.5-flash')
            chat = model.start_chat(history=formatted_history[:-1]) # History minus current msg
            response = chat.send_message(user_message)
            ai_response = response.text

            # 5. Save AI Response to Database (Pillar 1)
            ChatMessage.objects.create(
                conversation=conversation,
                role='bot',
                content=ai_response
            )

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
            
            # 1. Save the image to the database (Pillar 1)
            scan = MedicalScan.objects.create(
                user=request.user,
                image=image_file,
                scan_type='xray'  # You can make this dynamic later
            )

            # 2. Open image for Gemini
            img = PIL.Image.open(image_file)

            # 3. Configure Multimodal Prompt
            # We use 1.5-flash because it is incredibly fast at image reasoning
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = (
                "You are an expert Radiologist AI. Analyze this medical image. "
                "1. Identify the type of scan (X-ray, MRI, CT). "
                "2. Describe the findings (look for fractures, inflammation, or abnormalities). "
                "3. Provide a 'Clinical Impression' section. "
                "IMPORTANT: Always state that this is an AI assistant and a human doctor must confirm."
            )

            # 4. Generate Analysis
            response = model.generate_content([prompt, img])
            scan.ai_analysis = response.text
            scan.save()

            return JsonResponse({
                "analysis": response.text,
                "scan_id": scan.id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "No image uploaded"}, status=400)

# Also add the page renderer
@login_required
def scan_analysis_page(request):
    return render(request, 'core/scan_analysis.html')