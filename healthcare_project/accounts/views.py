from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import RegistrationForm, LoginForm


# =====================================
# PUBLIC HOMEPAGE
# =====================================
def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    return render(request, 'accounts/home.html')


# =====================================
# REGISTRATION
# =====================================
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Patient auto-approved
            if user.role == 'PATIENT':
                user.is_approved = True
            else:
                user.is_approved = False

            user.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# =====================================
# LOGIN
# =====================================
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.role in ['DOCTOR', 'ADMIN'] and not user.is_approved:
                    messages.error(request, "Your account is awaiting admin approval.")
                    return redirect('accounts:login')

                login(request, user)
                return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# =====================================
# LOGOUT
# =====================================
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:home')


# =====================================
# DASHBOARD REDIRECTION
# =====================================
@login_required
def dashboard_redirect(request):
    if request.user.role == 'PATIENT':
        return redirect('accounts:patient_dashboard')
    elif request.user.role == 'DOCTOR':
        return redirect('accounts:doctor_dashboard')
    elif request.user.role == 'ADMIN':
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:home')


# =====================================
# DASHBOARDS
# =====================================
@login_required
def patient_dashboard(request):
    if request.user.role != 'PATIENT':
        return redirect('accounts:home')
    return render(request, 'accounts/dashboard_patient.html')


@login_required
def doctor_dashboard(request):
    if request.user.role != 'DOCTOR':
        return redirect('accounts:home')
    return render(request, 'accounts/dashboard_doctor.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('accounts:home')
    return render(request, 'accounts/dashboard_admin.html')
