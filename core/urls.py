from django.urls import path
from . import views

app_name = 'core' # Used for namespacing URLs

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('register/', views.register_patient, name='register'),
# ]


urlpatterns = [
    path('', views.home, name='home'),             # Step 1: Landing Page
    path('login/', views.login_view, name='login'), # Step 2: Login Page
    path('register/', views.register_patient, name='register'), # Step 3: Register
    path('dashboard/', views.dashboard, name='dashboard'), # Step 4: Patient Dashboard
]