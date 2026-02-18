from django.urls import path
from . import views

app_name = 'core' # Used for namespacing URLs

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_patient, name='register'),
]