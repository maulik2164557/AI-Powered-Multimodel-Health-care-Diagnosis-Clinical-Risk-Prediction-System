import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class StandardMedicalAI:
    def __init__(self):
        # Configure Gemini with your API Key
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Initialize the model
        # We use gemini-1.5-flash for fast, clinical responses
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_diagnosis_summary(self, user_input):
        """
        Sends symptoms to Gemini and receives a structured medical response.
        """
        try:
            # Setting the context for a Medical Professional AI
            prompt = (
                f"You are a Clinical Diagnostic Assistant. A patient reports: '{user_input}'. "
                "Provide a response with the following sections:\n"
                "1. ANALYSIS: Brief overview of the symptoms.\n"
                "2. POTENTIAL CONDITIONS: List possible medical issues.\n"
                "3. RISK LEVEL: (Low, Medium, or High).\n"
                "4. SUGGESTED STEPS: Medicines (OTC only) or lifestyle advice.\n"
                "5. DISCLAIMER: State that this is not a final medical diagnosis."
            )

            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

# Initialize the engine
ai_bridge = StandardMedicalAI()