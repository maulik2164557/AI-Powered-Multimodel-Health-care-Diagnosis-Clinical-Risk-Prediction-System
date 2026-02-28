from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # The main page where the attractive chatbot lives
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    
    # The invisible API endpoint that the JavaScript talks to
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),

    path('download-pdf/', views.download_chat_pdf, name='download_chat_pdf'),

    path('radiology-lab/', views.scan_analysis_page, name='scan_analysis_page'),
    path('api/analyze-scan/', views.scan_analysis_api, name='scan_analysis_api'),

    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('api/scan-detail/<int:scan_id>/', views.view_scan_detail, name='view_scan_detail'),

    # This makes it the main home page (empty string '')
    path('', views.home_dashboard, name='home'),    # domain.com/
    # path('login/', views.login_view, name='login'),      # domain.com/login/
    path('register/', views.register_view, name='register'), # domain.com/register/


]