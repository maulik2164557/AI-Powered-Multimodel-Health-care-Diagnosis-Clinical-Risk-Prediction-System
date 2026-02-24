from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointments_home, name='appointments_home'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('doctor/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/update/<int:pk>/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
]