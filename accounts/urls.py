from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard Routing
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Role Dashboards
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]
