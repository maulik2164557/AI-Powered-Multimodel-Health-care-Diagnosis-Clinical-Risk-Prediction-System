# This file will house a unified GeminiEngine class to handle text consultations, image analysis, and clinical risk predictions.


from medical_history.models import ChatConversation, ChatMessage, MedicalScan, HealthMetric
import google.genai as genai
from django.conf import settings
import PIL.Image


class GeminiEngine:
    """
    A unified utility class to handle all AI operations across the project.
    """
    
    @staticmethod
    def get_model(model_name='gemini-1.5-flash'):
        """
        Returns a configured Gemini model instance (for older-style usage).
        """
        return genai.GenerativeModel(model_name)

    @staticmethod
    def get_client():
        """
        Factory for the newer google.genai Client.
        """
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    @classmethod
    def generate_chat_response(cls, user_message, history=None):
        """
        Simple text-only chat response using the unified Client.
        """
        client = cls.get_client()
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=user_message
        )
        return response.text

    @classmethod
    def analyze_medical_scan(cls, image_file, prompt=None):
        """Handles multimodal image analysis."""
        if not prompt:
            prompt = (
                "Identify the scan type, describe findings (fractures/abnormalities), "
                "and provide a Clinical Impression. Include a medical disclaimer."
            )
        
        img = PIL.Image.open(image_file)
        model = cls.get_model()
        response = model.generate_content([prompt, img])
        return response.text

    @classmethod
    def predict_clinical_risk(cls, patient_data):
        """Handles structured data analysis for risk prediction."""
        model = cls.get_model()
        prompt = (
            f"Evaluate vitals for an {patient_data['age']}-year-old {patient_data['gender']}: "
            f"BP: {patient_data['bp_sys']}/{patient_data['bp_dia']}, "
            f"Glucose: {patient_data['glucose']}, BMI: {patient_data['bmi']}. "
            "Predict risk for Cardiovascular Disease and Diabetes. Format as a clinical report."
        )
        response = model.generate_content(prompt)
        return response.text
    
    @classmethod
    def generate_patient_summary(cls, history_data):
        """
        Synthesizes multiple consultations and scans into a 
        brief executive summary for a doctor.
        """
        model = cls.get_model()
        prompt = (
            f"Summarize the following clinical history for a physician: {history_data}. "
            "Highlight recurring symptoms, critical scan findings, and risk trends. "
            "Keep it under 150 words and use professional clinical terminology."
        )
        response = model.generate_content(prompt)
        return response.text
    
    @staticmethod
    def get_response(prompt):
        """
        Primary helper for generating a clinical response.
        Uses the newer Client API and wraps common quota/rate-limit
        errors with a user-friendly message.
        """
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_text = str(e)
            # Clear explanation for expired/invalid API key
            if "API key expired" in error_text or "API_KEY_INVALID" in error_text:
                raise Exception(
                    "The configured Gemini API key is invalid or expired. "
                    "Please update the API key in the server settings."
                )
            # If the hosted Gemini API is out of quota, fall back to a
            # safe, generic clinical message instead of failing the chat.
            if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
                fallback = (
                    "Our main AI service is temporarily unavailable because its "
                    "usage limit has been reached (error 429: RESOURCE_EXHAUSTED).\n\n"
                    "However, based on your description, here is general guidance:\n"
                    "1. Monitor your symptoms closely, especially fever, severe pain, "
                    "   breathing difficulty, chest pain, confusion, or loss of consciousness.\n"
                    "2. If any emergency symptom is present, go to the nearest hospital or "
                    "   call emergency services immediately.\n"
                    "3. For non‑emergency but worrying symptoms, book an appointment with an "
                    "   appropriate specialist doctor as soon as possible.\n"
                    "4. Stay hydrated, avoid self‑medicating with strong drugs without a "
                    "   doctor’s supervision, and keep a record of your temperature, pain level, "
                    "   and any medicines you take.\n\n"
                    "Disclaimer: This is a generic, non‑personalized message shown because the "
                    "AI model could not be contacted. It is NOT a medical diagnosis. "
                    "Always consult a qualified doctor for final advice."
                )
                return fallback
            # For any other error, surface the original message to the caller.
            raise

    # def get_response(prompt, image=None, history=None):
    #     genai.configure(api_key=settings.GEMINI_API_KEY)
    #     model = genai.GenerativeModel('gemini-1.5-flash')

    #     content_parts = [prompt]
    #     print(f"DEBUG: Sending to Gemini API: {content_parts}")
        
    #     if image:
    #         # Handle media (Medical Scans)
    #         img = PIL.Image.open(image)
    #         response = model.generate_content([prompt, img])
    #     elif history:
    #         # Handle Chatbot sessions with memory
    #         chat = model.start_chat(history=history)
    #         response = chat.send_message(prompt)
    #     else:
    #         # General text analysis (Risk Prediction/History)
    #         response = model.generate_content(prompt)
        # return response.text
            
    
    @staticmethod
    def get_advice(symptoms_or_illness):
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = (
            f"Regarding {symptoms_or_illness}, provide: "
            "1. Necessary medicines and duration. "
            "2. Dietary/Food care. "
            "3. Recommended exercises. "
            "Include a disclaimer that this is AI-generated advice."
        )
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        return response.text
    
    @staticmethod
    def generate_health_plan(user):
        # Fetch the latest metrics for this user
        metrics = HealthMetric.objects.filter(user=user).last()
    
        if not metrics:
            return "No health metrics found. Please enter your data first."

        # Create a detailed prompt
        prompt = f"""
        As a medical AI assistant, analyze these patient metrics:
        - Blood Pressure: {metrics.blood_pressure_sys}/{metrics.blood_pressure_dia}
        - Glucose Level: {metrics.glucose_level} mg/dL
        - BMI: {metrics.bmi}
        - Heart Rate: {metrics.heart_rate} bpm

        Provide a professional health plan divided into:
        1. NECESSARY MEDICINES: (General suggestions based on these levels)
        2. FOOD CARE: (Specific dietary recommendations)
        3. EXERCISE: (Safe activity levels based on heart rate and BMI)
    
        Disclaimer: Add a note that this is AI-generated and not a substitute for a doctor's visit.
        """

        # Reuse the main helper so the same model and error handling are applied.
        return GeminiEngine.get_response(prompt)