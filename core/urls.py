from django.urls import path
from . import views

app_name = 'core' # Used for namespacing URLs

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('register/', views.register_patient, name='register'),
# ]


urlpatterns = [
    path('', views.home, name='home'),             
    path('login/', views.login_view, name='login'), 
    path('register/', views.register_patient, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'), 
]