from django.contrib import admin
from .models import MedicalLog, MedicalDocument


@admin.register(MedicalLog)
class MedicalLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'patient__username')
    ordering = ('-created_at',)


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'title', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title', 'patient__username')
    ordering = ('-uploaded_at',)
