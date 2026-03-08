from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('chat/', views.medical_chatbot, name='medical_chatbot'), # The main Chatbot UI
    path('chat-test/', views.ai_chat_placeholder, name='chat_test'),
    path('get-advice/', views.health_advice_view, name='get_health_advice'),
    path('save-analysis/', views.save_scan_analysis, name='save_scan_analysis'),
    path('download-prescription/', views.download_prescription, name='download_prescription'),
]