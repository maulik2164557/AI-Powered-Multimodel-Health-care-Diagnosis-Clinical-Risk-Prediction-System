from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'patient',
        'doctor',
        'date',
        'time',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'date',
        'doctor',
    )

    search_fields = (
        'patient__username',
        'patient__full_name',
        'doctor__username',
        'doctor__full_name',
    )

    ordering = ('-created_at',)

    # 👇 Explicitly define fields order
    fields = (
        'patient',
        'doctor',
        'date',
        'time',
        'message',
        'description',
        'status',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'patient',
        'doctor',
        'date',
        'time',
        'message',
        'description',
        'created_at',
        'updated_at',
    )
