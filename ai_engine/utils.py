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
    def get_model(model_name='gemini-3-flash-preview'):
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
            model='gemini-3-flash-preview',
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
        Uses the newer Client API. Any API problems (invalid key,
        quota, etc.) are propagated as clear technical errors so the
        UI can show them, without inserting generic medical advice.
        """
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Just propagate a clean error message upwards; no generic
            # clinical content is generated here. The frontend will show
            # the actual API error (e.g. quota exceeded, key invalid).
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
        response = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt)
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