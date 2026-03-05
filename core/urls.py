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

    path('api/predict-risk/', views.predict_clinical_risk, name='predict_clinical_risk'),
    path('api/consultation/<int:conversation_id>/', views.get_consultation_detail, name='consultation_detail'),

    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/patient/<int:patient_id>/', views.doctor_view_patient, name='doctor_view_patient'),
    path('api/book-appointment/', views.book_appointment_api, name='book_appointment_api'),
    path('api/update-appointment/<int:appt_id>/', views.update_appointment_status, name='update_appt'),
    path('admin-panel/approvals/', views.admin_approval_dashboard, name='admin_approvals'),
]