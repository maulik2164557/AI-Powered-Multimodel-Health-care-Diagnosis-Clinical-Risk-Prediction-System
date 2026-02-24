from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib import messages
from .forms import AppointmentForm
from .models import Appointment


# Patient
@login_required
def appointments_home(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-created_at')

    return render(request, 'appointments/appointments_home.html', {
        'appointments': appointments
    })

@login_required
def book_appointment(request):

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'pending'
            appointment.save()
            return redirect('appointments:appointments_home')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {
        'form': form
    })


# Doctor
@login_required
def doctor_appointments(request):

    # Ensure only doctors access
    if request.user.role != "DOCTOR":
        return redirect('accounts:dashboard_redirect')

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).order_by('date', 'time')

    return render(request, 'appointments/doctor_appointments.html', {
        'appointments': appointments
    })

@login_required
def update_appointment_status(request, pk, new_status):

    appointment = get_object_or_404(Appointment, pk=pk)

    # Only doctor assigned can update
    if request.user != appointment.doctor:
        return redirect('accounts:dashboard_redirect')

    # Only allow change if already approved
    if appointment.status != "APPROVED":
        messages.error(request, "Only approved appointments can be updated.")
        return redirect('appointments:doctor_appointments')

    # Check if appointment time has passed
    appointment_datetime = timezone.datetime.combine(
        appointment.date,
        appointment.time
    )

    appointment_datetime = timezone.make_aware(
        appointment_datetime,
        timezone.get_current_timezone()
    )

    if timezone.now() < appointment_datetime:
        messages.error(request, "You can only update after appointment time.")
        return redirect('appointments:doctor_appointments')

    if new_status in ["COMPLETED", "CANCELLED"]:
        appointment.status = new_status
        appointment.save()

    return redirect('appointments:doctor_appointments')
