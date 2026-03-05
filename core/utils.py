# This file will house a unified GeminiEngine class to handle text consultations, image analysis, and clinical risk predictions.


import google.generativeai as genai
from django.conf import settings
import PIL.Image

# Configure the SDK once at the module level
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiEngine:
    """
    A unified utility class to handle all AI operations across the project.
    """
    
    @staticmethod
    def get_model(model_name='gemini-1.5-flash'):
        """Returns a configured Gemini model instance."""
        return genai.GenerativeModel(model_name)

    @classmethod
    def generate_chat_response(cls, user_message, history=None):
        """Handles conversational logic with memory."""
        model = cls.get_model()
        # Start chat with provided history or empty list
        chat = model.start_chat(history=history or [])
        response = chat.send_message(user_message)
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