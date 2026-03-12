from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib import messages
from .forms import AppointmentForm
from .models import Appointment
import datetime


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

    if request.user.role != "PATIENT":
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user

            # System-managed approval
            appointment.status = 'approved'

            appointment.save()

            messages.success(
                request,
                "Appointment booked successfully. Your slot is confirmed."
            )

            return redirect('appointments:appointments_home')

    else:
        form = AppointmentForm(user=request.user)

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

    # Only the assigned doctor can update
    if request.user != appointment.doctor:
        return redirect('accounts:dashboard_redirect')

    # Only approved appointments can be changed
    if appointment.status != "approved":
        messages.error(request, "Only approved appointments can be updated.")
        return redirect('appointments:doctor_appointments')

    new_status = (new_status or "").lower()

    # Allow cancellation anytime
    if new_status == "cancelled":
        appointment.status = "cancelled"
        appointment.save()

        messages.success(request, "Appointment cancelled.")
        return redirect('appointments:doctor_appointments')

    # Completion only after appointment time
    if new_status == "completed":

        appointment_datetime = datetime.datetime.combine(
            appointment.date,
            appointment.time
        )

        appointment_datetime = timezone.make_aware(
            appointment_datetime,
            timezone.get_current_timezone()
        )

        if timezone.now() < appointment_datetime:
            messages.error(
                request,
                "You can only mark the appointment completed after its scheduled time."
            )
            return redirect('appointments:doctor_appointments')

        appointment.status = "completed"
        appointment.save()

        messages.success(request, "Appointment marked as completed.")

    return redirect('appointments:doctor_appointments')
